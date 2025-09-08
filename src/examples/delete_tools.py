import json, os
from oci.addons.adk import Agent, AgentClient, tool

from pathlib import Path
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")
OCI_PROFILE = os.getenv("OCI_PROFILE")
AGENT_ID = os.getenv("AGENT_ID")
AGENT_REGION = os.getenv("AGENT_REGION")
AGENT_COMPARTMENT_ID = os.getenv("AGENT_COMPARTMENT_ID")

def delete_tools():

    # Create a client with your authentication details
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    # Find the tools of the following agent in the following compartment
    tool_list = client.find_tools(AGENT_COMPARTMENT_ID, AGENT_ID)

    json_str = json.dumps(tool_list, indent=4)

    print(json_str)

    for item in tool_list:
        print(f"Tool Name: {item.get('display_name')}  \nTool OCID: {item.get('id')}")

    for item in tool_list:
        print(f"Deleting tool {item.get('display_name')} with tool OCID: {item.get('id')}")
        client.delete_tool(item.get('id'))

    print("Tool deleted!")

if __name__ == "__main__":
    delete_tools()