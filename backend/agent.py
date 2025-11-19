from kafka import KafkaConsumer
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent
from langchain_core.tools import tool
from supabase.client import create_client, Client
import json
import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in environment or .env file.")

# ---- Supabase Vector Store Setup ----
SUPABASE_URL = os.getenv("SUPABASE_API")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_API_KEY")
# ---- MongoDB Atlas Setup ----
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://khanak:root@cluster0.1gau7dh.mongodb.net/?appName=Cluster0")

if not all([SUPABASE_URL, SUPABASE_KEY, api_key]):
    raise ValueError("Missing environment variables. Please set SUPABASE_API, SUPABASE_SERVICE_API_KEY, GEMINI_API_KEY.")

# Mongo Setup
client = MongoClient(MONGO_URI)
#  Supabase + Embeddings Setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

try:
    vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
    )
except Exception as e:
    print(f"Error while defining vector store: {e}")

db = client["test"]
reports_collection = db["ipfix"]

# ---- Gemini Model ----
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=api_key
)

# ---- External Threat-Intel Tools (VirusTotal, AbuseIPDB, WHOIS/RDAP) ----
def virustotal_lookup_ip(ip: str):
    """Lookup an IP address on VirusTotal (v3 API). Returns JSON or error string."""
    key = os.getenv("VIRUSTOTAL_API_KEY")
    if not key:
        return "VIRUSTOTAL_API_KEY not set in environment"
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        return f"VirusTotal request failed: {e}"
    if resp.status_code == 200:
        return resp.json()
    return f"VirusTotal error {resp.status_code}: {resp.text}"


def abuseipdb_lookup_ip(ip: str, max_age_in_days: int = 90):
    """Lookup an IP address on AbuseIPDB. Returns JSON or error string."""
    key = os.getenv("ABUSEIPDB_API_KEY")
    if not key:
        return "ABUSEIPDB_API_KEY not set in environment"
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {"ipAddress": ip, "maxAgeInDays": max_age_in_days}
    headers = {"Key": key, "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
    except Exception as e:
        return f"AbuseIPDB request failed: {e}"
    if resp.status_code == 200:
        return resp.json()
    return f"AbuseIPDB error {resp.status_code}: {resp.text}"


def whois_lookup(ip: str):
    """Perform Whois lookup for an IP"""

    url = f"http://ipwho.is/{ip}"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        return f"Whois request failed: {e}"
    if resp.status_code == 200:
        return resp.json()
    return f"Whois error {resp.status_code}: {resp.text}"

#-----Elastic Search MCP Tool -----
def get_neighboring_packets(timestamp: str) -> str:
    """
    Query the local MCP Elasticsearch server to get packets within ±2 minutes of a given timestamp.
    """
    url = "http://host.docker.internal:4560/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": os.getenv("MCP_PROXY_AUTH_TOKEN", ""),  # optional
    }

    # Convert timestamp string → datetime
    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    gte = (ts - timedelta(minutes=2)).isoformat()
    lte = (ts + timedelta(minutes=2)).isoformat()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {
                "index": "ipfix-*",
                "query_body": {
                    "query": {
                        "range": {
                            "iana:flowStartMilliseconds": {
                                "gte": gte,
                                "lte": lte
                            }
                        }
                    },
                    "size": 10
                }
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text}"
        return response.text
    except Exception as e:
        return f"Error querying MCP: {e}"

@tool
def retrieve(query: str) -> str:
    """
    Retrieve cybersecurity context from the Supabase vector database.
    Searches for related incidents, mitigation steps, and attack strategies.
    """

    # prevent huge queries from killing Supabase
    if len(query) > 500:
        query = query[:500]

    try:
        retrieved_docs = vector_store.similarity_search(query, k=6)
    except Exception as e:
        return f"[RAG] Vector search failed: {e}"

    if not retrieved_docs:
        return "[RAG] No related cybersecurity documents found."

    # Convert docs to pure text only
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )

    return serialized


# ------ Kafka msgs processing agent ---------
agent = create_agent(
    model=llm,
    tools=[virustotal_lookup_ip, abuseipdb_lookup_ip, whois_lookup, get_neighboring_packets,retrieve],
    system_prompt=(
       "You are a skilled Cyber Threat Intelligence (CTI) Analyst specializing in NetFlow analysis."
        "Your task is to analyze a given network packet and produce a clear, detailed, structured Markdown report."
        "You have access to several analysis tools — use them only when needed to support your reasoning:"
        "- analyze_netflow(packet): Analyze network flow and detect anomalies or malicious signatures."
        "- virustotal_lookup_ip(ip): Check IP reputation and detections on VirusTotal."
        "- abuseipdb_lookup_ip(ip): Retrieve abuse confidence scores or recent reports for the IP."
        "- whois_lookup(query): Fetch ownership, ASN, and geolocation information."
        "- get_neighboring_packets(timestamp): Retrieve nearby packets for correlation or context."
        "- retrieve(query): Retrieve information about various kinds of attacks, how to identify and mitigate them."
        "When writing the report:"
        "1. Use Markdown formatting with clear headings and bullet points."
        "2. Include the following sections:"
        "### Summary"
        "- 2-3 sentences summarizing the packet analysis and possible attack."
        "### Key Indicators"
        "- Source IP, Destination IP, Ports, Protocol, and Timestamp."
        "### Threat Assessment"
        "- Explain if the activity indicates malicious, suspicious, or normal behavior; and if malicious, what can it possibly be."
        "- Mention any correlation with known campaigns or IoCs if applicable."
        "### Supporting Evidence"
        "- Summarize findings from each of VirusTotal, AbuseIPDB, WHOIS(like location of source and destination ip), neighboring packet analysis, and retrieval from vector score."
        "- Include key data points (e.g., detection ratio, abuse score, results of security engines, country, ASN, what do source and destination ports represent etc.)."
        "### Recommendation"
        "- Suggest Mitigation steps for the attack. Can take help from retrieved documents."
        "Use clear and readable Markdown — no JSON or code formatting. "
        "Ensure each report can stand alone as a professional analyst summary."
    )
)


# Extract plain text from threat_report if possible
def extract_text(report):
    # If it's a list of messages, get the last AIMessage or ToolMessage content
    if isinstance(report, dict) and "messages" in report and isinstance(report["messages"], list):
        for msg in reversed(report["messages"]):
            if hasattr(msg, "content"):
                content= msg.content
                if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                    print("\n1\n")
                    return content[0].get("text", str(content))

                # If it's already a string
                if isinstance(content, str):
                    print("\n2\n")
                    return content
    # If it's a string, return as is
    if isinstance(report, str):
        print("\n3\n")
        return report
    # Otherwise, fallback to string conversion
    print("\n4\n")
    return str(report)

# ---- Kafka testing Loop ----
# for message in consumer:
#     packet = message.value
#     print(f"\nReceived packet: {packet}")

#     # Generate threat intel report
#     threat_report = agent.invoke({"messages": [{"role": "user", "content": f"Analyze this packet: {packet}"}]})

#     # If threat_report is not a dict or string, convert it
#     plain_report = extract_text(threat_report)

#     reports_collection.insert_one({
#         "packet": packet,
#         "threat_report": plain_report
#     })

#     print("✅ Threat intel report saved to MongoDB Atlas.")
#     break

# def run_consumer():

while True:
        try:
            print("Inside try")
            consumer = KafkaConsumer(
                'ipfix',
                bootstrap_servers=['kafka:9092'],  # Kafka broker
                group_id='ipfix-consumer-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
            )
            print("Listening for NetFlow packets from Kafka...")

            for message in consumer:
                packet = message.value
                print(f"Received packet: {packet}")

                start_time = time.time()
                threat_report = agent.invoke({"messages": [{"role": "user", "content": f"Analyze this packet: {packet}"}]})
                print("threat_report", threat_report)
                report_latency = time.time() - start_time

                usage = {}
                if hasattr(threat_report, "response_metadata"):
                    usage = threat_report.response_metadata.get("token_usage", {})
                elif hasattr(threat_report, "usage"):
                    usage = threat_report.usage

                plain_report = extract_text(threat_report)
                
                save_time=time.time()
                reports_collection.insert_one({
                    "packet": packet,
                    "threat_report": plain_report,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                save_latency=time.time()-save_time

                print("Threat intel report saved to MongoDB Atlas.")
                print(f"Threat intel report saved. Report Generation Latency: {report_latency:.2f}s | Tokens: {usage} | Report Storage Latency: {save_latency:.2f}s")
                print("-" * 80)

        except Exception as e:
            print(f"Kafka connection error: {e}. Retrying in 10 seconds...")
            time.sleep(10)
