# Agent Orchestrator (Streaming + LangGraph-style Diagram, No python-graphviz)

## Run
```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

- Top diagram updates live (DOT rendered by Streamlit internally). No python `graphviz` package needed.
- Streaming logs update in-place as each tool executes.
