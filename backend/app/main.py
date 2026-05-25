"""
GhoraGhuri (ঘোরাঘুরি) — Main FastAPI Application
Production transit platform for Bangladesh.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, contribute, health, routes, sms, wallet
from app.config import settings
from app.database import close_db, init_db
from app.engine.loader import load_graph
from app.engine.seed_data import create_dhaka_graph
from app.utils.cache import close_redis, get_redis
from app.utils.i18n import load_locales

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.app_name} ({settings.app_name_bn})")

    # Load localization strings
    load_locales()
    logger.info("✅ Locales loaded (EN + BN)")

    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.warning(f"⚠️ Database not available: {e} (running in seed-data mode)")

    # Initialize Redis
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        redis_client = None
        logger.warning(f"⚠️ Redis not available: {e} (running without cache)")

    # Load transport graph
    try:
        graph = await load_graph(redis_client=redis_client)
    except Exception:
        graph = create_dhaka_graph()

    routes.set_graph(graph)
    logger.info(f"✅ Transport graph loaded: {graph.node_count} nodes, {graph.edge_count} edges")

    # bdapps status
    if settings.bdapps_configured:
        logger.info(f"✅ bdapps configured: app_id={settings.bdapps_app_id}")
    else:
        logger.warning("⚠️ bdapps NOT configured — running in dev mode (no payments)")

    logger.info(f"🟢 {settings.app_name} ready to serve!")

    yield

    # Shutdown
    logger.info(f"🔴 Shutting down {settings.app_name}...")
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")


# ── Create FastAPI app ─────────────────────────────────────

app = FastAPI(
    title=f"{settings.app_name} ({settings.app_name_bn})",
    description="Production transit routing platform for Bangladesh — multi-modal route finding, crowd-sourced data, bdapps payments.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routes ────────────────────────────────────

PREFIX = f"/api/{settings.api_version}"

app.include_router(health.router, prefix=PREFIX)
app.include_router(auth.router, prefix=PREFIX)
app.include_router(routes.router, prefix=PREFIX)
app.include_router(contribute.router, prefix=PREFIX)
app.include_router(wallet.router, prefix=PREFIX)
app.include_router(sms.router, prefix=PREFIX)


# ── Root endpoint ──────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "name_bn": settings.app_name_bn,
        "tagline": "Your Smart Transit Companion for Bangladesh",
        "tagline_bn": "বাংলাদেশের জন্য আপনার স্মার্ট যাতায়াত সঙ্গী",
        "version": "1.0.0",
        "docs": "/docs",
    }
