from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from src.agents.agent_image2text import agent_flow
import traceback

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
        print(input_prompt)
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
