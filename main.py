from agents import Agent, Runner,set_tracing_export_api_key,trace
from agentsdk_gemini_adapter import config
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
openai_key=os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
set_tracing_export_api_key(openai_key)
# Create an agent using OpenAI Agents SDK

assisstant_agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant that can help with customer orders and support.",
)

async def main():
    msg=input("Hi! We speak French, Spanish and English. How can I help?\n")
    agent=assisstant_agent
    inputs=msg
    while True:
        with trace("new workflow"):
        # Pass the Gemini configuration in run_config to any Runner method
            result = Runner.run_streamed(
            agent, 
            inputs,
            run_config=config
            )
        async for event in result.stream_events():
            if event.type =="run_item_stream_event":
                if event.item.type == "handoff_call_item":
                    print(event.item)

        user_input = input("Enter a message: ")
        if user_input.strip().lower() == "exit":
                break
        # Continue the conversation with accumulated history plus the new user message
        history = result.to_input_list()
        history.append({"role": "user", "content": user_input})
        inputs = history

if __name__=="__main__":
    asyncio.run(main())