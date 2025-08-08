from agents import (Agent, OpenAIChatCompletionsModel, 
                    Runner, set_tracing_disabled,
                    RunConfig, function_tool,RunContextWrapper)
from openai import AsyncOpenAI
import asyncio
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=os.getenv("gemini_api_key"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

model= OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash")


set_tracing_disabled(True)
@dataclass
class UserInfo:
    name: str
    age: int
    uid:int
    
@function_tool
async def get_user_age(wrapper:RunContextWrapper[UserInfo]) -> str:
    """Get user information."""
    return f"user {wrapper.context.name} is {wrapper.context.age} years old."

async def main():
    user_info = UserInfo(name="Madeeha", age=35, uid=12345)
    agent = Agent(
        name="UserInfoAgent",
        instructions="""An agent that provides user age using the tool 
        get_user_age.""",
        tools=[get_user_age],
        model=model,   
        )
    result = await Runner.run(
        starting_agent=agent,
        input="What is the user age? ",
        context=user_info     
    )
    print(result.final_output)
if __name__ == "__main__":
    asyncio.run(main())