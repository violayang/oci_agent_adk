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

class Fusion_SCM_Order_Toolkit(Toolkit):

    @tool
    def create_sales_order(self, payload: dict) -> str:
        """
        You are a tools to create sales order by invoking an External REST API.
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


            print(payload)
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

    @tool
    def get_sales_order(self, orderid: str) -> str:
        """
        You are a tools to get sales order by invoking an External REST API.
        :param query:
        :return:
        """
        try:

            """
            curl -u username:password "https://servername/fscmRestApi/resources/version/salesOrdersForOrderHub"
            """

            query_string = f"finder=findBySourceOrderNumberAndSystem;SourceTransactionNumber={orderid},SourceTransactionSystem=OPS"
            resource = f"?{query_string}"
            print(resource)
            response = requests.get(
                API_URL + resource,
                auth=(API_USER, API_PASS),
            )

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            response.raise_for_status()
            return f"Response: {json.dumps(response.json(), indent=4)}"

        except requests.exceptions.RequestException as e:
            return f"API call failed: {str(e)}"
        
    # @tool
    # def get_order_number(self, order_key: str) -> str:
    #     """
    #     You are a tools to fetch one sales order using order_key by invoking an External REST API.
    #     :param query:
    #     :return:
    #     """
    #     try:

    #         """
    #         curl -u username:password "https://servername/fscmRestApi/resources/version/salesOrdersForOrderHub"
    #         """
    #         response = requests.get(
    #             API_URL + "?q=OrderNumber=" + order_key,
    #             auth=(API_USER, API_PASS),
    #         )

    #         print("Status Code:", response.status_code)
    #         print("Response Text:", response.text)

    #         response.raise_for_status()
    #         return f"Response: {json.dumps(response.json(), indent=4)}"

    #     except requests.exceptions.RequestException as e:
    #         return f"API call failed: {str(e)}"

def test_case_create_sales_order():
    payload = {
        "SourceTransactionNumber": "97414",
        "SourceTransactionSystem": "OPS",
        "SourceTransactionId": "97414",
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
            "OrderedQuantity": 10,
            "ProductNumber": "AS7751100",
            "FOBPoint": "Destination",
            "FreightTerms": "Add freight",
            "PaymentTerms": "30 Net",
            "ShipmentPriority": "High"
            # "RequestedFulfillmentOrganizationId": 204
        }
        ]
    }

    toolkit = Fusion_SCM_Order_Toolkit()
    toolkit.create_sales_order(payload)

def test_get_sales_order():
    #order_string = "finder=findBySourceOrderNumberAndSystem;SourceTransactionNumber=97414,SourceTransactionSystem=OPS"
    order_string = "97414"
    
    toolkit = Fusion_SCM_Order_Toolkit()
    toolkit.get_sales_order(order_string)

# def test_get_order_number():
#     order_string = "98483"
#     toolkit = Fusion_SCM_Order_Toolkit()
#     toolkit.get_order_number(order_string)


# if __name__ == "__main__":
#     #test_case_create_sales_order()
#     #test_get_sales_order()