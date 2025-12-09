from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.database import engine, Base
from src.api import upload_api, analysis_api, report_api, discard_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
 
app = FastAPI(title="Exit Interview Analysis System", lifespan=lifespan)

app.include_router(upload_api.router, tags=["Upload Excel API"])
app.include_router(analysis_api.router, tags=["LLM Analysis API"])
app.include_router(report_api.router, tags=["Reports API"])
app.include_router(discard_api.router, tags=["Discard Pending Responses API"])

@app.get("/")
async def root():
    return {"message": "Exit Interview Analysis System is Running"}