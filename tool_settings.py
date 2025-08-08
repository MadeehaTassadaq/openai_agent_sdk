from agents import (Agent, Runner, function_tool, 
OpenAIChatCompletionsModel, set_tracing_disabled, RunConfig, ModelSettings)
import os
from openai import AsyncOpenAI
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent
gemini_api_key=os.getenv("GEMINI_API_KEY")

client=AsyncOpenAI(api_key=gemini_api_key,
              base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model=OpenAIChatCompletionsModel(openai_client=client,
                                 model="gemini-2.5-flash")
set_tracing_disabled(disabled=True)
config=RunConfig(model=model)
@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    tool_use_behavior="stop_on_first_tool",
    model_settings=ModelSettings(tool_choice="required"),
    model=model
)
@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello! I can provide weather information.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handles incoming messages and interacts with the agent."""
    history = cl.user_session.get("history", [])
    if history is None:
        history = []
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("history", history)
    
    await cl.Message(content="Thinking...").send()
    
    msg = cl.Message(content="")
    await msg.send()
    
    result = Runner.run_streamed(
        agent,
        input=message.content,
        run_config=config,max_turns=1
    )
    
    async for event in result.stream_events():
        if event.type=="raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    
    await cl.Message(content=result.final_output).send()
