from typing import Dict, Any
from oci.addons.adk import Toolkit, tool
import base64
from langchain_core.messages import HumanMessage
from src.llm.oci_genai_vision import initialize_vision_llm

# Load and encode your image (local file)
def encode_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded


@tool
def image_to_text(image_path:str, question:str) -> str:
    """
     a tool to convert image to text
    :param image_path:
    :param question:
    :return:
    """

    # Encode image
    image_base64 = encode_image_as_base64(image_path)

    # Construct message with image and text
    messages = [
        HumanMessage(
            content=[
                {"type": "text", "text": f"{question}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        )
    ]

    llm = initialize_vision_llm()
    response = llm.invoke(messages)
    #print(response.content)
    return response.content

def test_image_to_text():
    import os
    from pathlib import Path

    THIS_DIR = Path(__file__).resolve()
    PROJECT_ROOT = THIS_DIR.parent.parent.parent

    image_path = f"{PROJECT_ROOT}/images/orderhub_handwritten.jpg"
    question = "What is the ship to address"
    print(image_path)
    response = image_to_text(image_path, question)
    return response

if __name__ == "__main__":
    response = test_image_to_text()
    print(response)