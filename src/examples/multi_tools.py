import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.tools.custom_function_tools import AccountToolkit
from oci.addons.adk.tool.prebuilt import AgenticRagTool

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")
OCI_PROFILE = os.getenv("OCI_PROFILE")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
AGENT_KB_ID = os.getenv("AGENT_KB_ID")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

def main():

    # Assuming the resources were already provisioned
    agent_endpoint_id = AGENT_EP_ID
    knowledge_base_id = AGENT_KB_ID

    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region="us-chicago-1"
    )

    instructions = """
    You are customer support agent.
    Use RAG tool to answer tax related questions.
    Use function tools to fetch user and org info by id.
    Only orgs of Enterprise plan can use Responses API.
    """

    agent = Agent(
        client=client,
        agent_endpoint_id=agent_endpoint_id,
        instructions=instructions,
        tools=[
            AgenticRagTool(knowledge_base_ids=[knowledge_base_id]),
            AccountToolkit()
        ]
    )

    agent.setup()

    # This is a context your existing code is best at producing (e.g., fetching the authenticated user id)
    client_provided_context = "[Context: The logged in user ID is: user_123] "

    # Handle the first user turn of the conversation
    input = "What is the Responses API"
    input = client_provided_context + " " + input
    response = agent.run(input)
    response.pretty_print()

    # Handle the second user turn of the conversation
    input = "Is my user account eligible for the Responses API?"
    input = client_provided_context + " " + input
    response = agent.run(input, session_id=response.session_id)
    response.pretty_print()

    # Call the RAG Service
    input = "what is the tax M&E adjustment for entity 1000 ?"
    response = agent.run(input)
    response.pretty_print()


if __name__ == "__main__":
    main()