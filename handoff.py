from agents import Agent, OpenAIChatCompletionsModel, Runner, RunConfig, handoff, function_tool
import os, urllib
from openai import AsyncOpenAI
import requests
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

client=AsyncOpenAI(api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1")

model=OpenAIChatCompletionsModel(
    openai_client=client,
    model="openai/gpt-oss-20b"
)
config=RunConfig(model=model)

@function_tool
def search_google(query: str) -> str:
    """Return the top organic result snippet from Google via SerperAPI for the given query."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "SERPER_API_KEY is not set. Please set it in your environment to enable web search."

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return f"Error: {response.status_code}, {response.text}"
        results = response.json()
     # Return the top organic snippet if available
        if "organic" in results and len(results["organic"]) > 0:
            top = results["organic"][0]
            title = top.get("title", "No title")
            link = top.get("link", "No link")
            snippet = top.get("snippet", "No snippet")
            return f"{title}\n{snippet}\n{link}"
        else:
            return "No results found."
    except Exception as e:
        return f"Search error: {e}"



AI_Assistant=Agent(
    name="AI_Assistant",
    instructions="""You are a helpful AI assistant. For any fact-based or AI-related queries, ALWAYS use the `search_google` tool first and base your answer on its result.""",
    handoff_description="Use web search to help answer AI-related information.",
    tools=[search_google]
 
)
handsoff_obj=handoff(
    agent=AI_Assistant,
    tool_name_override="ai_assistant",
    tool_description_override="Use this for ALL user queries. Do not answer directly; delegate to this assistant which performs web search."
)
assistant=Agent(
    name="assistant",
    instructions="You are a helpful assistant for AI and Agentic AI questions. You must ALWAYS call the `ai_assistant` handoff tool and never answer directly.",
    handoffs=[handsoff_obj]
)

user_input = input("Enter Your Question (type 'exit' to quit): ")

    
try:
    result=Runner.run_sync(
        assistant,
        input=user_input,
        run_config=config,
    )
    print(result.final_output)
except Exception as e:
    print(f"Error: {e}")