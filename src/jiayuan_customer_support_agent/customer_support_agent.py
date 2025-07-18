from typing import Dict, Any
from oci.addons.adk import Agent, AgentClient, tool
import os
from typing import Dict
from oci.addons.adk import Agent, AgentClient, tool
from pathlib import Path
from dotenv import load_dotenv
from src.tools.custom_function_tools import AccountToolkit
from oci.addons.adk.tool.prebuilt import AgenticRagTool

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
# print(PROJECT_ROOT)

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
AGENT_KB_ID = os.getenv("AGENT_KB_ID")
AGENT_REGION = os.getenv("AGENT_REGION")

#--------------------------------------------------
@tool
def get_weather(location: str) -> Dict[str, str]:
    """
    Get the weather for a given location.

    Args:
      location(str): The location for which weather is queried
    """
    return {"location": location, "temperature": 72, "unit": "F"}
#--------------------------------------------------




@tool
def write_email(customerEmail: str, subject: str, emailBodyContent: str) -> Dict[str, Any]:
    """function tool to write and send email to customer

    Args:
      customerEmail: The email for the customer who created a support ticket.
      subject: The email subject, would typically contain the subject and ID of the ticket discussed.
      emailBodyContent: The email main content, will contain the actual reply from the customer support agent.
    """

    return {"customerEmail": customerEmail, "subject": "Re: "+subject}



def main():
    client = AgentClient(
        auth_type="api_key",
        profile="frankfurt",
        region=AGENT_REGION
    )

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions="function tool to write and send email to customer",
        tools=[write_email]
    )

    agent.setup()

    input = "write an email to customer ID 12?"
    response = agent.run(input)

    response.pretty_print()

if __name__ == "__main__":
    main()

