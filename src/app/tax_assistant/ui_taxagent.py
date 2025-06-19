import streamlit as st
from api_taxagent import rag_agent_service


# ─────────────────────── UI Layout ────────────────────────────

st.set_page_config(page_title="OCI RAG Tax Assistant", layout="wide")
st.title("🧾 Tax Assistant with OCI GenAI")
st.markdown("Ask tax-related questions using Oracle RAG Agent Service.")

user_input = st.text_area("Enter your query:", height=150)

if st.button("Ask"):
    if user_input.strip():
        try:
            with st.spinner("Contacting Oracle RAG Agent..."):
                response = rag_agent_service(user_input)
                st.success("Response received:")
                st.write(response)
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid question.")
