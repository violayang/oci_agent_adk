# Agent Orchestrator (Streaming + LangGraph-style Diagram, No python-graphviz)

## Run
python3.13 -m venv .venv_client_app

source .venv_client_app/bin/activate   

python3.13 -m pip install -r requirements.txt  

streamlit run app.py --server.address 0.0.0.0 --server.port 8505   