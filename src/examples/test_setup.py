import os, json, sys
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
AGENT_ID = os.getenv("AGENT_ID")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_REGION = os.getenv("AGENT_REGION")
AGENT_COMPARTMENT_ID = os.getenv("AGENT_COMPARTMENT_ID")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

# Use @tool to signal that this Python function is a function tool.
# Apply standard docstring to provide function and parameter descriptions.
@tool
def get_weather(location: str) -> Dict[str, str]:
    """
    Get the weather for a given location.

    Args:
      location(str): The location for which weather is queried
    """
    return {"location": location, "temperature": 72, "unit": "F"}

# remove tool after testing of initial setup
def list_tools():

    # Create a client with your authentication details
    client = AgentClient(
        auth_type="api_key",
        profile="frankfurt",  ## TODO
        region=AGENT_REGION
    )

    # Find the tools of the following agent in the following compartment
    tool_list = client.find_tools(AGENT_COMPARTMENT_ID, AGENT_ID)

    json_str = json.dumps(tool_list, indent=4)

    print(json_str)

    for item in tool_list:
        print(f"Tool Name: {item.get('display_name')}  \nTool OCID: {item.get('id')}")


def main():
    # Create an agent client with your authentication and region details
    # Replace the auth_type with your desired authentication method.
    client = AgentClient(
        auth_type="api_key",
        profile="frankfurt",
        region=AGENT_REGION,
    )

    # Create a local agent object with the client, instructions, and tools.
    # You also need the agent endpoint id. To obtain the OCID, follow Step 1.
    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions="You perform weather queries using tools.",
        tools=[get_weather]
    )

    # Sync local instructions and tools to the remote agent resource
    # You only need to invoke setup() when you change instructions and tools
    agent.setup()

    # Run the agent. You can embed this method in your webapp, slack bot, etc.
    # You invoke the run() when you need to handle your user's request.
    input = "Is it cold in Seattle?"
    response = agent.run(input)

    # Print the response
    response.pretty_print()

if __name__ == "__main__":
    main()
    list_tools()