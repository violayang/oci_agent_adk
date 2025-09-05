"""
create_sales_order.py
Author: Anup Ojah
Date: 2025-07-30
==========================
==Order Taking Assistant==
==========================
This module is an order-taking assistant designed to support sales workflows by extracting
customer order information from uploaded images and creates a sales order by posting data to APIs such as Fusion SCM
Workflow Overview:
1. Load config and credentials from .env
2. Register tools with the agent - create_sales_order, get_sales_order
3. Extract structured output from image_to_text to be able to create an order
4. Run the agent with user input and print response
"""

import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.toolkit.fusion_scm_order_toolkit import Fusion_SCM_Order_Toolkit
from src.tools.vision_instruct_tools import image_to_text
from src.prompt_engineering.topics.order_assistant import prompt_order_assistant
from src.common.fency_title import animate
from src.tools.dummy_email_tool import send_email_dummy
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

def agent_create_sales_order():

    # A shared client for all agents
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    instructions = prompt_order_assistant

    create_sales_order_agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            Fusion_SCM_Order_Toolkit(),
            image_to_text,
            send_email_dummy
        ]
    )

    create_sales_order_agent.setup()
    return create_sales_order_agent

def test_agents():

    agent_order = agent_create_sales_order()

    TITLE = "Sales Order Automation Agent"
    title = os.getenv("TITLE_TEXT", TITLE)
    dur = os.getenv("FANCY_DURATION", 5)
    fps = int(os.getenv("FANCY_FPS", "24"))
    duration = float(dur) if dur else None
    animate(title, fps=fps, duration=duration)
    
    saas_transaction_id = "R209_Sample_Order_ATOModel_209"

    payload = {
        "SourceTransactionNumber": saas_transaction_id,
        "SourceTransactionSystem": "OPS",
        "SourceTransactionId": saas_transaction_id,
        "TransactionalCurrencyCode": "USD",
        "BusinessUnitId": 300000046987012,
        "BuyingPartyNumber": "10060",
        #"TransactionTypeCode": "STD",
        "RequestedShipDate": "2018-09-19T19:51:48+00:00",
        "SubmittedFlag": 'true',
        "FreezePriceFlag": 'false',
        "FreezeShippingChargeFlag": 'false',
        "FreezeTaxFlag": 'false',
        "RequestingBusinessUnitId": 300000046987012,
        # "billToCustomer": [{
        #     "CustomerAccountId": 10060,
        #     "SiteUseId": 300000047368662
        # }],
        # "shipToCustomer": [{
        #     "PartyId": 10060,
        #     "SiteId": 300000047368662
        # }],
        "lines": [{
            "SourceTransactionLineId": "1",
            "SourceTransactionLineNumber": "1",
            "SourceScheduleNumber": "1",
            "SourceTransactionScheduleId": "1",
            "OrderedUOMCode": "zzu",
            "OrderedQuantity": 1,
            "ProductNumber": "AS6647431",
            "FOBPoint": "Destination",
            "FreightTerms": "Add freight",
            "PaymentTerms": "30 Net",
            "ShipmentPriority": "High"
            # "RequestedFulfillmentOrganizationId": 204
        },
        {
            "SourceTransactionLineId": "2",
            "SourceTransactionLineNumber": "2",
            "SourceScheduleNumber": "1",
            "SourceTransactionScheduleId": "1",
            "OrderedUOMCode": "zzu",
            "OrderedQuantity": 1,
            "ProductNumber": "AS6647432",
            "FOBPoint": "Destination",
            "FreightTerms": "Add freight",
            "PaymentTerms": "30 Net",
            "ShipmentPriority": "High"
            #"ParentSourceTransactionLineId": "1"
            # "RequestedFulfillmentOrganizationId": 204
        },
        {
            "SourceTransactionLineId": "3",
            "SourceTransactionLineNumber": "3",
            "SourceScheduleNumber": "1",
            "SourceTransactionScheduleId": "1",
            "OrderedUOMCode": "zzu",
            "OrderedQuantity": 1,
            "ProductNumber": "AS6647433",
            "FOBPoint": "Destination",
            "FreightTerms": "Add freight",
            "PaymentTerms": "30 Net",
            "ShipmentPriority": "High"
            #"ParentSourceTransactionLineId": "1"
            # "RequestedFulfillmentOrganizationId": 204
        }
        ]
    }

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = """
Get all information about the order.
"""
    # Read Order
    input_prompt = image_path + "   " + question
    response = agent_order.run(input_prompt, max_steps=4)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    print()
    print()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    # Create Order
    input_prompt = f"Create a sales order in Oracle SCM using a properly structured JSON payload.: /n   {payload}"
    response = agent_order.run(input_prompt, max_steps=4)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    print()
    print()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    # Get Order
    input_prompt = "get sales order for orderid : " + str(saas_transaction_id)
    response = agent_order.run(input_prompt, max_steps=4)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    print()
    print()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    email_string = f"Send an email to ops@example.com: subject: Sales Order Created for orderid : {saas_transaction_id}, body: {final_message}"
    response_email = agent_order.run(email_string)
    final_message_email = response_email.data["message"]["content"]["text"]
    print(final_message_email)

    # import json
    # from src.tools.dummy_email_tool import send_email_dummy

    # res_json = send_email_dummy.invoke({
    #     "to": ["ops@example.com"],
    #     "subject": f"Sales Order Created for orderid : {saas_transaction_id}",
    #     "body": str(final_message),
    # })
    # print(res_json)  # summary only

    # res = json.loads(res_json)
    # with open(res["saved_path"]) as f:
    #     record = json.load(f)

    # print("=== BODY FROM OUTBOX RECORD ===")
    # print(record["email"]["body"])


    print()
    print()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    test_agents()