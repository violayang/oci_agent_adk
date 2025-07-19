
import json
import re
from typing import List

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from langchain.prompts import PromptTemplate
from src.llm.oci_genai import initialize_llm

llm = initialize_llm()

# class Person(BaseModel):
#     """Information about a person."""
#
#     name: str = Field(..., description="The name of the person")
#     height_in_meters: float = Field(
#         ..., description="The height of the person expressed in meters."
#     )
#
#
# class People(BaseModel):
#     """Identifying information about all people in a text."""
#
#     people: List[Person]
#
#
# # Prompt
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Answer the user query. Output your answer as JSON that  "
#             "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
#             "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
#         ),
#         ("human", "{query}"),
#     ]
# ).partial(schema=People.schema())
#
#
# # Custom parser
# def extract_json(message: AIMessage) -> List[dict]:
#     """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.
#
#     Parameters:
#         text (str): The text containing the JSON content.
#
#     Returns:
#         list: A list of extracted JSON strings.
#     """
#     text = message.content
#     # Define the regular expression pattern to match JSON blocks
#     pattern = r"\`\`\`json(.*?)\`\`\`"
#
#     # Find all non-overlapping matches of the pattern in the string
#     matches = re.findall(pattern, text, re.DOTALL)
#
#     # Return the list of matched JSON strings, stripping any leading or trailing whitespace
#     try:
#         return [json.loads(match.strip()) for match in matches]
#     except Exception:
#         raise ValueError(f"Failed to parse: {message}")
#
#
# query = "Anna is 23 years old and she is 6 feet tall"
#
# #print(prompt.format_prompt(query=query).to_string())
#
# chain = prompt | llm | extract_json
#
# response = chain.invoke({"query": query})
# print(json.dumps(response, indent=2))

from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class Person(BaseModel):
    """Information about a person."""

    name: str = Field(..., description="The name of the person")
    height_in_meters: float = Field(
        ..., description="The height of the person expressed in meters."
    )


class People(BaseModel):
    """Identifying information about all people in a text."""

    people: List[Person]


# Set up a parser
parser = PydanticOutputParser(pydantic_object=People)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json` tags\n{format_instructions}",
        ),
        ("human", "{query}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

query = "Anna is 23 years old and she is 6 feet tall"

print(prompt.invoke({"query": query}).to_string())

chain = prompt | llm | parser

response = chain.invoke({"query": query})

print(response)