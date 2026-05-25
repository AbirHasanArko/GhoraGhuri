"""
GhoraGhuri — Application Settings
Loaded from environment variables / .env file
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    app_name: str = "GhoraGhuri"
    app_name_bn: str = "ঘোরাঘুরি"
    debug: bool = False
    api_version: str = "v1"
    secret_key: str = "change-me-in-production-please"

    # ── Database (PostgreSQL + PostGIS) ───────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ghoraghuri"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_graph_cache_ttl: int = 300  # seconds (5 min)
    redis_session_ttl: int = 86400  # 24 hours

    # ── JWT ───────────────────────────────────────────────────
    jwt_secret: str = "jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 72
    jwt_refresh_expiry_days: int = 30

    # ── bdapps API ────────────────────────────────────────────
    bdapps_base_url: str = "https://developer.bdapps.com"
    bdapps_app_id: str = ""
    bdapps_password: str = ""  # MD5-hashed API key
    bdapps_version: str = "1.0"

    # ── Economy ───────────────────────────────────────────────
    route_charge_bdt: float = 2.0
    coin_to_bdt_rate: float = 0.1  # 1 coin = 0.1 BDT → 10 coins = 1 BDT
    min_redeem_coins: int = 50
    reward_gps_track_per_km: int = 5
    reward_crowd_report: int = 2
    reward_route_verify: int = 5
    reward_stop_report: int = 3

    # ── Routing Engine ────────────────────────────────────────
    max_route_expansions: int = 10_000
    max_transfers: int = 5
    max_walking_meters: int = 2000
    default_optimize: str = "time"  # time | cost | comfort

    # ── Rate Limiting ─────────────────────────────────────────
    rate_limit_per_minute: int = 30
    rate_limit_route_per_hour: int = 20

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]

    @property
    def bdapps_configured(self) -> bool:
        """Check if bdapps credentials are set."""
        return bool(self.bdapps_app_id and self.bdapps_password)


settings = Settings()
