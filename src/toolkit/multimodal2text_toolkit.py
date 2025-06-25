import os
from pdf2image import convert_from_path
from oci.addons.adk import Toolkit, tool
from PIL import Image
from langchain_core.messages import HumanMessage
from src.llm.oci_genai_vision import initialize_vision_llm
from src.tools.vision_instruct_tools import encode_image_as_base64

class MultiModal2Text(Toolkit):
    @tool
    def image_to_text(self, image_path: str, question: str) -> str:
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
        # print(response.content)
        return response.content

    @tool
    def convert_pdf_to_png(self, pdf_path, output_dir):
        """
        a tool to convert pdf to text
        :param pdf_path:
        :param output_dir:
        :return:
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Convert all pages to images (each page = 1 PNG)
        Image.MAX_IMAGE_PIXELS = None
        pages = convert_from_path(pdf_path, dpi=1024)

        for i, page in enumerate(pages):
            output_path = os.path.join(output_dir, f"page_{i + 1}.png")
            page.save(output_path, "PNG")
            print(f"Saved: {output_path}")