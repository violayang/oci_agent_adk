# Agent Orchestrator

## Run
python3.13 -m venv .venv_client_app

source .venv_client_app/bin/activate   

python3.13 -m pip install -r requirements.txt  

#### start fastapi server
python3 -m uvicorn src.app.orderxhub.fastapi_orderx:app --host 0.0.0.0 --port 8084 --reload | tee fastapi.log

#### start streamlit application
streamlit run src/app/orderxhub/app.py --server.address 0.0.0.0 --server.port 8080 2>&1 | tee streamlit.log