### Configure your development environment

>>> 
> 
### Configuring and running the agent
>> python3.13 -m venv .venv
> 
>> source .venv/bin/activate
> 
>> python3.13 -m pip install -r requirements.txt

### Installing all the required packages
#### After you create a project and a virtual environment, install the latest version of required packages:

>> python3.13 -m pip install -r requirements.txt

### Authenticating your ADK app to OCI
#### The ADK provides an AgentClient class to simplify handling authentication and management of agent resources. Four authentication types are supported:

### API Key Authentication (Default)
#### API key authentication is the default and most common method for authenticating with OCI services.

from oci.addons.adk import AgentClient

client = AgentClient(
    auth_type="api_key",
    profile="DEFAULT",
    region="<your-region>"  # OCI region such as "us-chicago-1" or airport code such as "ORD"
)

### Configuring and running an agent - Quick Test

>> python3.13 -m src.examples.test_setup  

### Best practices to follow while building an agent. Below, you will see how to build an agent called 'taxagent' that has 2 tools - RAG Tool and a CustomFunction
![config/img.png](config/img.png)

#### Step 1: Build the tools required.

>> CustomFunction --> src/tools/custom_function_tools.py
> 
>> RAG Tool --> oci.addons.adk.tool.prebuilt import AgenticRagTool

#### Step 2: Build/Deploy the Agent - taxagent to GenAI Agent Service to manage deployment

>> python3.13 -m src.agents.taxagent

#### Step 3: Run/Test the API that will invoke the Agents deployed through GenAI Agent Service (remote)

>>  python3.13 -m src.llm.api_genai_agent 

#### Step 4: Run a streamilt app to execute the agent

>> python3.13 -m streamlit run src/app/tax_assistant/ui_taxagent.py

sample prompt : get tax m&e adjustment for entity 1000


