# Simple example demonstrating all capabilities of the Agent client
from agent_client import Agent
import time

# Configuration - replace with your actual credentials
API_KEY = "osJGAG-SjFMNxlZxb5uCIZKON6Z76lIZnx2nG2atkqo"
AGENT_ID = "2f86289c-33c6-40d7-bfa6-cda143dcc094"
BASE_URL = "http://localhost:6665"  # Change if your API is hosted elsewhere

# Callback function for streaming responses
def handle_response(response):
    print(f"STREAM: {response.get('type', 'unknown')} - {response.get('message', '')[:50]}...")

# Initialize agent
agent = Agent(
    agent_id=AGENT_ID,
    api_key=API_KEY,
    base_url=BASE_URL,
    stream_callback=handle_response
)

# Demo all capabilities
def run_demo():
    print("\n==== Agent Client Demo ====\n")
    
    # 1. Send a message
    print("1. Sending message to agent...")
    message_response = agent.message("Please analyze the project structure and report back.")
    print(f"   Response: {message_response}\n")
    
    # 2. Start streaming responses
    print("2. Starting response stream...")
    agent.start_streaming()
    print("   Stream started in background\n")
    
    # 3. Upload a file example (commented out to avoid creating files)
    print("3. File upload example (skipped, but would use):")
    print("   agent.upload_file('path/to/destination.txt', open('local_file.txt', 'rb'))\n")
    
    # Wait to see some streaming responses
    print("   Waiting for 5 seconds to see stream responses...")
    time.sleep(5)
    print("   Continuing with demo\n")
    
    # 4. Stop the agent
    print("4. Stopping the agent...")
    stop_response = agent.stop_agent(
        message="Demo completed",
        reason="Example demonstration finished"
    )
    print(f"   Response: {stop_response}\n")
    
    # 5. Stop streaming (cleanup)
    print("5. Stopping response stream...")
    agent.stop_streaming()
    print("   Stream stopped\n")
    
    print("==== Demo Complete ====")
    print("All Agent capabilities demonstrated:")
    print("- Sending messages")
    print("- Streaming responses")
    print("- Uploading files (example shown)")
    print("- Stopping agent execution")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        # Ensure we stop streaming when exiting
        agent.stop_streaming()