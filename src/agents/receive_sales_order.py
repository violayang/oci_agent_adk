"""
receive_sales_order.py
Author: Anup Ojah
Date: 2025-07-18
==========================
==Order Taking Assistant==
==========================
This module is an order-taking assistant designed to support sales workflows by extracting
customer order information from uploaded images and interacting with external order APIs such as Fusion SCM
Workflow Overview:
1. Load config and credentials from .env
2. Register tools with the agent - image_to_text, create_sales_order, get_sales_order
3. Extract structured output from image_to_text to be able to create and order
4. Run the agent with user input and print response
"""

import os, json
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.toolkit.fusion_scm_order_toolkit import Fusion_SCM_Order_Toolkit
from src.tools.vision_instruct_tools import image_to_text
from src.prompt_engineering.topics.order_assistant import prompt_order_assistant

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
AGENT_REGION = os.getenv("AGENT_REGION")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

def agent_flow_order():

    # A shared client for all agents
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    #instructions = prompt_order_assistant
    instructions = """
 You are a pass-through agent.

Your sole responsibility is to execute the requested tool and return its raw output exactly as-is.

Do not rephrase, summarize, analyze, or interpret the tool response in any way.

If the tool returns a JSON object, your final response must be the exact same JSON — unmodified and unwrapped. Do not add commentary, context, or explanations.

"""

    agent_order = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            image_to_text
        ]
    )


    agent_order.setup()
    return agent_order

def agent_setup():

    agent_order = agent_flow_order()

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = """Get all information about the order such as - 
BillToCustomer : {}
ShipToCustomer: {}}
- Item: {}, Quantity: {}, Requested Date: {}"""
    # Read Order
    input_prompt = image_path + "   " + question
    response = agent_order.run(input_prompt, max_steps=1)
    print(response.data)
    #final_message = response.data["message"]["content"]["text"]
    #print(final_message)



if __name__ == '__main__':
    agent_setup()