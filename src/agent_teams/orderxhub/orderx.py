import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
#from src.tools.custom_functions.pdf_to_image import convert_pdf_to_png_t
from src.tools.vision_instruct_tools import image_to_text
from src.toolkit.fusion_scm_order_toolkit import Fusion_SCM_Order_Toolkit
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

    # instructions = """
    # You are order taking assistant.
    # You have tools to take an order as a pdf and store it into a tmp folder.
    # """
    #
    # agent_pdf = Agent(
    #     client=client,
    #     agent_endpoint_id=AGENT_EP_ID,
    #     instructions=instructions,
    #     tools=[
    #         convert_pdf_to_png
    #     ]
    # )
    #
    # agent_pdf.setup()

    # instructions = """
    #     You are order taking assistant.
    #     You have tools to take an order as an image and process it by converting the image to text.
    #     """
    #
    # agent_image = Agent(
    #     client=client,
    #     agent_endpoint_id=AGENT_EP_ID,
    #     instructions=instructions,
    #     tools=[
    #         image_to_text
    #     ]
    # )


    instructions = """
            You are order taking assistant.
            You have tools to create order by invoking an External REST API. You also have the ability to list orders by invoking an External REST AP.
            """
    agent_order = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            Fusion_SCM_Order_Toolkit(),
        ]
    )

    #agent_image.setup()
    agent = agent_order.setup()


    return agent

def test_cases():
    # from pathlib import Path
    #
    # THIS_DIR = Path(__file__).resolve()
    # PROJECT_ROOT = THIS_DIR.parent.parent.parent.parent
    #
    # image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    # question = "/n What is the ship to address"
    #
    # input_prompt = image_path + "   " + question
    agent_create_order = agent_flow()

    # Handle the first user turn of the conversation
    #client_provided_context = image_path
    #input = client_provided_context + " " + question
    payload = {
        "SourceTransactionNumber": "ORDERX_Standard_Item_02",
        "SourceTransactionSystem": "GPR",
        "SourceTransactionId": "ORDERX_Standard_Item_02",
        "BusinessUnitName": "Vision Operations",
        "BuyingPartyName": "Computer Service and Rentals",
        "TransactionType": "Standard Orders",
        "RequestedShipDate": "2019-10-19T20:49:12+00:00",
        "RequestedFulfillmentOrganizationName": "Vision Operations",
        "PaymentTerms": "30 Net",
        "TransactionalCurrencyName": "US Dollar",
        "RequestingBusinessUnitName": "Vision Operations",
        "FreezePriceFlag": False,
        "FreezeShippingChargeFlag": False,
        "FreezeTaxFlag": False,
        "SubmittedFlag": True,
        "SourceTransactionRevisionNumber": 1,
        "billToCustomer": [{
            "PartyName": "Computer Service and Rentals",
            "AccountNumber": "1006",
            "Address1": "301 Summit Hill Drive",
            "City": "CHATTANOOGA",
            "State": "TN",
            "PostalCode": "37401",
            "County": "Hamilton",
            "Province": None,
            "Country": "US"
        }],
        "shipToCustomer": [{
            "PartyName": "Vision Corporation",
            "PartyId": 1002,
            "PartyNumber": "1002",
            "ContactId": 5801,
            "ContactNumber": "8623",
            "ContactName": "Henry Smith",
            "ContactFirstName": "Henry",
            "ContactLastName": "Smith",
            "SiteId": 21765,
            "Address1": "4598 Cherry Lane",
            "City": "BUFFALO",
            "County": "ERIE",
            "PostalCode": "14201",
            "Country": "US"
        }],
        "lines": [{
            "SourceTransactionLineId": "10",
            "SourceTransactionLineNumber": "10",
            "SourceTransactionScheduleId": "10",
            "SourceScheduleNumber": "10",
            "TransactionCategoryCode": "ORDER",
            "TransactionLineType": "Buy",
            "ProductNumber": "AS92888",
            "OrderedQuantity": 5,
            "OrderedUOM": "Each"
        }]
    }

    input_prompt = f"Create a sales order in Oracle SCM using a properly structured JSON payload.: /n   {payload}"
    response = agent_create_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

    input_prompt = "get sales order with query string for api call as : finder=findBySourceOrderNumberAndSystem;SourceTransactionNumber=404087,SourceTransactionSystem=GPR"
    response = agent_create_order.run(input_prompt)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)

if __name__ == '__main__':
    test_cases()