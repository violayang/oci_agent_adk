import os
from pathlib import Path
from dotenv import load_dotenv
from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.tool.prebuilt import CalculatorToolkit

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
AGENT_KB_ID = os.getenv("AGENT_KB_ID")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────


def agent_flow():

    client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region="us-chicago-1"
    )

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions="You perform calculations using tools provided.",
        tools=[CalculatorToolkit()]
    )

    agent.setup()
    return agent

def test_cases():

    agent = agent_flow()

    # First turn (here we start a new session)
    input = "What is the square root of 256?"
    response = agent.run(input, max_steps=3)
    print(response)
    response.pretty_print()

    # Second turn (here we use the same session from last run)
    input = "do the same thing for 81"
    response = agent.run(input, session_id=response.session_id, max_steps=3)
    response.pretty_print()

if __name__ == "__main__":
    test_cases()