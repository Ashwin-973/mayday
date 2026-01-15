"""
FastAPI application.
Main entry point for the backend server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router


# Create FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="Conversational AI agent for weather and stock data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies that the API is running and Ollama is accessible.
    """
    try:
        # Try to import and check Ollama connection
        from core.llm import get_llm
        llm = get_llm()
        
        return {
            "status": "healthy",
            "api": "running",
            "ollama": "accessible"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "api": "running",
            "ollama": f"error: {str(e)}"
        }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
