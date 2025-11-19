import requests
import json
import datetime
from datetime import datetime, timedelta
import os 
url = "http://localhost:4560/mcp"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",   # required for MCP streamable HTTP
    "Authorization":  os.getenv("MCP_PROXY_AUTH_TOKEN", "") # if you use MCP_PROXY_AUTH_TOKEN
}
    # Convert timestamp string → datetime
ts = datetime.fromisoformat("2025-11-05T10:25:50.680Z".replace("Z", "+00:00"))
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

response = requests.post(url, headers=headers, data=json.dumps(payload))
print("Status:", response.status_code)
print("Response:", response.text)