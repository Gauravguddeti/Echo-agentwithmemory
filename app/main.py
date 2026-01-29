from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import chat, tasks, memory, session, projects

app = FastAPI(title="Echo AI Assistant")

# CORS for frontend dev if needed (or just allow all for local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(projects.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

# Mount frontend files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
