import streamlit as st
import asyncio

from src.utils.extract_llm_response import extract_final_answer_from_chat_result
from src.agents.taxagent import agent_flow

st.set_page_config(page_title="OCI RAG Tax Assistant", layout="wide")
st.title("🧾 Tax Assistant with OCI GenAI")
st.markdown("Ask tax-related questions using Oracle RAG Agent Service.")

user_input = st.text_area("Enter your query:", height=150)
agent = agent_flow()

async def run_agent(agent, query):
    return await agent.run(query)

if st.button("Ask"):
    if user_input.strip():
        try:
            with st.spinner("Contacting Oracle Tax Agent..."):
                # Run the coroutine safely in a thread
                loop = asyncio.get_running_loop()
                task = loop.create_task(run_agent(agent, user_input))
                response = asyncio.run_coroutine_threadsafe(task, loop).result()

                st.success("Response received:")
                final_answer = extract_final_answer_from_chat_result(response)
                if final_answer:
                    st.write("**Final Answer:**", final_answer)

                    try:
                        citation_url = response.data.message.content.citations[0].source_location.url
                        st.markdown(f"[Source URL]({citation_url})")
                    except Exception:
                        pass
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter a valid question.")
