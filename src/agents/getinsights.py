"""
getinsights.py
Author: Anup Ojah
Date: 2025-07-18
=================================
==Get Business Insight Assistant==
==================================
This module initializes and runs an OCI GenAI Agent with Redis and Tavily MCP tool integrations.
It supports enterprise finance-related prompts (AP, GL, AR) and enables real-time web search via Tavily.
Workflow Overview:
1. Load config and credentials from .env
2. Start MCP clients for Redis and Tavily
3. Register tools with the agent
4. Run the agent with user input and print response
"""

import asyncio, os

from mcp.client.session_group import StreamableHttpParameters
from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.mcp import MCPClientStreamableHttp
from pathlib import Path
from dotenv import load_dotenv
from oci.addons.adk.tool.prebuilt import AgenticRagTool
from mcp.client.stdio import StdioServerParameters
from oci.addons.adk.mcp import MCPClientStdio
from anyio import get_cancelled_exc_class
from src.prompt_engineering.topics.ask_data import prompt_Agent_Auditor
from src.llm.oci_genai_agent import initialize_oci_genai_agent_service

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
REDIS_MCP_SERVER = os.getenv("REDIS_MCP_SERVER")
TAVILY_MCP_SERVER = os.getenv("TAVILY_MCP_SERVER")



async def agent_flow(input_prompt: str, session_id:str):

    # MCP REDIS Server endpoint configs
    redis_server_params = StreamableHttpParameters(
        url=REDIS_MCP_SERVER,
    )

    # Use npx
    tavily_server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", TAVILY_MCP_SERVER])

    # time_server_params = StdioServerParameters(
    #     command="uvx",
    #     args=["mcp-server-time", "--local-timezone=America/Los_Angeles"],
    # )

    # Start both MCP clients manually
    # time_mcp_client = MCPClientStdio(params=time_server_params)
    redis_mcp_client = MCPClientStreamableHttp(params=redis_server_params)
    tavily_mcp_client = MCPClientStdio(params=tavily_server_params)

    # await time_mcp_client.__aenter__()
    await redis_mcp_client.__aenter__()
    await tavily_mcp_client.__aenter__()


    try:
        # Setup agent client
        client = AgentClient(
            auth_type="api_key",
            config=OCI_CONFIG_FILE,
            profile=OCI_PROFILE,
            region=AGENT_REGION
        )

        agent = Agent(
            client=client,
            agent_endpoint_id=AGENT_EP_ID,
            instructions= prompt_Agent_Auditor,
            tools=[
                # await time_mcp_client.as_toolkit(),
                await redis_mcp_client.as_toolkit(),
                await tavily_mcp_client.as_toolkit(),
            ],
        )

        agent.setup()

        print(f"Running: {input_prompt}")
        try:
            if(session_id == ""):
                response = await agent.run_async(input_prompt, max_steps=10)
            else:
                response = await agent.run_async(input_prompt, session_id=session_id ,max_steps=10) # working on a bug with session_id

            session_id = response.session_id  # <-- global variable is now updated
            print(f"Session ID: {session_id}")
            response.pretty_print()
        except get_cancelled_exc_class():
            print("🟡 Agent run cancelled (tool timeout or interrupt).")

    finally:
        # Clean shutdown with full cancel error suppression
        # try:
        #     await time_mcp_client.__aexit__(None, None, None)
        # except get_cancelled_exc_class():
        #     print("⚠️ MCPClientStdio cancelled during shutdown.")
        try:
            await tavily_mcp_client.__aexit__(None, None, None)
        except get_cancelled_exc_class():
            print("⚠️ MCPClientStdio cancelled during tavily_mcp_client shutdown.")

        try:
            await redis_mcp_client.__aexit__(None, None, None)
        except get_cancelled_exc_class():
            print("⚠️ MCPClientStreamableHttp cancelled during redis_mcp_client shutdown.")

    return response


if __name__ == "__main__":
    generative_ai_agent_runtime_client, session_id = initialize_oci_genai_agent_service()
    print(f"<UNK> Generative AI Agent {session_id}")

    # Test input
    input_message = (
        "Search the internet to find out the best way to pay an invoice. "
        "Using the best practices from above, answer - Which invoice should I pay first based on criteria such as highest amount due and highest past due date for 'session:e5f6a932-6123-4a04-98e9-6b829904d27f'"
    )
    asyncio.run(agent_flow(input_message, session_id)) # ✅ safe now with proper async context use

