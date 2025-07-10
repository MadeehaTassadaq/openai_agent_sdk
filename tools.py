import os 
from openai import AsyncOpenAI
import requests,random
from agents import Agent,OpenAIChatCompletionsModel,Runner,set_tracing_disabled,RunConfig,function_tool
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import chainlit as cl
load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")

client=AsyncOpenAI(api_key=gemini_api_key,
              base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model=OpenAIChatCompletionsModel(openai_client=client,
                                 model="gemini-2.5-flash")
set_tracing_disabled(disabled=True)
config=RunConfig(model=model)

@function_tool
def how_many_jokes():
    "generates the number of jokes"
    return random.randint(1,10)
@function_tool
def get_weather(city:str)->str:
    """Get the weather for the required city"""
    try:
        data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=c26482b837c14873aa7190029250907&q={city}")
        data = data.json()
        return f"the weather of the current {city} is {data['current']['temp_c']}c and {data['current']['condition']['text']}."
    except Exception as e:
        return f"could not fetch the weather due to an error: {str(e)}"

# 🧠 Agent definition
agent :Agent= Agent(name="Madeeha",
    instructions=(
        "If the user asks for jokes, first call `how_many_jokes`, then tell that many jokes with numbers. "
        "If the user asks for weather, call the `get_weather` function with the city name."
    ),
    model=model,
    tools=[how_many_jokes, get_weather]
)

@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Hello I am a weather agent i can help you tell weather?").send()

@cl.on_message
async def handle_message(message:cl.on_message):
    history=cl.user_session.get("history")
    history.append({"role":"user","content":message.content})
    
    msg=cl.Message(content="")
    await msg.send()
    result=Runner.run_streamed(
        agent,
        input=history,
        run_config=config
    )
    async for event in result.stream_events():
        if event.type=="raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
            
            
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("history",history)
    await cl.Message(content=result.final_output).send()