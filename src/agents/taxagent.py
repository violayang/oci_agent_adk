"""
taxagent.py
Author: Anup Ojah
Date: 2025-07-18
==========================
==Tax Auditor Assistant==
==========================
This module is a specialized assistant designed to audit and explain tax amounts applied to business transactions
Workflow Overview:
1. Load config and credentials from .env
2. Register tools with the agent - AgenticRagTool, SQL Tool
3. Run the agent with user input and print response
"""

import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.toolkit.user_info import AccountToolkit
from oci.addons.adk.tool.prebuilt import AgenticRagTool
from src.prompt_engineering.topics.tax_auditor import prompt_Agent_Auditor
import logging

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
logging.getLogger('adk').setLevel(logging.DEBUG)

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")
OCI_PROFILE = os.getenv("OCI_PROFILE")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
TAX_AGENT_KB_ME_ID = os.getenv("TAX_AGENT_KB_ME_ID")
TAX_AGENT_KB_BUS_ID = os.getenv("TAX_AGENT_KB_BUS_ID")
AGENT_REGION = os.getenv("AGENT_REGION")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

def agent_flow():

    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    instructions = prompt_Agent_Auditor # Assign the right topic
    custom_instructions = (f"The RAG Tool with Tax knowledge about Meals and Entertaintment can be found under the knowledge base at {TAX_AGENT_KB_ME_ID} and Tax knowledge about Business can be found under the knowledge base at {TAX_AGENT_KB_BUS_ID} ")
    # custom_instructions = (
    #     f"response with not more than 10 words. Hide any PHI information from sending back to the user")

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            AgenticRagTool(knowledge_base_ids=[TAX_AGENT_KB_ME_ID], description=custom_instructions),
            AccountToolkit()
        ]
    )

    return agent


def setup_agent():

    agent = agent_flow()
    agent.setup()

    # This is a context your existing code is best at producing (e.g., fetching the authenticated user id)
    client_provided_context = "[Context: The logged in user ID is: user_123] "

    # Handle the first user turn of the conversation
    input = "Get user information for user logged in."
    input = client_provided_context + " " + input
    response = agent.run(input)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)
    # print(response.raw_data['message']['content']['text'])
    # response.pretty_print()

    # Handle the second user turn of the conversation
    input = "Get more information about the organization he/she works for."
    input = client_provided_context + " " + input
    response = agent.run(input, session_id=response.session_id)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    # Call the RAG Service
    input = "“Is a $500 client lunch at steakhouse deductible?”"
    response = agent.run(input, session_id=response.session_id)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)


if __name__ == "__main__":
    setup_agent()