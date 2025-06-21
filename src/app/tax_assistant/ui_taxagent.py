import streamlit as st
from src.app.tax_assistant.api_taxagent import tax_agent_orchestrator, extract_final_answer_from_chat_result


# ─────────────────────── UI Layout ────────────────────────────

st.set_page_config(page_title="OCI RAG Tax Assistant", layout="wide")
st.title("🧾 Tax Assistant with OCI GenAI")
st.markdown("Ask tax-related questions using Oracle RAG Agent Service.")

user_input = st.text_area("Enter your query:", height=150)

if st.button("Ask"):
    if user_input.strip():
        try:
            with st.spinner("Contacting Oracle Tax Agent..."):
                response = tax_agent_orchestrator(user_input)
                st.success("Response received:")

                final_answer = extract_final_answer_from_chat_result(response)
                if(final_answer):
                    st.write("Final Answer: ", final_answer)
                    # Extract Citation URL
                    if (response.data.message):
                        citation_url = response.data.message.content.citations[0].source_location.url
                        st.write("Source URL:", citation_url)
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid question.")
