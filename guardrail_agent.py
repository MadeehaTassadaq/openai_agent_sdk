import asyncio
from agents import Agent, Runner,function_tool,InputGuardrail,GuardrailFunctionOutput
from agentsdk_gemini_adapter import config
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class HomeWorkOutput(BaseModel):
    is_Homework:bool
    reasoning:str
     
guardrail_agent=Agent(
    name="guardrail_agent",
    instructions="You are a guardrail agent that can help with homework.",
    output_type=HomeWorkOutput,
    )
math_agent=Agent(
    name="math_agent",
    instructions="You are a math agent that can help with math problems.",
    handoff_description="You are a math agent that can help with math problems.",
)
history_agent=Agent(
    name="history_agent",
    instructions="You are a history agent that can help with history questions.",
    handoff_description="You are a history agent that can help with history questions.",
)
async def homework_guardrail(input:str):


# Pass the Gemini configuration in run_config to any Runner method
async def main():
    query:str = input("Enter your query: \n")
    result = await Runner.run(agent, query, run_config=config)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())