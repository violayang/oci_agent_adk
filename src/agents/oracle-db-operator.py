"""
oracle-db-operator.py
Author: Anup Ojah
Date: 2025-23-18
=================================
==Oracle Database Operator==
==================================
This agent integrates with Oracle DB SQLCl MCP Server, allowing NL conversation with any Oracle Database (19 c or higher).
https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/using-oracle-sqlcl-mcp-server.html
Workflow Overview:
1. Load config and credentials from .env
2. Start MCP clients for SQLCL
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



async def start_sql_agent():
    # Initialize SQLcl MCP Tool (Persistent)
    adb_server_params = StdioServerParameters(
        command="/Applications/sqlcl/bin/sql",
        args=["-mcp"])

    adb_mcp_client = await MCPClientStdio(params=adb_server_params).__aenter__()

    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=prompt_Agent_Auditor,
        tools=[
            await adb_mcp_client.as_toolkit(),
        ],
    )

    agent.setup()

    return agent, adb_mcp_client  # return both to close later

async def main():
    agent, mcp_client = await start_sql_agent()

    try:
        while True:
            try:
                input_message = input("🔹 sql-operator> ").strip()
                if input_message.lower() in {"exit", "quit"}:
                    print("🛑 Exiting agent loop...")
                    break
                print(f"▶️ Running: {input_message}")
                response = await agent.run_async(input_message, max_steps=10)
                response.pretty_print()
            except KeyboardInterrupt:
                print("\n🛑 KeyboardInterrupt received. Exiting...")
                break


    finally:
        # Clean shutdown with full cancel error suppression
        try:
            await mcp_client.__aexit__(None, None, None)
        except get_cancelled_exc_class():
            print("⚠️ MCPClientStdio cancelled during adb_mcp_client shutdown.")


if __name__ == "__main__":
    asyncio.run(main())
