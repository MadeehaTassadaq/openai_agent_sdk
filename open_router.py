import os 
from openai import AsyncOpenAI
from agents import Agent,OpenAIChatCompletionsModel,Runner,set_tracing_disabled,RunConfig
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import chainlit as cl
load_dotenv()
openrouter_api_key=os.getenv("OPENROUTER_API_KEY")

client=AsyncOpenAI(api_key=openrouter_api_key,
              base_url="https://openrouter.ai/api/v1/")

model=OpenAIChatCompletionsModel(openai_client=client,
                                 model="google/gemini-2.0-flash-001")
set_tracing_disabled(disabled=True)
config=RunConfig(model=model)

gynaecologit_agent:Agent=Agent(name="Gynaecologist",
            instructions="You are an expert gynaecolgist with 4-5 years practical experience in dealing with women conditions",
            model=model)
obstetric_agent:Agent=Agent(name="Obstetrician",
                            instructions="You are an expert obstetrician with 4-5 years practical experience in dealing with obstetrics",
                         model=model)
main_agent:Agent=Agent(name="OBstetrucs and Gynaecologist",
                            instructions="You are an expert gynaecolgist and obstetrician withover 25-30 years practical experience in dealing with women conditions and obstetrics",
                         model=model,
                         handoffs=[gynaecologit_agent,obstetric_agent])
@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Hello I am a gynaecologist.How can i assist you?").send()

@cl.on_message
async def handle_message(message:cl.on_message):
    history=cl.user_session.get("history")
    history.append({"role":"user","content":message.content})
    
    msg=cl.Message(content="")
    await msg.send()
    result=Runner.run_streamed(
        main_agent,
        input=history,
        run_config=config
    )
    async for event in result.stream_events():
        if event.type=="raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
            
            
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("history",history)
    await cl.Message(content=result.final_output).send()