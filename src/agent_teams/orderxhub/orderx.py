import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.agents.agent_image2text import agent_flow_image2text
from src.toolkit.fusion_scm_order_toolkit import Fusion_SCM_Order_Toolkit
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

def agent_flow_order():

    # A shared client for all agents
    client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region=AGENT_REGION
    )

    instructions = """
                You are order taking assistant. Don't make any decision of your own and simply follow the prompt to execute the right tool.
                Use the too 'image_to_text' to convert an image to text. When using this tool, please extract 
                    ***Customer Name***, ***Contact*** ***Address***, ***Item***, ***Quantity and ***Date***
                Use the tool 'create_sales_order' to create sales order by invoking an External REST API. When using this tool, please add the following to the final answer:
                    Your Order has been processed correctly and OrderNumber created is {OrderNumber}.
                Use the tool 'get_sales_order' to get sales order by invoking an External REST API.
                """
    agent_order = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            Fusion_SCM_Order_Toolkit(), image_to_text
        ]
    )


    agent_order.setup()
    return agent_order

def agent_setup():

    agent_order = agent_flow_order()


    payload = {
        "SourceTransactionNumber": "R13_Sample_Order_ATOModel_13",
        "SourceTransactionSystem": "GPR",
        "SourceTransactionId": "R13_Sample_Order_ATOModel_13",
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

    from pathlib import Path

    THIS_DIR = Path(__file__).resolve()
    PROJECT_ROOT = THIS_DIR.parent.parent.parent.parent

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = "/n Get all the order details from the uploaded image. Format the response using a JSON schema. Tempe = Tampa"
    # Read Order
    input_prompt = image_path + "   " + question
    response = agent_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    # Create Order
    input_prompt = f"Create a sales order in Oracle SCM using a properly structured JSON payload.: /n   {payload}"
    response = agent_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    # Get Order
    input_prompt = "get sales order for orderid : GPR:R13_Sample_Order_ATOModel_11"
    response = agent_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

if __name__ == '__main__':
    agent_setup()