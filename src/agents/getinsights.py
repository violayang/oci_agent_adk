import asyncio, os

from mcp.client.session_group import StreamableHttpParameters
from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.mcp import MCPClientStreamableHttp
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
AGENT_REGION = os.getenv("AGENT_REGION")


async def agent_flow(input_message:str):

    params = StreamableHttpParameters(
        url="https://cf95-104-48-173-98.ngrok-free.app/mcp",
    )

    async with MCPClientStreamableHttp(
        params=params,
        name="redis mcp server",
    ) as mcp_client:

        client = AgentClient(
            auth_type="api_key",
            config=OCI_CONFIG_FILE,
            profile=OCI_PROFILE,
            region=AGENT_REGION
        )

        agent = Agent(
            client=client,
            agent_endpoint_id=AGENT_EP_ID,
            instructions="You are a Redis-savvy assistant.Only allow read operation with the best tool you have",
            tools=[await mcp_client.as_toolkit()],
        )

        agent.setup()

        # Should trigger the `add` tool
        print(f"Running: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        return agent

async def agent_setup():

        input_message = "which Invoice I should pay first based criteria such as highest amount due and highest past due date for 'session:e5f6a932-6123-4a04-98e9-6b829904d27f'"
        agent = await agent_flow(input_message)

if __name__ == "__main__":
    asyncio.run(agent_setup())