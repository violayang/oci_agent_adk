#%% md
## Setup Tool - OCI RAG AGENT SERVICE
#The OCI RAG Agent Service is a pre-built service from Oracle cloud, that is designed to perform multi-modal
# augmented search against any pdf (with embedded tables and charts) or txt files.

import oci,os
from langchain_core.tools import tool
from oci.generative_ai_agent_runtime import GenerativeAiAgentRuntimeClient
from oci.generative_ai_agent_runtime.models import CreateSessionDetails

from dotenv import load_dotenv
from pathlib import Path

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / ".env")

# Set up the OCI GenAI Agents endpoint configuration
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")

config = oci.config.from_file(profile_name="DEFAULT")  # Update this with your own profile name
sess_id = ""


def initialize_oci_genai_agent_service():
    """Initialize OCI GenAI Agent Service and create a session"""

    # Initialize service client with default config file
    generative_ai_agent_runtime_client = oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient(
        config,
        service_endpoint=AGENT_SERVICE_EP)

    # Create Session
    create_session_response = generative_ai_agent_runtime_client.create_session(
        create_session_details=oci.generative_ai_agent_runtime.models.CreateSessionDetails(
            display_name="USER_Session",
            description="User Session"),
        agent_endpoint_id=AGENT_EP_ID)

    sess_id = create_session_response.data.id

    # print("generative_ai_agent_runtime_client :" + str(generative_ai_agent_runtime_client))
    # print(sess_id)

    return generative_ai_agent_runtime_client, sess_id  # Return both client and session ID


# Response Generator
@tool
def rag_agent_service(inp: str):
    """RAG AGENT"""
    #inp = state["messages"][-1].content
    generative_ai_agent_runtime_client, sess_id = initialize_oci_genai_agent_service()
    response = generative_ai_agent_runtime_client.chat(
        agent_endpoint_id=AGENT_EP_ID,
        chat_details=oci.generative_ai_agent_runtime.models.ChatDetails(
            user_message=inp,
            session_id=sess_id))

    # print(str(response.data))
    response = response.data.message.content.text
    return response

# Test Cases -
def test_case():
    answer = rag_agent_service.invoke("how to create a good recipe")
    print(answer)

if __name__ == "__main__":
    test_case()


