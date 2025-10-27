# server.py
import os, time, mimetypes, asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Verolux Dev Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

@app.get("/health")
def health():
    return JSONResponse({"ok": True, "ts": time.time()})

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"type": "hello", "ts": time.time()})
        while True:
            await ws.send_json({"type": "ping", "ts": time.time()})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

def ranged_iter(path, start, end, chunk=1024*1024):
    with open(path, "rb") as f:
        f.seek(start)
        left = end - start + 1
        while left > 0:
            n = min(chunk, left)
            data = f.read(n)
            if not data: break
            left -= len(data)
            yield data

@app.get("/stream")
def stream(request: Request, source: str):
    # Dev: source format "file:videoplayback.mp4" (file berada di folder kerja)
    if not source.startswith("file:"):
        raise HTTPException(400, "Dev mode only supports file:")
    path = source.split("file:")[1]
    if not os.path.isfile(path):
        raise HTTPException(404, f"File not found: {path}")

    size = os.path.getsize(path)
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    range_header = request.headers.get("range")

    if range_header:
        start_s, end_s = range_header.replace("bytes=", "").split("-")
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else size - 1
        end = min(end, size - 1)
        headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
        }
        return StreamingResponse(ranged_iter(path, start, end), status_code=206, media_type=ctype, headers=headers)
    else:
        headers = {"Accept-Ranges": "bytes", "Content-Length": str(size)}
        return StreamingResponse(open(path, "rb"), media_type=ctype, headers=headers)

