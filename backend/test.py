import os
from dotenv import load_dotenv
import json
from langchain.agents import create_agent,AgentExecutor, create_tool_calling_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI


class Weather(BaseModel):
    temperature: float
    condition: str

# load environment variables (.env should contain your API key)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not set")

def weather_tool(city: str) -> str:
    """Get the weather for a city."""
    return f"it's sunny and 70 degrees in {city}"

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=API_KEY
)

agent = create_agent(
    model,
    tools=[weather_tool],
    response_format=ToolStrategy(Weather)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF?"}]
})

print(result)  # Should print a structured Weather object