from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Dict
import shutil
from src.agents.agent_image2text import agent_flow
import traceback, json, os

app = FastAPI()

@app.post("/query/image")
async def ask_agent_from_image(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        # Save image locally
        temp_path = Path("/tmp") / image.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)


        # Build the prompt
        input_prompt = f"{str(temp_path)}   \n{question}"
        agent_image2text = agent_flow()
        response = await agent_image2text.run_async(input_prompt)

        final_answer = response.data["message"]["content"]["text"]
        print(final_answer)

        return JSONResponse(content={"final_answer": final_answer})
    except Exception as e:
        # Print the full stack trace to stdout/logs
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )



@app.post("/orders/create")
async def create_sales_order(payload: Dict = Body(...)):
    """
    Create an order using the OCI AI agent and a structured JSON payload.
    """
    try:
        # Convert the Python dict to a properly escaped JSON string
        payload_json = json.dumps(payload)

        # Construct a human-readable prompt with embedded JSON
        input_prompt = f"Create a sales order using a properly structured JSON payload:\n{payload_json}"

        agent_order = agent_flow()
        response = await agent_order.run_async(input_prompt)

        final_answer = response.data["message"]["content"]["text"]
        print(final_answer)

        return JSONResponse(content={"final_answer": final_answer})
    except Exception as e:
        # Print the full stack trace to stdout/logs
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.get("/orders/query")
async def query_sales_order(query_string: str):
    """
    Get sales order using a query string for the Oracle SCM API.
    Example:
    /orders/query?query_string=finder=findBySourceOrderNumberAndSystem;SourceTransactionNumber=404087,SourceTransactionSystem=GPR
    """
    try:
        input_prompt = f"Get sales order with query string for API call as: {query_string}"
        agent = agent_flow()
        response = await agent.run_async(input_prompt)

        final_answer = response.data["message"]["content"]["text"]
        print(final_answer)

        return JSONResponse(content={"final_answer": final_answer})
    except Exception as e:
        # Print the full stack trace to stdout/logs
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
