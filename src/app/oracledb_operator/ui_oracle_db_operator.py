# sql_operator_app.py

import streamlit as st
import asyncio
from src.agents.oracledb_operator import start_sql_agent, run_sql_operator_once
from src.llm.oci_genai_agent import initialize_oci_genai_agent_service

st.set_page_config(page_title="Oracle DB Operator", layout="wide")
st.title("🛠️ Oracle SQLCL Operator via MCP")
st.markdown("Ask natural language questions to your Oracle DB using SQLcl MCP tool.")

# 🔧 Safe async wrapper for Streamlit thread
def run_async(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func(*args, **kwargs))

# ──────── Agent Initialization ────────
if "agent" not in st.session_state or "mcp_client" not in st.session_state:
    with st.spinner("🔌 Initializing Oracle SQLcl Agent..."):
        try:
            agent, mcp_client = run_async(start_sql_agent)
            st.session_state.agent = agent
            st.session_state.mcp_client = mcp_client
        except Exception as e:
            st.error(f"❌ MCP Tool init failed: {e}")
            st.stop()

# ──────── User Query Input ────────
user_input = st.text_area("Enter SQL-related query:", height=150)

if st.button("Run Query"):
    if user_input.strip():
        try:
            result = run_async(
                run_sql_operator_once,
                st.session_state.agent,
                user_input
            )
            st.markdown("### ✅ Response")
            st.markdown(result)
        except Exception as e:
            st.error(f"❌ Agent execution failed: {e}")