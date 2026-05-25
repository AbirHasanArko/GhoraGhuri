"""
GhoraGhuri — Transport Graph Data Structure
In-memory weighted directed graph representing Bangladesh's multi-modal transport network.

Nodes = stops, hubs, stands, intersections
Edges = transport connections (bus, rickshaw, CNG, walking, etc.)
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """A transport node (stop/hub) in the graph."""
    id: str
    code: str
    name_en: str
    name_bn: str
    lat: float
    lng: float
    node_type: str
    is_active: bool = True

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GraphNode):
            return self.id == other.id
        return NotImplemented


@dataclass
class GraphEdge:
    """A transport edge (route segment) in the graph."""
    id: str
    from_id: str
    to_id: str
    transport_mode: str
    route_name_en: str | None
    route_name_bn: str | None
    time_minutes: float
    fare_bdt: float
    distance_meters: float
    crowd_level: str  # low, medium, high, extreme
    reliability: float  # 0.0 to 1.0
    is_bidirectional: bool = True

    @property
    def crowd_penalty(self) -> float:
        """Numeric crowd penalty for cost calculation."""
        return {
            "low": 0.0,
            "medium": 0.3,
            "high": 0.7,
            "extreme": 1.0,
        }.get(self.crowd_level, 0.5)


@dataclass
class TransportGraph:
    """
    In-memory directed graph for multi-modal transit routing.

    Structure:
        nodes: Dict[node_id → GraphNode]
        adjacency: Dict[node_id → List[GraphEdge]]  (outgoing edges)

    The graph is loaded from PostgreSQL at startup and cached in Redis.
    Updates flow in from contributor data (crowd levels, new routes, etc.).
    """

    nodes: dict[str, GraphNode] = field(default_factory=dict)
    adjacency: dict[str, list[GraphEdge]] = field(default_factory=dict)

    # Lookup indexes
    _code_to_id: dict[str, str] = field(default_factory=dict)
    _name_en_to_id: dict[str, str] = field(default_factory=dict)
    _name_bn_to_id: dict[str, str] = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(edges) for edges in self.adjacency.values())

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        self._code_to_id[node.code.upper()] = node.id
        self._name_en_to_id[node.name_en.lower()] = node.id
        self._name_bn_to_id[node.name_bn] = node.id

        if node.id not in self.adjacency:
            self.adjacency[node.id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add an edge to the graph.
        If bidirectional, also adds the reverse edge.
        """
        if edge.from_id not in self.adjacency:
            self.adjacency[edge.from_id] = []
        self.adjacency[edge.from_id].append(edge)

        if edge.is_bidirectional:
            reverse = GraphEdge(
                id=f"{edge.id}_rev",
                from_id=edge.to_id,
                to_id=edge.from_id,
                transport_mode=edge.transport_mode,
                route_name_en=edge.route_name_en,
                route_name_bn=edge.route_name_bn,
                time_minutes=edge.time_minutes,
                fare_bdt=edge.fare_bdt,
                distance_meters=edge.distance_meters,
                crowd_level=edge.crowd_level,
                reliability=edge.reliability,
                is_bidirectional=False,  # prevent infinite recursion
            )
            if edge.to_id not in self.adjacency:
                self.adjacency[edge.to_id] = []
            self.adjacency[edge.to_id].append(reverse)

    def get_neighbors(self, node_id: str) -> list[GraphEdge]:
        """Get all outgoing edges from a node."""
        return self.adjacency.get(node_id, [])

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def find_nearest_node(self, lat: float, lng: float, max_results: int = 1) -> list[str]:
        """
        Find the nearest graph node(s) to a geographic point.
        Uses haversine distance for accuracy.

        Args:
            lat: Latitude
            lng: Longitude
            max_results: Number of nearest nodes to return

        Returns:
            List of node IDs, sorted by distance (nearest first)
        """
        distances: list[tuple[float, str]] = []

        for node_id, node in self.nodes.items():
            if not node.is_active:
                continue
            dist = self._haversine(lat, lng, node.lat, node.lng)
            distances.append((dist, node_id))

        distances.sort(key=lambda x: x[0])
        return [node_id for _, node_id in distances[:max_results]]

    def find_node_by_name(self, text: str, lang: str = "en") -> str | None:
        """
        Find a node by name using fuzzy matching.

        Args:
            text: Search text (e.g., 'Mirpur 10', 'মিরপুর ১০')
            lang: Language hint ('en' or 'bn')

        Returns:
            Node ID if found, None otherwise
        """
        text_lower = text.strip().lower()

        # Exact match first
        if lang == "bn":
            if text.strip() in self._name_bn_to_id:
                return self._name_bn_to_id[text.strip()]
        else:
            if text_lower in self._name_en_to_id:
                return self._name_en_to_id[text_lower]

        # Code match
        text_upper = text.strip().upper().replace(" ", "")
        if text_upper in self._code_to_id:
            return self._code_to_id[text_upper]

        # Fuzzy substring match
        best_match: str | None = None
        best_score = 0.0

        lookup = self._name_en_to_id if lang == "en" else self._name_bn_to_id

        for name, node_id in lookup.items():
            name_compare = name.lower() if lang == "en" else name
            score = self._fuzzy_score(text_lower if lang == "en" else text.strip(), name_compare)
            if score > best_score and score > 0.4:  # minimum threshold
                best_score = score
                best_match = node_id

        return best_match

    def find_node_by_code(self, code: str) -> str | None:
        """Find a node by its code (e.g., 'MIR10')."""
        return self._code_to_id.get(code.upper())

    def update_edge_crowd(self, edge_id: str, crowd_level: str) -> bool:
        """
        Update the crowd level of an edge (from contributor data).

        Returns True if the edge was found and updated.
        """
        for edges in self.adjacency.values():
            for edge in edges:
                if edge.id == edge_id or edge.id == f"{edge_id}_rev":
                    edge.crowd_level = crowd_level
                    return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to dict for Redis caching."""
        return {
            "nodes": {
                nid: {
                    "id": n.id, "code": n.code,
                    "name_en": n.name_en, "name_bn": n.name_bn,
                    "lat": n.lat, "lng": n.lng,
                    "node_type": n.node_type, "is_active": n.is_active,
                }
                for nid, n in self.nodes.items()
            },
            "edges": [
                {
                    "id": e.id, "from_id": e.from_id, "to_id": e.to_id,
                    "transport_mode": e.transport_mode,
                    "route_name_en": e.route_name_en, "route_name_bn": e.route_name_bn,
                    "time_minutes": e.time_minutes, "fare_bdt": e.fare_bdt,
                    "distance_meters": e.distance_meters,
                    "crowd_level": e.crowd_level, "reliability": e.reliability,
                    "is_bidirectional": e.is_bidirectional,
                }
                for edges in self.adjacency.values()
                for e in edges
                if not e.id.endswith("_rev")  # skip reverse edges in serialization
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TransportGraph:
        """Deserialize graph from dict (Redis cache)."""
        graph = cls()

        for nid, ndata in data.get("nodes", {}).items():
            graph.add_node(GraphNode(**ndata))

        for edata in data.get("edges", []):
            graph.add_edge(GraphEdge(**edata))

        return graph

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance in meters between two points.
        """
        R = 6_371_000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(d_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def _fuzzy_score(query: str, target: str) -> float:
        """Simple fuzzy matching score (0.0 to 1.0)."""
        if query == target:
            return 1.0
        if query in target:
            return 0.8 + (0.2 * len(query) / len(target))
        if target in query:
            return 0.6

        # Character overlap
        common = sum(1 for c in query if c in target)
        if not query:
            return 0.0
        return common / max(len(query), len(target))
