from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from .database.db import ROOT_DIR, init_db
from .routes import assistant, ngo, profiles, schemes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="SAHAAY - AI-Powered Government Scheme Assistant",
    description="MVP API for welfare scheme discovery, RAG explanations, voice output, and NGO assistance.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(schemes.router)
app.include_router(assistant.router)
app.include_router(ngo.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "sahaay-mvp"}


FRONTEND_DIR = Path(ROOT_DIR) / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")
