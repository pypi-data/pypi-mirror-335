#!/usr/bin/env python
from browser_use.telemetry.service import ProductTelemetry
from browser_use.telemetry.views import (
    AgentRunTelemetryEvent,
    AgentStepTelemetryEvent,
    AgentEndTelemetryEvent,
    ControllerRegisteredFunctionsTelemetryEvent,
    RegisteredFunction
)

# Optional: Uncomment to disable telemetry (for testing)
# os.environ["ANONYMIZED_TELEMETRY"] = "false"

# Get the telemetry service instance (singleton)
telemetry = ProductTelemetry()

# Example telemetry data
agent_id = "example-agent-123"

# Example 1: Agent Run Event
run_event = AgentRunTelemetryEvent(
    agent_id=agent_id,
    use_vision=True,
    task="Search for Python tutorials",
    model_name="gpt-4o",
    chat_model_library="langchain-openai",
    version="0.1.40",
    source="example_script"
)

# Example 2: Agent Step Event
step_event = AgentStepTelemetryEvent(
    agent_id=agent_id,
    step=1,
    step_error=[],
    consecutive_failures=0,
    actions=[
        {"type": "go_to_url", "url": "https://example.com"},
        {"type": "click_element", "selector": "#search-button"}
    ]
)

# Example 3: Agent End Event
end_event = AgentEndTelemetryEvent(
    agent_id=agent_id,
    steps=5,
    max_steps_reached=False,
    is_done=True,
    success=True,
    total_input_tokens=1250,
    total_duration_seconds=15.7,
    errors=[]
)

# Example 4: Controller Registered Functions Event
controller_event = ControllerRegisteredFunctionsTelemetryEvent(
    registered_functions=[
        RegisteredFunction(name="go_to_url", params={"url": "string"}),
        RegisteredFunction(name="click_element", params={"selector": "string"}),
        RegisteredFunction(name="input_text", params={
            "selector": "string", 
            "text": "string"
        })
    ]
)

# Send the telemetry events
def send_example_telemetry():
    print("Sending example telemetry events...")
    
    # Capture each event
    telemetry.capture(run_event)
    print(f"✓ Sent run event: {run_event.name}")
    
    telemetry.capture(step_event)
    print(f"✓ Sent step event: {step_event.name}")
    
    telemetry.capture(end_event)
    print(f"✓ Sent end event: {end_event.name}")
    
    telemetry.capture(controller_event)
    print(f"✓ Sent controller event: {controller_event.name}")
    
    print("All example telemetry events sent!")

if __name__ == "__main__":
    send_example_telemetry() 