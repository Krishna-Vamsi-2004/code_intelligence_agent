
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import generate_router, debug_router, score_router, mermaid_router, mermaid_cli_router, pipeline_router
from models.schemas import PipelineRequest
from utils.service_container import ServiceContainer

app = FastAPI(title="Code Intelligence Agent")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Force service container initialization
    ServiceContainer._instance = None
    services = ServiceContainer.get_instance()
    print(f"✅ Services initialized: LLM type = {type(services.llm).__name__}")

# CORS middleware for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers as these are end points 
app.include_router(generate_router.router, prefix="/api/generate", tags=["Code Generation"])
app.include_router(debug_router.router, prefix="/api/debug", tags=["Debugging"])
app.include_router(score_router.router, prefix="/api/score", tags=["Optimality Score"])
app.include_router(mermaid_router.router, prefix="/api/mermaid", tags=["Visual Flow"])
app.include_router(mermaid_cli_router.router, prefix="/api/mermaid-cli", tags=["Mermaid CLI"])
app.include_router(pipeline_router.router, prefix="/api/pipeline", tags=["Pipeline"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Code Intelligence Agent API"}
