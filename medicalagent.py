import asyncio
from agents import Agent, Runner
from agentsdk_gemini_adapter import config
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create an agent using OpenAI Agents SDK
agent = Agent(
    name="Medical Assistant",
    instructions="You are a helpful assistant that can help with medical questions and answers.",
)

# Pass the Gemini configuration in run_config to any Runner method
async def main():
    query:str = input("Enter your query: \n")
    result = await Runner.run(agent, query, run_config=config)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())