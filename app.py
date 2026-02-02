"""
FastAPI Backend for RAG2 - AI Research Paper Assistant
Provides REST API endpoints for paper ingestion and querying
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG2 - AI Research Paper Assistant",
    description="Upload research papers and ask questions using RAG",
    version="1.0.0"
)

# CORS configuration - allow frontend to access API
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline (singleton)
rag_pipeline = None
papers_dir = Path('data/papers')
papers_dir.mkdir(parents=True, exist_ok=True)


def get_pipeline():
    """Get or create RAG pipeline instance"""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()
    return rag_pipeline


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]


class HealthResponse(BaseModel):
    status: str
    message: str
    papers_count: int


class PaperInfo(BaseModel):
    filename: str
    size_bytes: int


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG2 - AI Research Paper Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload (POST)",
            "query": "/api/query (POST)",
            "papers": "/api/papers (GET)"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        pdf_files = list(papers_dir.glob('*.pdf'))
        return HealthResponse(
            status="healthy",
            message="API is running",
            papers_count=len(pdf_files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/papers", response_model=List[PaperInfo])
async def list_papers():
    """List all uploaded papers"""
    try:
        pdf_files = list(papers_dir.glob('*.pdf'))
        papers = [
            PaperInfo(
                filename=pdf.name,
                size_bytes=pdf.stat().st_size
            )
            for pdf in pdf_files
        ]
        return papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_paper(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF research paper
    
    - Saves PDF to data/papers/
    - Automatically ingests into vector database
    - Returns success message
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Save file
        file_path = papers_dir / file.filename
        content = await file.read()
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Ingest the paper
        pipeline = get_pipeline()
        pipeline.ingest_papers([str(file_path)])
        
        return {
            "status": "success",
            "message": f"Paper '{file.filename}' uploaded and ingested successfully",
            "filename": file.filename,
            "size_bytes": len(content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/query", response_model=QueryResponse)
async def query_papers(request: QueryRequest):
    """
    Ask a question about the uploaded papers
    
    - Uses RAG to find relevant context
    - Generates answer with source citations
    - Returns answer and sources
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check if any papers are uploaded
        pdf_files = list(papers_dir.glob('*.pdf'))
        if not pdf_files:
            raise HTTPException(
                status_code=400,
                detail="No papers uploaded. Please upload at least one PDF first."
            )
        
        # Query the RAG pipeline
        pipeline = get_pipeline()
        result = pipeline.query(request.question)
        
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/ingest-all")
async def ingest_all_papers():
    """
    Manually trigger ingestion of all papers in data/papers/
    Useful for re-indexing or initial setup
    """
    try:
        pdf_files = list(papers_dir.glob('*.pdf'))
        
        if not pdf_files:
            return {
                "status": "warning",
                "message": "No PDF files found in data/papers/",
                "papers_ingested": 0
            }
        
        pipeline = get_pipeline()
        pipeline.ingest_papers([str(p) for p in pdf_files])
        
        return {
            "status": "success",
            "message": f"Ingested {len(pdf_files)} paper(s)",
            "papers_ingested": len(pdf_files),
            "papers": [p.name for p in pdf_files]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.delete("/api/papers/{filename}")
async def delete_paper(filename: str):
    """
    Delete a specific paper by filename
    """
    try:
        file_path = papers_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Paper '{filename}' not found")
        
        # Delete the file
        file_path.unlink()
        
        return {
            "status": "success",
            "message": f"Paper '{filename}' deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.delete("/api/papers")
async def delete_all_papers():
    """
    Delete all papers from data/papers/
    """
    try:
        pdf_files = list(papers_dir.glob('*.pdf'))
        
        if not pdf_files:
            return {
                "status": "warning",
                "message": "No papers to delete",
                "deleted_count": 0
            }
        
        # Delete all PDF files
        for pdf in pdf_files:
            pdf.unlink()
        
        return {
            "status": "success",
            "message": f"Deleted {len(pdf_files)} paper(s)",
            "deleted_count": len(pdf_files)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# Run the API server
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 Starting RAG2 API Server")
    print("="*60)
    print(f"\n✓ Papers directory: {papers_dir.absolute()}")
    print(f"✓ CORS enabled for: {ALLOWED_ORIGINS}")
    print("\n📡 Server starting at http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
