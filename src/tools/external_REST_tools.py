# Connect to any service to integrate any data and functionality with a public REST interface
import requests, os
import json
from oci.addons.adk import Toolkit, tool
from pathlib import Path
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
API_USER = os.getenv("FUSION_SCM_API_USER")
API_PASS = os.getenv("FUSION_SCM_API_PASS")
API_URL = os.getenv("FUSION_SCM_API_URL")

@tool
def create_order(payload: dict) -> str:
    """
    You are a tools to create order by invoking an External REST API.
    :param query:
    :return:
    """
    try:

        headers = {
            "Content-Type": "application/vnd.oracle.adf.resourceitem+json",
            "Accept": "application/vnd.oracle.adf.resourceitem+json"
        }

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        response = requests.post(
            API_URL,
            auth=(API_USER, API_PASS),
            headers=headers,
            data=payload  # ✅ Correctly serialized JSON
        )

        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

        response.raise_for_status()
        return f"Response: {json.dumps(response.json(), indent=4)}"

    except requests.exceptions.RequestException as e:
        return f"API call failed: {str(e)}"

def test_case():
    payload = {
        "SourceTransactionNumber": "ORDERX_Standard_Item_02",
        "SourceTransactionSystem": "GPR",
        "SourceTransactionId": "ORDERX_Standard_Item_02",
        "BusinessUnitName": "Vision Operations",
        "BuyingPartyName": "Computer Service and Rentals",
        #"BuyingPartyContactName": "Brian Smith",
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

    create_order(payload)

if __name__ == "__main__":
    test_case()