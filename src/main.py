from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from contextlib import asynccontextmanager
from src.database.database import engine, Base
from src.api import upload_api, analysis_api, report_api, discard_api,excel_download, analytics_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
 
app = FastAPI(title="Exit Interview Analysis System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # OR specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_api.router, tags=["Upload Excel API"])
app.include_router(analysis_api.router, tags=["LLM Analysis API"])
app.include_router(report_api.router, tags=["Reports API"])
app.include_router(discard_api.router, tags=["Discard Pending Responses API"])
app.include_router(excel_download.router, tags=["Excel Download API"])
app.include_router(analytics_api.router, tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "Exit Interview Analysis System is Running"}