from dotenv import load_dotenv
from typing import Any
import requests
import os
from agents import Runner,set_tracing_disabled,Agent,AgentHooks,RunContextWrapper,function_tool,Tool
from agentsdk_gemini_adapter import config

load_dotenv()
set_tracing_disabled(True)

class MyAgentHooks(AgentHooks):
    
    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this
        agent."""
        print("Agent Hook Starts")

    async def on_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print("Agent Hook Ends")

    async def on_handoff(
        self,
        context: RunContextWrapper,
        agent: Agent,
        source: Agent,
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing
        off to this agent."""
        print("hands off hook")
        print("From agent",{source.name})
        print("To Agent",{agent.name})
        

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
    ) -> None:
        """Called before a tool is invoked."""
        print("weather tool Fire..")
        print("tool_name",tool)

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print("Tool Hook End")

@function_tool
def get_weather(city:str)->str:
    """Get the weather for the required city"""
    try:
        data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=c26482b837c14873aa7190029250907&q={city}")
        data = data.json()
        return f"the weather of the current {city} is {data['current']['temp_c']}c and {data['current']['condition']['text']}."
    except Exception as e:
        return f"could not fetch the weather due to an error: {str(e)}"

weather_agent:Agent=Agent(name="Weather_agent",
instructions="You tell the weather of the city?",
handoff_description="You are provide tool to tell weather of the city?",
tools=[get_weather],
hooks=MyAgentHooks())

agent:Agent=Agent(name="Assistant",
instructions="You are a helpful assistant who handsoff to the weather agent",
handoffs=[weather_agent],
hooks=MyAgentHooks())


async def main():
    msg=input("I am an AI Agent that can Tell weather of the given city?\n")
    try:
        result=await Runner.run(
            agent,
            input=msg,
            run_config=config
        )
        print("Final result:", result.final_output)
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


