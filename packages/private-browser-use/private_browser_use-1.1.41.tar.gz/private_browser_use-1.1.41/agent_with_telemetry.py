#!/usr/bin/env python
"""
Example demonstrating browser-use with telemetry enabled.
Set ANONYMIZED_TELEMETRY=false to disable telemetry.
"""
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent
from browser_use.telemetry.service import ProductTelemetry

# Load environment variables from .env file
load_dotenv()

# Uncomment to disable telemetry
# os.environ["ANONYMIZED_TELEMETRY"] = "false"


async def run_agent_with_telemetry():
    """Run an agent with telemetry enabled and print all events"""
    # Enable debug logging to see telemetry events
    os.environ["BROWSER_USE_LOGGING_LEVEL"] = "debug"

    # Create agent (this will automatically send telemetry events)
    agent = Agent(
        task="Compare prices of iPhones on different websites",
        llm=ChatOpenAI(model="gpt-4o"),
    )

    # Get telemetry service to observe events
    telemetry = ProductTelemetry()
    print(f"Telemetry user ID: {telemetry.user_id}")
    print(f"Telemetry enabled: {telemetry._posthog_client is not None}")

    # Run the agent (this will generate various telemetry events)
    print("\nRunning agent... (telemetry events will be captured)")
    await agent.run(max_steps=5)  # Limit to 5 steps for demo purposes

    # At this point, multiple telemetry events have been sent automatically:
    # 1. AgentRunTelemetryEvent - when agent.run() was called
    # 2. AgentStepTelemetryEvent - for each step the agent takes
    # 3. AgentEndTelemetryEvent - when agent.run() completes
    print("\nAgent run complete. Check logs for telemetry events.")


if __name__ == "__main__":
    asyncio.run(run_agent_with_telemetry()) 