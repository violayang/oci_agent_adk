"""
orderx_hub.py
Author: Anup Ojah
Date: 2025-07-30
==========================
==Order Taking Supervisor Assistant==
==========================
This module is an order-taking supervisor assistant that can be used by a customers
to submit their sales orders through phone, email, handwritten notes or chat messages.
The agent will apply it's multi-modal tool capability, extract the required informaiton
to create an order in Fusion SCM

Workflow Overview:
1. Load config and credentials from .env
2. Register two sub agents to the supervisor - receive_sales_order and create_sales_order
3. Extract structured output from source, create an order, and send an email with the confirmed order to the sales agent
4. Run the agent with user input and print response
"""

import os
import logging
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.agents.receive_sales_order import agent_receive_sales_order
from src.agents.create_sales_order import agent_create_sales_order
from src.prompt_engineering.topics.order_assistant import prompt_order_assistant

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
AGENT_KB_ID = os.getenv("AGENT_KB_ID")
AGENT_REGION = os.getenv("AGENT_REGION")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

def agent_flow_order():

    # Create a client with your authentication details
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    ## Receive Sales Order Agent
    instructions = prompt_order_assistant
    _agent_receive_sales_order = agent_receive_sales_order()
    _agent_create_sales_order = agent_create_sales_order()
    agent_order = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            _agent_receive_sales_order.as_tool(
                tool_name="agent_receive_sales_order",
                tool_description="order-taking assistant designed to support sales workflows by extracting customer order information from uploaded images",
            ),
            # _agent_create_sales_order.as_tool(
            #     tool_name="agent_create_sales_order",
            #     tool_description="create order assistant designed to create a sales order by posting data to APIs such as Fusion SCM",
            # ),
        ]
    )

    return agent_order

def agent_setup():

    agent_order = agent_flow_order()
    agent_order.setup()

    payload = {
        "SourceTransactionNumber": "R13_Sample_Order_ATOModel_22",
        "SourceTransactionSystem": "GPR",
        "SourceTransactionId": "R13_Sample_Order_ATOModel_22",
        "TransactionalCurrencyCode": "USD",
        "BusinessUnitId": 204,
        "BuyingPartyNumber": "1006",
        "TransactionTypeCode": "STD",
        "RequestedShipDate": "2018-09-19T19:51:48+00:00",
        "SubmittedFlag": 'true',
        "FreezePriceFlag": 'false',
        "FreezeShippingChargeFlag": 'false',
        "FreezeTaxFlag": 'false',
        "RequestingBusinessUnitId": 204,
        "billToCustomer": [{
            "CustomerAccountId": 1006,
            "SiteUseId": 1025
        }],
        "shipToCustomer": [{
            "PartyId": 1006,
            "SiteId": 1036
        }],
        "lines": [{
            "SourceTransactionLineId": "1",
            "SourceTransactionLineNumber": "1",
            "SourceScheduleNumber": "1",
            "SourceTransactionScheduleId": "1",
            "OrderedUOMCode": "Ea",
            "OrderedQuantity": 1,
            "ProductNumber": "STOVE_ATO_MODEL",
            "FOBPoint": "Destination",
            "FreightTerms": "Add freight",
            "PaymentTerms": "30 Net",
            "ShipmentPriority": "High",
            "RequestedFulfillmentOrganizationId": 204
        },
            {
                "SourceTransactionLineId": "2",
                "SourceTransactionLineNumber": "2",
                "SourceScheduleNumber": "1",
                "SourceTransactionScheduleId": "1",
                "OrderedUOMCode": "Ea",
                "OrderedQuantity": 1,
                "ProductNumber": "GAS_FUEL",
                "FOBPoint": "Destination",
                "FreightTerms": "Add freight",
                "PaymentTerms": "30 Net",
                "ShipmentPriority": "High",
                "RequestedFulfillmentOrganizationId": 204,
                "ParentSourceTransactionLineId": "1"
            },
            {
                "SourceTransactionLineId": "3",
                "SourceTransactionLineNumber": "3",
                "SourceScheduleNumber": "1",
                "SourceTransactionScheduleId": "1",
                "OrderedUOMCode": "Ea",
                "OrderedQuantity": 1,
                "ProductNumber": "Burner_4_GRID",
                "PurchasingUOMCode": "Ea",
                "FOBPoint": "Destination",
                "FreightTerms": "Add freight",
                "PaymentTerms": "30 Net",
                "ShipmentPriority": "High",
                "FOBPointCode": "Destination",
                "RequestedFulfillmentOrganizationId": 204,
                "ParentSourceTransactionLineId": "1"
            }
        ]
    }

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = """
Get all information about the order.
"""
    # Read Order
    input_prompt = image_path + "   " + question
    response = agent_order.run(input_prompt, max_steps=10)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)
    #
    # # Create Order
    # input_prompt = f"Create a sales order in Oracle SCM using a properly structured JSON payload.: /n   {payload}"
    # response = agent_order.run(input_prompt)
    # final_message = response.data["message"]["content"]["text"]
    # print(final_message)

    # # Get Order
    # input_prompt = "get sales order for orderid : GPR:R13_Sample_Order_ATOModel_22"
    # response = agent_order.run(input_prompt)
    # final_message = response.data["message"]["content"]["text"]
    # print(final_message)

if __name__ == '__main__':
    agent_setup()