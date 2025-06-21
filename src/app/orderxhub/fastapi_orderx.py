from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os
from src.app.orderxhub.api_orderx import orderx_agent_orchestrator, extract_final_answer_from_chat_result
from src.agents.orderx import agent_flow


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

        agent = agent_flow()

        response = agent.run(input_prompt)

        final_answer = response.data["message"]["content"]["text"]
        print(final_answer)
        # response = orderx_agent_orchestrator(input_prompt)
        #
        # final_answer = extract_final_answer_from_chat_result(response)

        return JSONResponse(content={"final_answer": final_answer})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
