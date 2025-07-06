import asyncio
from agents import Agent, Runner,function_tool
from agentsdk_gemini_adapter import config
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import List
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")  # Debug print

@dataclass
class user_context:
    user_id:str
    is_pro_user:bool

@function_tool
def get_user_context(context:user_context):
    """Get the user context and return a greeting based on user status"""
    if context.is_pro_user:
        return f"Welcome back, Pro User {context.user_id}! Thank you for being a premium member. How can I assist you today?"
    else:
        return f"Hello User {context.user_id}! Welcome to our service. Consider upgrading to Pro for premium features."

# Create an agent using OpenAI Agents SDK
agent = Agent[user_context](
    name="greet user",
    instructions="You are a greeting agent. When a user asks to be greeted, ALWAYS use the get_user_context tool with the provided context to greet them appropriately. Do not ask for additional information - use the context that is already provided.",
    tools=[get_user_context],
)
print(f"Agent: {agent}")  # Debug print
pro_user=user_context(user_id="1",is_pro_user=True)
free_user=user_context(user_id="2",is_pro_user=False)
print(f"pro_user: {pro_user}")  # Debug print
# Pass the Gemini configuration in run_config to any Runner method


result = Runner.run_sync(agent, "please greet me",context=pro_user, run_config=config)
result = Runner.run_sync(agent, "please greet me",context=free_user, run_config=config)
print(f"Result object: {result}")  # Debug print
print(result.final_output)


