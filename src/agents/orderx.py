import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.tools.vision_instruct_tools import image_to_text

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
AGENT_REGION = os.getenv("AGENT_REGION")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

def agent_flow():

    client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region=AGENT_REGION
    )

    instructions = """
    You are order taking assistant.
    You have tools to take an order as an image and process it by converting the image to text.
    """

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            image_to_text
        ]
    )

    agent.setup()

    return agent

def test_cases():
    from pathlib import Path

    THIS_DIR = Path(__file__).resolve()
    PROJECT_ROOT = THIS_DIR.parent.parent.parent

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = "/n What is the ship to address"

    input_prompt = image_path + "   " + question
    agent = agent_flow()

    # Handle the first user turn of the conversation
    #client_provided_context = image_path
    #input = client_provided_context + " " + question

    response = agent.run(input_prompt)

    final_message = response.data["message"]["content"]["text"]
    print(final_message)

if __name__ == '__main__':
    test_cases()
