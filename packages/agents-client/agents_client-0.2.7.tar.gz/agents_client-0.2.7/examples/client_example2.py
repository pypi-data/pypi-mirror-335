from agent_client import Agent

# Example agent credentials
API_KEY = "osJGAG-SjFMNxlZxb5uCIZKON6Z76lIZnx2nG2atkqo"
AGENT_ID = "d12325b9-b78e-4864-acb7-27fdb49b9eb7"

# Create a simple callback function to handle streaming responses
def handle_response(response):
    print(f"Received: {response.get('type')} - {response.get('message', '')}")

# Initialize the agent
agent = Agent(
    agent_id=AGENT_ID,
    api_key=API_KEY,
    # Optionally provide a callback function during initialization
    stream_callback=handle_response
)

# Start streaming responses in a background thread
agent.start_streaming()

# Send a message to the agent
print("Sending message to agent...")
response = agent.message("Hello, Agent!")
print(f"Message sent! Response ID: {response.get('row_id')}")

# The agent's responses will be streamed to our callback function
print("Waiting for streaming responses...")

# Keep the program running to receive streaming responses
try:
    # For this example, we'll just wait for user input to exit
    input("\nPress Enter to exit...\n")
finally:
    # Stop streaming when done
    agent.stop_streaming()
    print("Streaming stopped")
