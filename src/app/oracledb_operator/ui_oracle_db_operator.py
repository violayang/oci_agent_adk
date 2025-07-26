import asyncio
import streamlit as st
from anyio import get_cancelled_exc_class  # Assuming this is needed from your code
from src.agents.oracledb_operator import start_sql_agent

# Helper to run async functions synchronously in Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # No current event loop in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If loop is already running (e.g., in some environments), use nested asyncio
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return loop.run_until_complete(coro)

# Streamlit app configuration
st.set_page_config(page_title="Oracle Database Operator", page_icon="🔹", layout="wide")
st.title("🔹 Oracle Database Operator")
st.markdown("""
This app allows natural language conversations with an Oracle Database (19c or higher) via SQLcl MCP Server.  
Enter your query below and interact with the agent.  
For more details, see the [documentation](https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/using-oracle-sqlcl-mcp-server.html).
""")

# Initialize session state for agent, client, and chat history
if "agent" not in st.session_state:
    st.session_state.agent = None
    st.session_state.mcp_client = None
    st.session_state.messages = []  # List of dicts: {"role": "user" or "assistant", "content": str}
    st.session_state.initialized = False

# Function to initialize agent (runs only once)
def initialize_agent():
    if not st.session_state.initialized:
        with st.spinner("Initializing Oracle DB Agent... This may take a moment."):
            try:
                agent, mcp_client = run_async(start_sql_agent())
                st.session_state.agent = agent
                st.session_state.mcp_client = mcp_client
                st.session_state.initialized = True
                st.success("Agent initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()  # Halt app if initialization fails

# Shutdown function
def shutdown_agent():
    if st.session_state.mcp_client:
        with st.spinner("Shutting down agent..."):
            try:
                run_async(st.session_state.mcp_client.__aexit__(None, None, None))
                st.session_state.agent = None
                st.session_state.mcp_client = None
                st.session_state.initialized = False
                st.session_state.messages = []  # Clear history
                st.success("Agent shut down successfully. Refresh the page to restart.")
            except get_cancelled_exc_class():
                st.warning("MCPClientStdio cancelled during shutdown.")
            except Exception as e:
                st.error(f"Error during shutdown: {e}")

# Initialize on first run
initialize_agent()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Enter your query (e.g., 'Show me the top 5 employees') or type 'exit' to quit:")

if user_input:
    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if user_input.lower() in {"exit", "quit"}:
        st.info("🛑 Exiting agent loop...")
        shutdown_agent()
    else:
        # Run the agent asynchronously
        with st.chat_message("assistant"):
            with st.spinner("▶️ Processing query..."):
                try:
                    response = run_async(st.session_state.agent.run_async(user_input, max_steps=10))
                    # Display response (assuming response has pretty_print; adapt if needed)
                    response_content = response.pretty_print()  # If pretty_print returns a string, use it
                    if not isinstance(response_content, str):
                        response_content = str(response)  # Fallback
                    st.markdown(response_content)
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                except Exception as e:
                    error_msg = f"⚠️ Error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Add a shutdown button for manual exit
if st.button("🛑 Shutdown Agent"):
    shutdown_agent()