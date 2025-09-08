"""
oracledb_operator.py
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
from src.llm.oci_genai_agent import initialize_oci_genai_agent_service
from src.prompt_engineering.topics.oracle_db_operator import promt_oracle_db_operator

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

    instructions = promt_oracle_db_operator

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            await adb_mcp_client.as_toolkit(),
        ],
    )

    agent.setup()

    return agent, adb_mcp_client  # return both to close later

async def run_sql_operator_once(agent, user_input: str):
    """
    Executes a single input with the initialized agent and returns the pretty-printed response.
    """
    print(f"▶️ Sending input: {user_input}")
    response = await agent.run_async(user_input.strip(), max_steps=10)
    print("✅ Agent responded.")
    return response.pretty()



async def main(session_id: str):
    agent, mcp_client = await start_sql_agent()

    try:
        while True:
            try:
                input_message = input("🔹 sql-operator> ").strip()
                if input_message.lower() in {"exit", "quit"}:
                    print("🛑 Exiting agent loop...")
                    break
                print(f"▶️ Running: {input_message}")
                if (session_id == ""):
                    response = await agent.run_async(input_message, max_steps=10)
                else:
                    response = await agent.run_async(input_message,  max_steps=10)  # working on a bug with session_id

                session_id = response.session_id  # <-- global variable is now updated
                print(f"Session ID: {session_id}")
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
    generative_ai_agent_runtime_client, session_id = initialize_oci_genai_agent_service()
    asyncio.run(main(session_id))
