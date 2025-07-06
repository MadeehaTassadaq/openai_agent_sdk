import asyncio
from agents import Agent, Runner, function_tool
from dataclasses import dataclass
from agentsdk_gemini_adapter import config
from typing import List
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@dataclass
class Purchase:
    id: str
    name: str
    price: float
    date: str

@dataclass
class UserContext:
    uid: str
    is_pro_user: bool
    
    async def fetch_purchases(self) -> List[Purchase]:
        # This is a mock implementation
        # In a real application, this would fetch from a database
        if self.uid == "user123":
            return [
                Purchase(id="p1", name="Basic Plan", price=9.99, date="2023-01-15"),
                Purchase(id="p2", name="Premium Add-on", price=4.99, date="2023-02-20"),
                Purchase(id="p3", name="Annual Subscription", price=99.99, date="2023-03-10")
            ]
        elif self.uid == "user456":
            return [
                Purchase(id="p4", name="Free Trial", price=0.00, date="2023-01-01")
            ]
        return []

@function_tool
async def get_user_info(context: UserContext) -> str:
    """Get personalized information about the user including ID and subscription status"""
    user_type = "Pro" if context.is_pro_user else "Free"
    return f"User ID: {context.uid}, Subscription Type: {user_type}"

@function_tool
async def get_purchase_history(context: UserContext) -> str:
    """Get the complete purchase history for the current user"""
    purchases = await context.fetch_purchases()
    if not purchases:
        return "No purchase history found for this user."
    
    result = "Purchase History:\n"
    total_spent = 0.0
    for i, p in enumerate(purchases, 1):
        result += f"{i}. {p.name}: ${p.price:.2f} on {p.date}\n"
        total_spent += p.price
    
    result += f"\nTotal spent: ${total_spent:.2f}"
    result += f"\nNumber of purchases: {len(purchases)}"
    return result

@function_tool
async def get_personalized_greeting(context: UserContext) -> str:
    """Get a personalized greeting based on user status and purchase history"""
    purchases = await context.fetch_purchases()
    
    if context.is_pro_user:
        if len(purchases) > 2:
            return "Welcome back, valued Pro member! Your loyalty with multiple purchases is greatly appreciated."
        else:
            return "Welcome back to our premium service! We value your continued support."
    else:
        if len(purchases) > 0:
            return "Welcome back! We see you've tried our service. Consider upgrading to Pro for unlimited access."
        else:
            return "Welcome! Consider upgrading to our Pro plan for additional features and benefits."

@function_tool
async def get_user_statistics(context: UserContext) -> str:
    """Get detailed statistics about the user's account and purchases"""
    purchases = await context.fetch_purchases()
    
    total_spent = sum(p.price for p in purchases)
    avg_purchase = total_spent / len(purchases) if purchases else 0
    
    stats = f"User Statistics for {context.uid}:\n"
    stats += f"Account Type: {'Pro' if context.is_pro_user else 'Free'}\n"
    stats += f"Total Purchases: {len(purchases)}\n"
    stats += f"Total Spent: ${total_spent:.2f}\n"
    if purchases:
        stats += f"Average Purchase: ${avg_purchase:.2f}\n"
        stats += f"First Purchase: {min(p.date for p in purchases)}\n"
        stats += f"Latest Purchase: {max(p.date for p in purchases)}\n"
    
    return stats

@function_tool
async def get_recommendations(context: UserContext) -> str:
    """Get personalized recommendations based on user status and purchase history"""
    purchases = await context.fetch_purchases()
    
    if context.is_pro_user:
        if len(purchases) >= 3:
            return "As a loyal Pro member, you might be interested in:\n- Early access to new features\n- Priority customer support\n- Exclusive content and tutorials\n- Referral rewards program"
        else:
            return "As a Pro member, consider exploring:\n- Advanced features and tools\n- Premium content library\n- Custom integrations\n- Dedicated account manager"
    else:
        if len(purchases) > 0:
            return "Based on your activity, you might enjoy:\n- Upgrading to Pro for unlimited access\n- Exploring premium features\n- Access to exclusive content\n- Priority support"
        else:
            return "Get started with:\n- Free trial of Pro features\n- Basic tutorials and guides\n- Community support forum\n- Upgrade to Pro for full access"

context_agent = Agent[UserContext](
    name="user context agent",
    instructions="""You are a helpful assistant that provides personalized responses based on the user context.
    
    IMPORTANT: Always use the available tools to get current information about the user before responding.
    Do not make assumptions about user data - always fetch it using the tools.
    
    Available tools:
    - get_user_info: Get basic user information (ID and subscription type)
    - get_purchase_history: Get detailed purchase history with totals
    - get_personalized_greeting: Get a personalized greeting based on user status
    - get_user_statistics: Get comprehensive account statistics
    - get_recommendations: Get personalized recommendations
    
    For Pro users: Provide detailed, premium-level service with comprehensive information
    For Free users: Be encouraging and highlight upgrade benefits
    
    Always use multiple tools to provide complete, accurate information.""",
    tools=[get_user_info, get_purchase_history, get_personalized_greeting, get_user_statistics, get_recommendations]
)

async def main():    
    # Create a sample user context
    pro_user_context = UserContext(uid="user123", is_pro_user=True)
    free_user_context = UserContext(uid="user456", is_pro_user=False)
    
    # Example using the context agent with a pro user
    print("\n=== Pro User Example ===")
    result = await Runner.run(
        context_agent, 
        "Give me a complete overview of my account including statistics and recommendations", 
        context=pro_user_context,
        run_config=config
    )
    print("Response for Pro User:", result.final_output)
    
    # Example using the context agent with a free user
    print("\n=== Free User Example ===")
    result = await Runner.run(
        context_agent, 
        "Tell me about my account and what you recommend for me", 
        context=free_user_context,
        run_config=config
    )
    print("Response for Free User:", result.final_output)
   

if __name__ == "__main__":
    asyncio.run(main())               