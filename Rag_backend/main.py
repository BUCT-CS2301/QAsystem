from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Annotated
import json

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.qa_service import QAService


class ChatRequest(BaseModel):
    question: str


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


@app.post("/api/chat")
def chat_sse(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")

    async def event_stream():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        queue = asyncio.Queue()

        def background_generate():
            try:
                gen, m = qa_service.ask_stream(question)
                for t in gen:
                    loop.call_soon_threadsafe(queue.put_nowait, ("token", t))
                loop.call_soon_threadsafe(queue.put_nowait, ("meta", m))
            except Exception as exc:
                loop.call_soon_threadsafe(queue.put_nowait, ("error", exc))
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, ("done", None))

        executor = ThreadPoolExecutor(max_workers=1)
        loop.run_in_executor(executor, background_generate)

        buffer = ""
        meta = None
        
        while True:
            msg_type, item = await queue.get()
            
            if msg_type == "token":
                token = item
                buffer += token
                
                buffer = buffer.replace("[CONTENT]\n", "").replace("[CONTENT]", "")
                buffer = buffer.replace("[LLM_CONTENT]\n", "").replace("[LLM_CONTENT]", "")
                
                last_bracket = buffer.rfind("[")
                if last_bracket != -1:
                    partial = buffer[last_bracket:]
                    if "[CONTENT]".startswith(partial) or "[LLM_CONTENT]".startswith(partial):
                        safe_part = buffer[:last_bracket]
                        buffer = partial
                    else:
                        safe_part = buffer
                        buffer = ""
                else:
                    safe_part = buffer
                    buffer = ""
                
                if safe_part:
                    lines = safe_part.split('\n')
                    token_data = "".join(f"data: {line}\n" for line in lines)
                    sse_msg = f"event: llm\n{token_data}\n"
                    print(sse_msg.strip(), flush=True)
                    yield sse_msg
                    
            elif msg_type == "meta":
                meta = item
                if buffer:
                    buffer = buffer.replace("[CONTENT]", "").replace("[LLM_CONTENT]", "")
                    if buffer:
                        lines = buffer.split('\n')
                        token_data = "".join(f"data: {line}\n" for line in lines)
                        sse_msg = f"event: llm\n{token_data}\n"
                        print(sse_msg.strip(), flush=True)
                        yield sse_msg
                
                if meta and meta.sources:
                    for src in meta.sources:
                        src_data = json.dumps({"name": src.name, "url": src.url}, ensure_ascii=False)
                        src_msg = f"event: source\ndata: {src_data}\n\n"
                        print(src_msg.strip(), flush=True)
                        yield src_msg
                
                images = []
                if meta and getattr(meta, "related_artifacts", None):
                    for a in meta.related_artifacts:
                        if a.image_url and a.image_url not in images:
                            images.append(a.image_url)
                for img_url in images:
                    img_data = json.dumps({"url": img_url}, ensure_ascii=False)
                    img_msg = f"event: img\ndata: {img_data}\n\n"
                    print(img_msg.strip(), flush=True)
                    yield img_msg
                    
            elif msg_type == "error":
                import traceback
                traceback.print_exception(type(item), item, item.__traceback__)
                err_msg = f"event: error\ndata: {str(item)}\n\n"
                print(err_msg.strip(), flush=True)
                yield err_msg
                break
                
            elif msg_type == "done":
                done_msg = "event: done\ndata: end\n\n"
                print(done_msg.strip(), flush=True)
                yield done_msg
                break


    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
