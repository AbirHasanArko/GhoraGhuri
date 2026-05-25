"""
GhoraGhuri — Multi-Objective Cost Function
Computes the traversal cost for edges in the transport graph.

The cost function balances multiple factors:
    cost = α*time + β*fare + γ*crowd + δ*walking_penalty + ε*transfer_penalty

Weights are adjustable based on user preference (optimize for time, cost, or comfort).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.engine.graph import GraphEdge


@dataclass
class RoutePreferences:
    """User preferences for route optimization."""
    optimize: str = "time"  # "time" | "cost" | "comfort"
    avoid_walking: bool = False
    max_walking_meters: int = 2000
    max_transfers: int = 5

    # Custom weight overrides (optional)
    custom_weights: dict[str, float] = field(default_factory=dict)


# ── Weight Presets ────────────────────────────────────────────

WEIGHT_PRESETS: dict[str, dict[str, float]] = {
    "time": {
        "alpha_time": 0.45,
        "beta_fare": 0.15,
        "gamma_crowd": 0.15,
        "delta_walking": 0.15,
        "epsilon_transfer": 0.10,
    },
    "cost": {
        "alpha_time": 0.15,
        "beta_fare": 0.45,
        "gamma_crowd": 0.15,
        "delta_walking": 0.15,
        "epsilon_transfer": 0.10,
    },
    "comfort": {
        "alpha_time": 0.20,
        "beta_fare": 0.10,
        "gamma_crowd": 0.35,
        "delta_walking": 0.25,
        "epsilon_transfer": 0.10,
    },
}

# ── Normalization Constants ───────────────────────────────────
# Based on typical Dhaka transport ranges

MAX_TIME_MINUTES = 120.0  # 2 hours max single-leg
MAX_FARE_BDT = 100.0  # 100 BDT max single-leg
MAX_DISTANCE_METERS = 20_000.0  # 20 km max single-leg


def get_weights(preferences: RoutePreferences) -> dict[str, float]:
    """Get cost function weights based on user preferences."""
    preset = WEIGHT_PRESETS.get(preferences.optimize, WEIGHT_PRESETS["time"])

    if preferences.custom_weights:
        return {**preset, **preferences.custom_weights}

    return preset


def edge_cost(
    edge: GraphEdge,
    preferences: RoutePreferences,
    previous_mode: str | None = None,
) -> float:
    """
    Calculate the traversal cost for a single edge.

    Args:
        edge: The graph edge to evaluate
        preferences: User's route preferences
        previous_mode: Transport mode of the previous edge (for transfer penalty)

    Returns:
        Cost value (lower is better). Not a real-world unit — used for A* comparison.

    Cost formula:
        cost = α * time_normalized
             + β * fare_normalized
             + γ * crowd_penalty
             + δ * walking_penalty
             + ε * transfer_penalty
    """
    weights = get_weights(preferences)

    # ── Time component ────────────────────────────────────
    time_normalized = min(edge.time_minutes / MAX_TIME_MINUTES, 1.0)

    # ── Fare component ────────────────────────────────────
    fare_normalized = min(edge.fare_bdt / MAX_FARE_BDT, 1.0) if MAX_FARE_BDT > 0 else 0.0

    # ── Crowd penalty ─────────────────────────────────────
    crowd_penalty = edge.crowd_penalty

    # ── Walking penalty ───────────────────────────────────
    if edge.transport_mode == "walking":
        if preferences.avoid_walking:
            walking_penalty = 2.0  # very high penalty
        else:
            # Proportional to distance
            walking_penalty = min(edge.distance_meters / preferences.max_walking_meters, 1.5)
    else:
        walking_penalty = 0.0

    # ── Transfer penalty ──────────────────────────────────
    if previous_mode and previous_mode != edge.transport_mode:
        # Mode change = transfer
        # Bigger penalty for uncomfortable transfers
        if edge.transport_mode == "walking":
            transfer_penalty = 0.3  # walking to transfer is mild
        else:
            transfer_penalty = 0.6  # full mode switch
    else:
        transfer_penalty = 0.0

    # ── Reliability bonus ─────────────────────────────────
    # Higher reliability = lower cost (subtract a small bonus)
    reliability_bonus = (1.0 - edge.reliability) * 0.1

    # ── Final cost ────────────────────────────────────────
    cost = (
        weights["alpha_time"] * time_normalized
        + weights["beta_fare"] * fare_normalized
        + weights["gamma_crowd"] * crowd_penalty
        + weights["delta_walking"] * walking_penalty
        + weights["epsilon_transfer"] * transfer_penalty
        + reliability_bonus
    )

    return max(cost, 0.001)  # ensure positive cost


def heuristic(
    lat1: float, lng1: float,
    lat2: float, lng2: float,
    avg_speed_kmh: float = 15.0,
) -> float:
    """
    A* heuristic: estimated cost from current position to goal.

    Uses straight-line distance / average transport speed.
    The average speed in Dhaka traffic is ~15 km/h for buses/CNGs.

    This heuristic is admissible (never overestimates) because:
    - Straight-line distance ≤ actual travel distance
    - We use a generous average speed

    Args:
        lat1, lng1: Current position
        lat2, lng2: Goal position
        avg_speed_kmh: Average transport speed (default: 15 km/h for Dhaka)

    Returns:
        Heuristic cost value (same scale as edge_cost)
    """
    import math

    R = 6_371_000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_meters = R * c

    # Convert to time estimate (minutes)
    time_estimate_minutes = (distance_meters / 1000.0) / avg_speed_kmh * 60.0

    # Normalize to cost scale
    normalized_time = min(time_estimate_minutes / MAX_TIME_MINUTES, 1.0)

    # Scale down to ensure admissibility (multiply by smallest weight)
    return normalized_time * 0.15
