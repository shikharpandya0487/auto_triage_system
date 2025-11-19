import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import time
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from sentence_transformers import util


# Load environment
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found")

MONGO_URI = os.getenv("MONGO_URI")
SUPABASE_URL = os.getenv("SUPABASE_API", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_API_KEY", "")

if not all([SUPABASE_URL, SUPABASE_KEY, API_KEY]):
    raise ValueError("Missing environment variables. Please set SUPABASE_API, SUPABASE_SERVICE_API_KEY, GEMINI_API_KEY.")


# Setup MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["test"]
chat_history_collection = db["chat_history"]

#  Supabase + Embeddings Setup  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Setup the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=API_KEY
)

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


# Define tools
@tool
def virustotal_lookup_ip(ip: str) -> dict:
    """Lookup an IP address on VirusTotal (v3 API)."""
    key = os.getenv("VIRUSTOTAL_API_KEY")
    if not key:
        return {"error": "VIRUSTOTAL_API_KEY not set"}
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": key}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"VirusTotal error {resp.status_code}", "text": resp.text}

@tool
def abuseipdb_lookup_ip(ip: str, max_age_in_days: int = 90) -> dict:
    """Lookup IP via AbuseIPDB."""
    key = os.getenv("ABUSEIPDB_API_KEY")
    if not key:
        return {"error": "ABUSEIPDB_API_KEY not set"}
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {"ipAddress": ip, "maxAgeInDays": max_age_in_days}
    headers = {"Key": key, "Accept": "application/json"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"AbuseIPDB error {resp.status_code}", "text": resp.text}

@tool
def whois_lookup(ip: str) -> dict:
    """Perform WHOIS lookup for an IP."""
    url = f"http://ipwho.is/{ip}"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"Whois error {resp.status_code}", "text": resp.text}

@tool
def retrieve(query: str):
    """
    Retrieve cybersecurity context from the Supabase vector database.
    Searches for related incidents, mitigation steps, and attack strategies.
    """
    retrieved_docs = vector_store.similarity_search(query, k=6)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs
    """  """

#-----Elastic Search MCP Tool -----  
@tool
def get_neighboring_packets(ianaflowStartMilliseconds: str) -> str:
    """
    Query the local MCP Elasticsearch server to get packets within ±2 minutes of a given packet's iana:flowStartMilliseconds.
    """
    url = "http://localhost:4560/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": os.getenv("MCP_PROXY_AUTH_TOKEN", ""),  # optional
    }

    # Convert timestamp string to datetime
    ts = datetime.fromisoformat(ianaflowStartMilliseconds.replace("Z", "+00:00"))
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
    
# Create the cyber intelligence agent
agent = create_agent(
    model=llm,
    tools=[virustotal_lookup_ip, abuseipdb_lookup_ip, whois_lookup, retrieve, get_neighboring_packets],
    system_prompt=(
        "You are an advanced Cyber Threat Intelligence (CTI) Agent built to investigate, "
        "analyze, and correlate cybersecurity threats using multiple data sources and reasoning capabilities."
        
        "Your goal is to assist security analysts by:"
        " - Investigating suspicious IPs or network indicators."
        " - Correlating intelligence from public threat databases."
        " - Retrieving relevant cybersecurity documents, incidents, and mitigations from the internal knowledge base."
        " - Providing clear, evidence-backed conclusions with proper reasoning."

        "You are equipped with the following tools:"
        "1. VirusTotal Lookup Tool (`virustotal_lookup_ip`) "
        "Used to query IP addresses from the VirusTotal API (v3). Returns reputation details, related detections, "
        "and any associated malicious reports."

        "2. AbuseIPDB Lookup Tool (`abuseipdb_lookup_ip`) "
        "Used to assess the reputation of an IP address against the AbuseIPDB database. "
        "Helps determine if the IP has been reported for malicious activities like spam, DDoS, or botnet behavior."

        "3. WHOIS Lookup Tool (`whois_lookup`) "
        "Used to perform WHOIS lookups for IP addresses. Returns ownership details, ASN information, and geolocation "
        "to trace the potential origin of a threat."

        "4. Context Retrieval Tool (`retrieve`) "
        "Queries the Supabase vector database to retrieve cybersecurity context such as prior incidents, "
        "attack patterns, and remediation strategies relevant to the query. "
        "This helps in correlating new threats with historical knowledge."

        "5. Neighbouring Packets Retrieval Tool (`get_neighboring_packets`) "
        "Queries Elastic Search to retrieve NetFlow packets within ± 2 minutes of the timestamp of the packet currently being processed, "
        "to answer questions about previous packets. "
        "This helps in identifying threats with help of past packet history."

        "Behavioral Instructions:"
        "- Always cross-verify your findings from multiple sources when possible."
        "- Provide concise, actionable intelligence summaries (avoid raw dumps unless requested)."
        "- When uncertain, clearly state the limitation and suggest possible next steps."
        "- Maintain a professional tone, but ensure your reasoning is transparent and analytical."
        "- Structure responses logically with sections like *Summary*, *Findings*, and *Conclusion* for clarity."

        "You are operating as an autonomous CTI analyst who can synthesize data from the above tools, "
        "generate structured threat intelligence reports, and adapt your response based on the given query context "
        "and past conversation history."
    )
)


def test_vectorstore_similarity(vector_store, embedding_model, test_queries, k=5, threshold=0.6):
    """
    Tests whether the vector store returns semantically similar documents.

    Args:
        vector_store: The SupabaseVectorStore instance.
        embedding_model: The embedding model used (e.g. HuggingFaceEmbeddings()).
        test_queries (list[str]): A list of queries to test.
        k (int): Number of top documents to retrieve per query.
        threshold (float): Minimum average similarity score expected (0–1).

    Returns:
        dict: Summary of results for each query with similarity diagnostics.
    """
    print("\n Running Vector Store Similarity Test...\n")
    results_summary = {}

    for query in test_queries:
        print(f"Query: {query}")
        try:
            # Retrieve similar documents
            retrieved_docs = vector_store.similarity_search(query, k=k)

            if not retrieved_docs:
                print("No documents retrieved.")
                results_summary[query] = {"status": "fail", "reason": "No results"}
                continue

            # Embed query and docs using the provided embedding model
            query_emb = embedding_model.embed_query(query)
            doc_embs = [embedding_model.embed_query(doc.page_content) for doc in retrieved_docs]

            # Compute cosine similarities
            similarities = [util.cos_sim(query_emb, emb).item() for emb in doc_embs]
            avg_sim = sum(similarities) / len(similarities)

            # Log result
            for i, (doc, sim) in enumerate(zip(retrieved_docs, similarities), 1):
                snippet = doc.page_content[:150].replace("\n", " ")
                print(f"   {i}. sim={sim:.3f} → {snippet}...")

            print(f"Avg similarity: {avg_sim:.3f}")

            results_summary[query] = {
                "status": "pass" if avg_sim >= threshold else "low_similarity",
                "avg_similarity": avg_sim,
                "retrieved_docs": [doc.page_content for doc in retrieved_docs],
            }

        except Exception as e:
            print(f"Error while testing query '{query}': {e}")
            results_summary[query] = {"status": "error", "error": str(e)}

        print("-" * 60)

    return results_summary



app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # or ["POST", "GET"]
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_endpoint(request: Request):
    body = await request.json()
    query = body.get("query", "")
    packet = body.get("packet", None)

    # --- Prepare packet context for agent ---
    packet_context = ""
    if packet:
        packet_context = (
            "Network Packet Data Provided:\n"
            f"{json.dumps(packet, indent=2)}\n\n"
            "Use the IPs (source/destination) or relevant details from this packet to perform "
            "threat intelligence lookups (VirusTotal, AbuseIPDB, WHOIS) where useful."
        )

    # # --- Load chat history from MongoDB ---
    history_docs = list(chat_history_collection.find().sort("_id", -1).limit(10))
    history_text = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history_docs]) if history_docs else ""

    # --- Build full context for agent ---
    input_messages = []
    # if history_text:
    #     input_messages.append({"role": "system", "content": f"Recent conversation history:\n{history_text}"})
    if packet_context:
        input_messages.append({"role": "system", "content": packet_context})
    input_messages.append({"role": "user", "content": query})

    # --- Track latency start ---
    start_time = time.time()

    # --- Invoke agent ---
    result = agent.invoke({"messages": input_messages})
    
    end_time = time.time()
    latency = round(end_time - start_time, 2)

    # --- Extract token usage if available ---
    total_tokens = None
    input_tokens = None
    output_tokens = None

    # --- Save this conversation turn to MongoDB ---
    chat_history_collection.insert_one({
        "user": query,
        "assistant": result["output"] if isinstance(result, dict) and "output" in result else str(result)
    })

    # --- Return response ---
    last_ai_message = None
    if isinstance(result, dict) and "messages" in result:
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                content = msg.content
                if isinstance(content, list):
                    # Extract 'text' fields and join if multiple parts
                    texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                    content = "\n".join(texts)
                if hasattr(msg, "usage_metadata") and isinstance(msg.usage_metadata, dict):
                    input_tokens = msg.usage_metadata.get("input_tokens")
                    output_tokens = msg.usage_metadata.get("output_tokens")
                    total_tokens = msg.usage_metadata.get("total_tokens")
                last_ai_message = content
                break
    #print(last_ai_message)
    print(f"Latency: {latency}s | Tokens: total={total_tokens}, input={input_tokens}, output={output_tokens}")

    return {
        "response": str(last_ai_message) or "No AIMessage found",
    }



# if __name__ == "__main__":
#     sample_queries = [
#         "What are common ransomware attack vectors?",
#         "Mitigation steps for SQL injection",
#         "How to detect phishing attempts"
#     ]

#     report = test_vectorstore_similarity(vector_store, embeddings, sample_queries)
#     print("\n Test Summary:\n", json.dumps(report, indent=2))
