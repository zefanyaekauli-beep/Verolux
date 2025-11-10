"""
Simple Backend Server - Basic Version
This is a simplified backend for testing
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Backend", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Simple Backend Running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




















