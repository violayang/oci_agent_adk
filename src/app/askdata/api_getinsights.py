from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from src.agents.getinsights import agent_flow
import traceback, json, os
import asyncio, os

app = FastAPI()


@app.get("/askdata/getinsights")
async def getinsights(input_prompt: str):
    """
    Get insights from conversation stored by AskData solutions into a Redis cache.
    """
    try:

        #agent_get = await agent_flow()
        response = await agent_flow(input_prompt)
        print(response)
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

async def main():
    result = await getinsights("based on criteria such as highest amount due and highest past due date for 'session:e5f6a932-6123-4a04-98e9-6b829904d27f'")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())