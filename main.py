# 📦 Import Required Libraries
import os
from dotenv import load_dotenv
import asyncio,json,requests

from agents import (
    Agent,                           # 🤖 Core agent class
    Runner,                          # 🏃 Runs the agent
    AsyncOpenAI,                     # 🌐 OpenAI-compatible async client
    OpenAIChatCompletionsModel,     # 🧠 Chat model interface
    function_tool,                   # 🛠️ Decorator to turn Python functions into tools     # ⚙️ (Optional) Set default OpenAI client
    set_tracing_disabled          # 🚫 Disable internal tracing/logging
)


# 🌿 Load environment variables from config.env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# 🚫 Disable tracing for clean output (optional for beginners)
set_tracing_disabled(disabled=True)

# 🔐 1) Environment & Client Setup
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # 🔑 Get your API key from environment
BASE_URL = "https://api.groq.com/openai/v1"  # 🌐 Gemini-compatible base URL (set this in .env file)

# 🌐 Initialize the AsyncOpenAI-compatible client with Gemini details
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url=BASE_URL,
)

# 🧠 2) Model Initialization
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="qwen/qwen3-32b",        # ⚡ Fast Gemini model
    openai_client=external_client
)
@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city"""
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?q={city}&key={WEATHER_API_KEY}")
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant weather information
        if 'current' in data and 'location' in data:
            location = data['location']
            current = data['current']
            return f"Weather in {location['name']}, {location['country']}: {current['temp_c']}°C, {current['condition']['text']}"
        else:
            return f"Weather data not available for {city}"
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"

@function_tool
def get_real_time_data(query: str) -> str:
    try:
    #   """Get the real time data for a given query from google"""
        params = {
        "q": query,
        "api_key": SERP_API_KEY
    }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
     #   Extract relevant information from search results
        if 'organic_results' in data and data['organic_results']:
            results = data['organic_results'][:3]  # Get first 3 results
            formatted_results = []
            for result in results:
                formatted_results.append(f"• {result.get('title', 'No title')}: {result.get('snippet', 'No description')}:{result.get('link', 'link')}")
            return "\n".join(formatted_results)
        else:
            return f"No search results found for: {query}"
    except Exception as e:
        return f"Error searching for {query}: {str(e)}"

# 🔍 3) Create the Agent
agent: Agent = Agent(name="Live Agent",
    model=model,
    tools=[get_weather, get_real_time_data],
    instructions="""You are a helpful assistant that can get weather information and real-time data from the internet. 
    When asked about currency exchange rates, stock prices, or current events, use the get_real_time_data function to search for the latest information.
    When asked about weather, use the get_weather function.
    Always provide clear, concise responses based on the data you retrieve.""",
    
)
async def main():
    try:
        print("🔍 Starting agent with query")
        response = await Runner.run(
            starting_agent=agent,
            input="What is the rate of dollar in pakistan and what is the weather in Islamabbad?"
        )
        print("✅ Agent response received:")
        print(response.final_output)
    except Exception as e:
        print(f"❌ Error running agent: {str(e)}")
        print("Please check your API keys and internet connection.")
if __name__ == "__main__":
    asyncio.run(main())
