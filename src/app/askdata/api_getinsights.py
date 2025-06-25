#%% md
## Setup Tool - OCI RAG AGENT SERVICE
#The OCI RAG Agent Service is a pre-built service from Oracle cloud, that is designed to perform multi-modal
# augmented search against any pdf (with embedded tables and charts) or txt files.

import oci
import os
import re
from oci.generative_ai_agent_runtime import GenerativeAiAgentRuntimeClient
from oci.generative_ai_agent_runtime.models import CreateSessionDetails
from src.llm.oci_genai_agent import initialize_oci_genai_agent_service, extract_final_answer_from_chat_result

from dotenv import load_dotenv
from pathlib import Path

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / "config/.env")
# Set up the OCI GenAI Agents endpoint configuration
AGENT_EP_ID = os.getenv("AGENT_EP_ID")

def getinsights_agent_orchestrator(inp: str):
    """AGENT Orchestrator"""
    #inp = state["messages"][-1].content
    generative_ai_agent_runtime_client, sess_id = initialize_oci_genai_agent_service()
    response = generative_ai_agent_runtime_client.chat(
        agent_endpoint_id=AGENT_EP_ID,
        chat_details=oci.generative_ai_agent_runtime.models.ChatDetails(
            user_message=inp,
            session_id=sess_id))

    return response

# Test Cases -
def test_case():
    response = getinsights_agent_orchestrator("which Invoice I should pay first based criteria such as highest amount due and highest past due date for 'session:e5f6a932-6123-4a04-98e9-6b829904d27f'")
    print(response.data)
    final_answer = extract_final_answer_from_chat_result(response)
    print("Final Answer:", final_answer)


if __name__ == "__main__":
    test_case()


