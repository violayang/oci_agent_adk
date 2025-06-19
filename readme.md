### Configuring and running the agent
python3.13 -m venv .venv
source .venv/bin/activate
python3.13 -m pip install -r requirements.txt

### Installing the ADK
# After you create a project and a virtual environment, install the latest version of ADK:
#requirements.txt
pip install --upgrade "oci[adk]@https://artifactory.oci.oraclecorp.com:443/opc-public-sdk-dev-pypi-local/oci-2.154.1+preview.1.228-py3-none-any.whl"


### Authenticating your ADK app to OCI
# The ADK provides an AgentClient class to simplify handling authentication and management of agent resources. Four authentication types are supported:

### API Key Authentication (Default)
# API key authentication is the default and most common method for authenticating with OCI services.

from oci.addons.adk import AgentClient

client = AgentClient(
    auth_type="api_key",
    profile="DEFAULT",
    region="<your-region>"  # OCI region such as "us-chicago-1" or airport code such as "ORD"
)

### Configuring and running an agent - Quick Test

python3.13 -m src.examples.test_setup  


