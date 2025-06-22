import asyncio

from mcp.client.session_group import StreamableHttpParameters
from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.mcp import MCPClientStreamableHttp

async def main():

    params = StreamableHttpParameters(
        url="http://localhost:8000/mcp",
    )

    async with MCPClientStreamableHttp(
        params=params,
        name="Streamable MCP Server",
    ) as mcp_client:

        client = AgentClient(
            auth_type="security_token",
            profile="DEFAULT",
            region="us-chicago-1"
        )

        agent = Agent(
            client=client,
            agent_endpoint_id="ocid1.genaiagentendpoint...",
            instructions="Use the tools to answer the questions.",
            tools=[await mcp_client.as_toolkit()],
        )

        agent.setup()

        # Should trigger the `add` tool
        input_message = "Add these numbers: 7 and 22."
        print(f"Running: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()

        # Should trigger the `get_secret_word` tool
        input_message = "What's the secret word?"
        print(f"\n\nRunning: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())