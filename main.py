from agents import Agent, Runner
from agentsdk_gemini_adapter import config
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create an agent using OpenAI Agents SDK
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant that can help with customer orders and support.",
)

# Pass the Gemini configuration in run_config to any Runner method
result = Runner.run_sync(agent, "I want to buy a new laptop", run_config=config)
print(result.final_output)

