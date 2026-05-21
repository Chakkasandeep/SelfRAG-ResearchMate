import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import asyncio
import json

# Initialize environment configuration
load_dotenv(override=True)

# Configure logging structure
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

# Load graph workflow after env loading
from graph.workflow import run_research_pipeline

app = FastAPI(
    title="ResearchMate API",
    description="Zero-Hallucination Academic Literature Review Agentic Assistant using LangGraph + Self-RAG."
)

# Enable CORS for Next.js dev server connections
cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "ResearchMate FastAPI services are running."}

@app.post("/api/research/stream")
async def research_stream(body: dict):
    """
    Streaming SSE endpoint that runs the LangGraph research pipeline.
    Yields step-by-step agent transition logs and synthesis outputs.
    """
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Research query cannot be empty.")
        
    logger.info(f"Initiating research stream for query: '{query}'")

    async def event_generator():
        try:
            async for event in run_research_pipeline(query):
                # Starlette EventSourceResponse requires standard yield formats
                yield {
                    "event": "message",
                    "data": json.dumps(event)
                }
        except asyncio.CancelledError:
            logger.info("SSE client disconnected from research stream.")
        except Exception as e:
            logger.error(f"Error encountered during research graph execution: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"stage": "error", "error": str(e)})
            }

    return EventSourceResponse(event_generator())

@app.post("/api/export/pptx")
async def export_pptx(body: dict):
    """
    Server-side PowerPoint exporter endpoint.
    Converts synthetic review nodes and reference keys to formatted slide decks.
    """
    review = body.get("review", "")
    citations = body.get("citations", [])
    
    if not review:
        raise HTTPException(status_code=400, detail="Literature review content is empty.")
        
    try:
        from output.ppt_generator import generate_pptx
        path = generate_pptx(review, citations)
        logger.info(f"Successfully generated PowerPoint slide deck at {path}")
        
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename="Literature_Review_Deck.pptx"
        )
    except Exception as e:
        logger.error(f"PowerPoint generation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PowerPoint deck: {str(e)}")

@app.post("/api/export/pdf")
async def export_pdf(body: dict):
    """
    Server-side PDF exporter endpoint using ReportLab.
    Ensures seamless dependency-free generation of academic reports on Windows.
    """
    review = body.get("review", "")
    citations = body.get("citations", [])
    
    if not review:
        raise HTTPException(status_code=400, detail="Literature review content is empty.")
        
    try:
        from output.pdf_generator import generate_pdf
        path = generate_pdf(review, citations)
        logger.info(f"Successfully generated academic PDF report at {path}")
        
        return FileResponse(
            path,
            media_type="application/pdf",
            filename="Literature_Review_Report.pdf"
        )
    except Exception as e:
        logger.error(f"PDF generation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting FastAPI on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
