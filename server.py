import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.health import router as health_router
from backend.routes.parse import router as parse_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Property Parser")

# API routes
app.include_router(health_router, prefix="/api")
app.include_router(parse_router, prefix="/api")

# Serve favicon
@app.get("/favicon.png")
async def favicon():
    return FileResponse("favicon.png")

# Serve frontend static files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8090, reload=True)
