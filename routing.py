from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,set_tracing_export_api_key
)
from  hooks import MyAgentHook
from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
import asyncio
from dotenv import load_dotenv
load_dotenv()
from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace

import os
openai_key=os.getenv("OPENAI_API_KEY")
set_tracing_export_api_key(openai_key)
gemini_api_key=os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)


french_agent = Agent(
    name="french_agent",
    instructions="You only speak French",
    model=model
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish",
    model=model
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English",
    model=model,
    hooks=MyAgentHook()
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
    model=model
)

async def main():
    msg=input("Hi! We speak French, Spanish and English. How can I help?\n")
    agent=triage_agent
    inputs=msg

    while True:
        with trace("routing demo",group_id="conversation_id"):
            result=Runner.run_streamed(
                agent,
                inputs,
            )
            async for event in result.stream_events():
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    print(data.delta, end="", flush=True)
                elif isinstance(data, ResponseContentPartDoneEvent):
                    print("\n")

            print("\n")
            user_msg = input("Enter a message: ")
            if user_msg.strip().lower() == "exit":
                break
            # Continue the conversation with accumulated history plus the new user message
            history = result.to_input_list()
            history.append({"role": "user", "content": user_msg})
            inputs = history
            
if __name__=="__main__":
    asyncio.run(main())