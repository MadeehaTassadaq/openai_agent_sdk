from agents import Agent,Runner
from agentsdk_gemini_adapter import config
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


model = config.GeminiModel(
    model_name="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
)

order_agent = Agent(
    name="order_agent",
    description="A simple agent that can handle customer order details",
    model=model
    )

customer_agent = Agent(
    name="customer_agent",
    description="A simple agent that can handle customer support details",
    model=model
    )
trial_agent = Agent(
    name="trial_agent",
    description="A simple agent that can handsoff order details to order agent and customer support details to customer agent",
    model=model,
    tools=[order_agent,customer_agent])

query = "I want to buy a new laptop"
result = Runner.run_sync(trial_agent, query)
print(result.final_output)

