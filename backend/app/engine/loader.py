"""
GhoraGhuri — Graph Loader
Loads transport graph from database or Redis cache.
"""
from __future__ import annotations

import json
import logging

import redis.asyncio as redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.engine.graph import GraphEdge, GraphNode, TransportGraph
from app.engine.seed_data import create_dhaka_graph

logger = logging.getLogger(__name__)

GRAPH_CACHE_KEY = "ghoraghuri:graph:v1"


async def load_graph_from_cache(redis_client: redis.Redis) -> TransportGraph | None:
    """Try to load graph from Redis cache."""
    try:
        cached = await redis_client.get(GRAPH_CACHE_KEY)
        if cached:
            data = json.loads(cached)
            graph = TransportGraph.from_dict(data)
            logger.info(
                f"Loaded graph from Redis cache: {graph.node_count} nodes, {graph.edge_count} edges"
            )
            return graph
    except Exception as e:
        logger.warning(f"Failed to load graph from cache: {e}")
    return None


async def save_graph_to_cache(redis_client: redis.Redis, graph: TransportGraph) -> None:
    """Save graph to Redis cache."""
    try:
        data = json.dumps(graph.to_dict())
        await redis_client.setex(
            GRAPH_CACHE_KEY,
            settings.redis_graph_cache_ttl,
            data,
        )
        logger.info(f"Saved graph to Redis cache (TTL: {settings.redis_graph_cache_ttl}s)")
    except Exception as e:
        logger.warning(f"Failed to save graph to cache: {e}")


async def load_graph_from_db(session: AsyncSession) -> TransportGraph:
    """
    Load graph from PostgreSQL.
    Falls back to seed data if database is empty.
    """
    graph = TransportGraph()

    try:
        # Load nodes
        result = await session.execute(
            text("""
                SELECT id::text, code, name_en, name_bn,
                       ST_Y(location::geometry) as lat,
                       ST_X(location::geometry) as lng,
                       node_type
                FROM transport_nodes
                WHERE is_active = true
            """)
        )
        nodes = result.fetchall()

        if not nodes:
            logger.info("No nodes in database — using seed data")
            return create_dhaka_graph()

        for row in nodes:
            graph.add_node(GraphNode(
                id=row.id,
                code=row.code,
                name_en=row.name_en,
                name_bn=row.name_bn,
                lat=row.lat,
                lng=row.lng,
                node_type=row.node_type,
            ))

        # Load edges
        result = await session.execute(
            text("""
                SELECT id::text, from_node_id::text, to_node_id::text,
                       transport_mode, route_name_en, route_name_bn,
                       base_time_minutes, base_fare_bdt, distance_meters,
                       crowd_level, reliability_score, is_bidirectional
                FROM transport_edges
                WHERE is_active = true
            """)
        )
        edges = result.fetchall()

        for row in edges:
            graph.add_edge(GraphEdge(
                id=row.id,
                from_id=row.from_node_id,
                to_id=row.to_node_id,
                transport_mode=row.transport_mode,
                route_name_en=row.route_name_en,
                route_name_bn=row.route_name_bn,
                time_minutes=row.base_time_minutes,
                fare_bdt=row.base_fare_bdt,
                distance_meters=row.distance_meters,
                crowd_level=row.crowd_level,
                reliability=row.reliability_score,
                is_bidirectional=row.is_bidirectional,
            ))

        logger.info(f"Loaded graph from DB: {graph.node_count} nodes, {graph.edge_count} edges")

    except Exception as e:
        logger.warning(f"Failed to load graph from DB: {e} — using seed data")
        return create_dhaka_graph()

    return graph


async def load_graph(
    session: AsyncSession | None = None,
    redis_client: redis.Redis | None = None,
) -> TransportGraph:
    """
    Load transport graph with caching strategy:
    1. Try Redis cache first
    2. Fall back to PostgreSQL
    3. Fall back to seed data

    After loading from DB/seed, caches to Redis.
    """
    # 1. Try cache
    if redis_client:
        graph = await load_graph_from_cache(redis_client)
        if graph:
            return graph

    # 2. Try database
    if session:
        graph = await load_graph_from_db(session)
    else:
        logger.info("No DB session available — using seed data")
        graph = create_dhaka_graph()

    # 3. Cache the result
    if redis_client:
        await save_graph_to_cache(redis_client, graph)

    return graph
