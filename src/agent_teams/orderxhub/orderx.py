import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.agents.agent_image2text import agent_flow
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

    client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region=AGENT_REGION
    )

    instructions = """
            You are order taking assistant. Don't make any decision of your own and simply follow the prompr to execute the right tool.
            Use the tool 'create_sales_order' to create sales order by invoking an External REST API.
            Use the tool 'get_sales_order' to get sales order by invoking an External REST API.
            """
    agent_order = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            Fusion_SCM_Order_Toolkit(),
        ]
    )

    agent_order.setup()
    return agent_order

def agent_setup():

    agent_order = agent_flow_order()


    payload = {
        "SourceTransactionNumber": "R13_Sample_Order_ATOModel_02",
        "SourceTransactionSystem": "GPR",
        "SourceTransactionId": "R13_Sample_Order_ATOModel_02",
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

    input_prompt = f"Create a sales order in Oracle SCM using a properly structured JSON payload.: /n   {payload}"
    response = agent_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    input_prompt = "get sales order with query string for api call as : finder=findBySourceOrderNumberAndSystem;SourceTransactionNumber=R13_Sample_Order_ATOModel_03,SourceTransactionSystem=GPR"
    response = agent_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

if __name__ == '__main__':
    agent_setup()