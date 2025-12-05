from fastapi import FastAPI
from src.api import upload_api, llm_analysis

app = FastAPI()

app.include_router(upload_api.router, tags=["Upload Excel API"])
app.include_router(llm_analysis.router, tags=["LLM Analysis API"])