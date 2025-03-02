from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil
import logging
from groq import Groq
from utils.utils import LLM_GROQ

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medicine Comparission for Medical Reps ",
    description="",
    version="1.0.0"
)

@app.post("/askme/", summary="Query the Uploaded CSV File", tags=["Data Query"])
async def askme(
    medicine_name: str = Query(..., description="The Name of the medicine")
):
        """
    Query the data in an uploaded CSV file using an LLM.
    
    **Parameters:**
    - **medicine_name**: The question related to the data in the csv file.
    """
        result = LLM_GROQ(medicine_name)
        logger.info("LLM processed the query successfully.")
        return {"message": result}

# Run the FastAPI app (if running locally)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the FastAPI application on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
