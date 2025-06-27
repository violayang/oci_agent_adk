import json, os
from oci.addons.adk import Agent, AgentClient, tool


from pathlib import Path
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent
print(PROJECT_ROOT)
load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
AGENT_ID = os.getenv("AGENT_ID")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_REGION = os.getenv("AGENT_REGION")
AGENT_COMPARTMENT_ID = os.getenv("AGENT_COMPARTMENT_ID")

# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────

@tool
def get_trending_keywords(topic):
    """ Get the trending keywords for a given topic. """
    # Here is a mock implementation
    return json.dumps({"topic": topic, "keywords": ["agent", "stargate", "openai"]})

@tool
def send_email(recipient, subject, body):
    """ Send an email to a recipient. """
    # Here is a mock implementation
    print("Sending email to ", recipient, "with subject", subject, "and body", body)
    return "Sent!"

def main():

    # A shared client for all agents
    # Create a client with your authentication details
    client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region=AGENT_REGION
    )

    # trend analyzer collaborator agent
    trend_analyzer = Agent(
        name="Trend Analyzer",
        instructions="You use the tools provided to analyze the trending keywords of given topics.",
        agent_endpoint_id=AGENT_EP_ID,
        client=client,
        tools=[
            get_trending_keywords,
        ]
    )

    # content writer collaborator agent
    content_writer = Agent(
        name="Content Writer",
        instructions="You write a mini blog post (4 sentences) using the trending keywords.",
        agent_endpoint_id=AGENT_EP_ID,
        client=client,
    )

    # marketing director supervisor agent
    marketing_director = Agent(
        name="Marketing Director",
        instructions="You ask the trend analyzer for trending keywords and "
         + " You then ask the content writer to write a blog post using the trending keywords. "
         + " You then send email to 'jane.doe@example.com' with the blog post."
         + " Then summarize the actions you took and reply to the user.",
        agent_endpoint_id=AGENT_EP_ID,
        client=client,
        tools=[
            trend_analyzer.as_tool(
                tool_name="analyze_trending_keywords",
                tool_description="Analyze the trending keywords of given topics",
            ),
            content_writer.as_tool(
                tool_name="write_blog_post",
                tool_description="Write a blog post using the trending keywords.",
            ),
            send_email,
        ]
    )

    # Set up the agents once
    trend_analyzer.setup()
    content_writer.setup()
    marketing_director.setup()

    # Use the supervisor agent to process the end user request
    input = "Produce a blog post about current trends in the AI industry."
    response = marketing_director.run(input, max_steps=5)
    response.pretty_print()


if __name__ == "__main__":
    main()