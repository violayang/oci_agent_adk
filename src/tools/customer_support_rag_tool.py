from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.tool.prebuilt import AgenticRagTool
import os, json, sys
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv

## -------------- Set env var --------------------
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
AGENT_ID = os.getenv("AGENT_ID")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_REGION = os.getenv("AGENT_REGION")
AGENT_COMPARTMENT_ID = os.getenv("AGENT_COMPARTMENT_ID")
AGENT_KB_ID = os.getenv("AGENT_KB_ID")
print(AGENT_KB_ID)


def main():

    client = AgentClient(
        auth_type="api_key",
        profile="frankfurt",
        region="eu-frankfurt-1"
    )

    # Assuming the knowledge base is already provisioned

    # Create a RAG tool that uses the knowledge base
    # The tool name and description are optional, but strongly recommended for LLM to understand the tool.
    rag_tool = AgenticRagTool(
        name="OCI RAG tool",
        description="Use this tool to answer questions customer has about products.",
        knowledge_base_ids=[AGENT_KB_ID],
    )

    # Create the agent with the RAG tool
    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions="Answer question using the OCI RAG tool.",
        tools=[rag_tool]
    )

    # Set up the agent once
    agent.setup()

    # Run the agent with a user query
    input = "My internet is running very slow, how do I troubleshoot it?"
    response = agent.run(input)
    response.pretty_print()


if __name__ == "__main__":
    main()
