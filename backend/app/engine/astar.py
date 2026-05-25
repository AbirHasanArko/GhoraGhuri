"""
GhoraGhuri — A* Routing Algorithm
Multi-modal pathfinding through Bangladesh's transport network.

Features:
- A* search with admissible heuristic (haversine-based)
- Multi-objective cost function (time, fare, crowd, walking, transfers)
- Mode-aware state space: (node_id, last_transport_mode)
- Configurable max expansions, max transfers, max walking
- Returns structured route with step-by-step instructions
"""
from __future__ import annotations

import heapq
import logging
import time
from dataclasses import dataclass, field

from app.config import settings
from app.engine.cost import RoutePreferences, edge_cost, heuristic
from app.engine.graph import GraphEdge, GraphNode, TransportGraph

logger = logging.getLogger(__name__)


@dataclass
class RouteStep:
    """A single step in a route."""
    step_order: int
    from_node: GraphNode
    to_node: GraphNode
    edge: GraphEdge
    transport_mode: str
    instruction_en: str
    instruction_bn: str
    duration_minutes: float
    fare_bdt: float
    distance_meters: float


@dataclass
class RouteResult:
    """Complete route result from A* search."""
    steps: list[RouteStep]
    total_time_min: float
    total_time_max: float
    total_fare_min: float
    total_fare_max: float
    total_distance_meters: float
    num_transfers: int
    confidence_score: float
    computation_ms: float
    nodes_expanded: int
    is_found: bool = True
    error_message: str | None = None


@dataclass(order=True)
class _PQEntry:
    """Priority queue entry for A*."""
    f_score: float
    counter: int  # tiebreaker
    node_id: str = field(compare=False)
    last_mode: str | None = field(compare=False)
    g_score: float = field(compare=False)
    path: list[GraphEdge] = field(compare=False, default_factory=list)
    transfers: int = field(compare=False, default=0)


# ── Transport mode display names ─────────────────────────────

MODE_NAMES_EN = {
    "bus": "Bus",
    "rickshaw": "Rickshaw",
    "cng": "CNG Auto-Rickshaw",
    "leguna": "Leguna",
    "tempo": "Tempo",
    "walking": "Walk",
    "launch": "Launch/Boat",
    "train": "Train",
}

MODE_NAMES_BN = {
    "bus": "বাস",
    "rickshaw": "রিকশা",
    "cng": "সিএনজি",
    "leguna": "লেগুনা",
    "tempo": "টেম্পো",
    "walking": "হাঁটুন",
    "launch": "লঞ্চ/নৌকা",
    "train": "ট্রেন",
}


def _generate_instruction_en(edge: GraphEdge, from_node: GraphNode, to_node: GraphNode) -> str:
    """Generate English route instruction for a step."""
    mode = MODE_NAMES_EN.get(edge.transport_mode, edge.transport_mode)

    if edge.transport_mode == "walking":
        dist = int(edge.distance_meters)
        return f"Walk {dist}m from {from_node.name_en} to {to_node.name_en} (≈{int(edge.time_minutes)} min)"

    route_info = f" ({edge.route_name_en})" if edge.route_name_en else ""
    fare_info = f", ৳{int(edge.fare_bdt)}" if edge.fare_bdt > 0 else ""
    return (
        f"Take {mode}{route_info} from {from_node.name_en} "
        f"to {to_node.name_en} (≈{int(edge.time_minutes)} min{fare_info})"
    )


def _generate_instruction_bn(edge: GraphEdge, from_node: GraphNode, to_node: GraphNode) -> str:
    """Generate Bangla route instruction for a step."""
    mode = MODE_NAMES_BN.get(edge.transport_mode, edge.transport_mode)

    if edge.transport_mode == "walking":
        dist = int(edge.distance_meters)
        return f"{from_node.name_bn} থেকে {to_node.name_bn} পর্যন্ত {dist} মিটার হাঁটুন (≈{int(edge.time_minutes)} মিনিট)"

    route_info = f" ({edge.route_name_bn})" if edge.route_name_bn else ""
    fare_info = f", ৳{int(edge.fare_bdt)}" if edge.fare_bdt > 0 else ""
    return (
        f"{from_node.name_bn} থেকে {to_node.name_bn} পর্যন্ত "
        f"{mode}{route_info} নিন (≈{int(edge.time_minutes)} মিনিট{fare_info})"
    )


def find_route(
    graph: TransportGraph,
    start_id: str,
    end_id: str,
    preferences: RoutePreferences | None = None,
) -> RouteResult:
    """
    Find optimal route using A* search.

    Args:
        graph: The transport graph to search
        start_id: Starting node ID
        end_id: Destination node ID
        preferences: Route optimization preferences

    Returns:
        RouteResult with step-by-step instructions and cost estimates
    """
    start_time = time.perf_counter()

    if preferences is None:
        preferences = RoutePreferences()

    max_expansions = settings.max_route_expansions

    # ── Validate inputs ──────────────────────────────────

    start_node = graph.get_node(start_id)
    end_node = graph.get_node(end_id)

    if not start_node:
        return RouteResult(
            steps=[], total_time_min=0, total_time_max=0,
            total_fare_min=0, total_fare_max=0, total_distance_meters=0,
            num_transfers=0, confidence_score=0, computation_ms=0,
            nodes_expanded=0, is_found=False,
            error_message=f"Start node not found: {start_id}",
        )

    if not end_node:
        return RouteResult(
            steps=[], total_time_min=0, total_time_max=0,
            total_fare_min=0, total_fare_max=0, total_distance_meters=0,
            num_transfers=0, confidence_score=0, computation_ms=0,
            nodes_expanded=0, is_found=False,
            error_message=f"Destination node not found: {end_id}",
        )

    if start_id == end_id:
        return RouteResult(
            steps=[], total_time_min=0, total_time_max=0,
            total_fare_min=0, total_fare_max=0, total_distance_meters=0,
            num_transfers=0, confidence_score=1.0,
            computation_ms=0, nodes_expanded=0,
            is_found=True,
            error_message="Origin and destination are the same",
        )

    # ── A* Search ────────────────────────────────────────

    counter = 0
    h_start = heuristic(start_node.lat, start_node.lng, end_node.lat, end_node.lng)

    open_set: list[_PQEntry] = []
    heapq.heappush(open_set, _PQEntry(
        f_score=h_start,
        counter=counter,
        node_id=start_id,
        last_mode=None,
        g_score=0.0,
        path=[],
        transfers=0,
    ))

    # Best g_score for each state: (node_id, last_mode)
    best_g: dict[tuple[str, str | None], float] = {(start_id, None): 0.0}

    nodes_expanded = 0

    while open_set and nodes_expanded < max_expansions:
        current = heapq.heappop(open_set)
        nodes_expanded += 1

        # ── Goal check ────────────────────────────────
        if current.node_id == end_id:
            computation_ms = (time.perf_counter() - start_time) * 1000
            return _build_result(
                graph, current.path, preferences, computation_ms, nodes_expanded
            )

        # ── Expand neighbors ──────────────────────────
        for edge in graph.get_neighbors(current.node_id):
            if not graph.get_node(edge.to_id):
                continue  # skip edges to inactive/missing nodes

            # Check walking distance limit
            if edge.transport_mode == "walking" and edge.distance_meters > preferences.max_walking_meters:
                continue

            # Count transfers
            is_transfer = current.last_mode is not None and current.last_mode != edge.transport_mode
            new_transfers = current.transfers + (1 if is_transfer else 0)

            if new_transfers > preferences.max_transfers:
                continue

            # Calculate cost
            g_new = current.g_score + edge_cost(edge, preferences, current.last_mode)

            state = (edge.to_id, edge.transport_mode)

            # Skip if we've seen a better path to this state
            if state in best_g and g_new >= best_g[state]:
                continue

            best_g[state] = g_new

            # Heuristic
            to_node = graph.get_node(edge.to_id)
            if to_node:
                h = heuristic(to_node.lat, to_node.lng, end_node.lat, end_node.lng)
            else:
                h = 0.0

            counter += 1
            heapq.heappush(open_set, _PQEntry(
                f_score=g_new + h,
                counter=counter,
                node_id=edge.to_id,
                last_mode=edge.transport_mode,
                g_score=g_new,
                path=current.path + [edge],
                transfers=new_transfers,
            ))

    # ── No path found ────────────────────────────────────
    computation_ms = (time.perf_counter() - start_time) * 1000
    return RouteResult(
        steps=[], total_time_min=0, total_time_max=0,
        total_fare_min=0, total_fare_max=0, total_distance_meters=0,
        num_transfers=0, confidence_score=0,
        computation_ms=computation_ms, nodes_expanded=nodes_expanded,
        is_found=False,
        error_message="No route found between the specified locations",
    )


def _build_result(
    graph: TransportGraph,
    path: list[GraphEdge],
    preferences: RoutePreferences,
    computation_ms: float,
    nodes_expanded: int,
) -> RouteResult:
    """Build a structured RouteResult from the A* path."""

    steps: list[RouteStep] = []
    total_time = 0.0
    total_fare = 0.0
    total_distance = 0.0
    num_transfers = 0
    reliability_sum = 0.0
    prev_mode: str | None = None

    for i, edge in enumerate(path):
        from_node = graph.get_node(edge.from_id)
        to_node = graph.get_node(edge.to_id)

        if not from_node or not to_node:
            continue

        # Count transfers
        if prev_mode and prev_mode != edge.transport_mode:
            num_transfers += 1

        instruction_en = _generate_instruction_en(edge, from_node, to_node)
        instruction_bn = _generate_instruction_bn(edge, from_node, to_node)

        steps.append(RouteStep(
            step_order=i + 1,
            from_node=from_node,
            to_node=to_node,
            edge=edge,
            transport_mode=edge.transport_mode,
            instruction_en=instruction_en,
            instruction_bn=instruction_bn,
            duration_minutes=edge.time_minutes,
            fare_bdt=edge.fare_bdt,
            distance_meters=edge.distance_meters,
        ))

        total_time += edge.time_minutes
        total_fare += edge.fare_bdt
        total_distance += edge.distance_meters
        reliability_sum += edge.reliability
        prev_mode = edge.transport_mode

    # ── Time/fare ranges ─────────────────────────────────
    # Add ±20% variance for ETA range (Dhaka traffic is unpredictable)
    time_variance = 0.20
    fare_variance = 0.10

    total_time_min = total_time * (1 - time_variance)
    total_time_max = total_time * (1 + time_variance)
    total_fare_min = total_fare * (1 - fare_variance)
    total_fare_max = total_fare * (1 + fare_variance)

    # ── Confidence score ─────────────────────────────────
    # Based on average reliability of edges in path
    avg_reliability = reliability_sum / len(path) if path else 0.0
    confidence = min(avg_reliability, 1.0)

    return RouteResult(
        steps=steps,
        total_time_min=round(total_time_min, 1),
        total_time_max=round(total_time_max, 1),
        total_fare_min=round(total_fare_min, 1),
        total_fare_max=round(total_fare_max, 1),
        total_distance_meters=round(total_distance, 0),
        num_transfers=num_transfers,
        confidence_score=round(confidence, 2),
        computation_ms=round(computation_ms, 2),
        nodes_expanded=nodes_expanded,
        is_found=True,
    )
