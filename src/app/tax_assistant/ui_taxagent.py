import streamlit as st
import asyncio

from src.utils.extract_llm_response import extract_final_answer_from_chat_result
from src.agents.taxagent import agent_flow

st.set_page_config(page_title="OCI RAG Tax Assistant", layout="wide")
st.title("🧾 Tax Assistant with OCI GenAI")
st.markdown("Ask tax-related questions using Oracle RAG Agent Service.")

user_input = st.text_area("Enter your query:", height=150)

agent = agent_flow()

# Utility to safely run async code in Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()

    return loop.run_until_complete(coro)

if st.button("Ask"):
    if user_input.strip():
        try:
            with st.spinner("Contacting Oracle Tax Agent..."):
                response = run_async(agent.run_async(user_input))

                st.success("Response received:")
                final_answer = response.data["message"]["content"]["text"]

                if final_answer:
                    st.write("**Final Answer:**", final_answer)

                    try:
                        citation_url = response.data["message"]["content"]["citations"][0]["source_location"]["url"]
                        st.markdown(f"[Source URL]({citation_url})")
                    except Exception:
                        pass

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid question.")
