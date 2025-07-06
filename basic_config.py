import asyncio
from agents import Agent, Runner,function_tool
from agentsdk_gemini_adapter import config
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@function_tool
def get_weather(city:str):
    """Get the weather of a city"""
    return f"The weather of {city} is SunnY"

# Create an agent using OpenAI Agents SDK
agent = Agent(
    name="weather_haikus_agent",
    instructions="You are a weather haiku agent that can create haikus about weather.",
    tools=[get_weather],
)

# Pass the Gemini configuration in run_config to any Runner method
async def main():
    query:str = input("Enter your query: \n")
    result = await Runner.run(agent, query, run_config=config)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())