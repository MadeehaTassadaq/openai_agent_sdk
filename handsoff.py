import asyncio
from agents import (Agent, RunContextWrapper, handoff,OpenAIChatCompletionsModel,
                Runner, set_tracing_disabled,RunConfig,function_tool)
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

class CurrentUser(BaseModel):
    is_logged_in:bool

client=AsyncOpenAI(api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

model=OpenAIChatCompletionsModel(openai_client=client,
    model="gemini-2.0-flash")

config=RunConfig(model=model)
set_tracing_disabled(disabled=True)

async def can_customer_refund(local_context:RunContextWrapper[CurrentUser],agent:Agent[CurrentUser])->bool:
    print("local_context :",local_context.context)
    print("agent :",agent)
    if local_context.context and local_context.context.is_logged_in:
        return True
    return False

@function_tool
def weather_in_city(city:str)->str:
    return f"The weather in {city} is sunny"

billing_agent = Agent(name="Billing agent",model=model)
refund_agent = Agent(name="Refund agent",model=model)

triage_agent = Agent(
    name="Triage agent", 
    model=model,
    handoffs=[handoff(agent=refund_agent,
    is_enabled=True,
    input_filter=can_customer_refund)
])

async def main():
    current_user=CurrentUser(is_logged_in=True)
    result=await Runner.run(
        triage_agent,"i have send return back my order can u plz refund it order details=12345,amount=100",
        run_config=config,
        context=current_user)

    print(result.final_output)
    print(result.last_agent.name)

if __name__=="__main__":
    asyncio.run(main())
