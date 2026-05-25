from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.qa_service import QAService


qa_service = QAService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    qa_service.close()


app = FastAPI(title="Museum Knowledge QA API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/qa/ask")
def ask(
    question: Annotated[str, Query(description="用户问题")],
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")

    result = qa_service.ask(question.strip())
    return {
        "code": 200,
        "data": {
            "content": result.content,
            "sources": [asdict(source) for source in result.sources],
            "llmContent": result.llmContent,
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
