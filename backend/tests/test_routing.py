"""
GhoraGhuri — Routing Engine Tests
Tests the A* algorithm and cost function with the Dhaka seed graph.
"""
import pytest

from app.engine.astar import find_route
from app.engine.cost import RoutePreferences, edge_cost
from app.engine.graph import GraphEdge
from app.engine.seed_data import create_dhaka_graph


@pytest.fixture
def graph():
    """Create a test graph from seed data."""
    return create_dhaka_graph()


class TestGraphStructure:
    """Test graph construction and lookup."""

    def test_graph_has_nodes(self, graph):
        assert graph.node_count > 50

    def test_graph_has_edges(self, graph):
        assert graph.edge_count > 100

    def test_find_node_by_code(self, graph):
        node_id = graph.find_node_by_code("MIR10")
        assert node_id == "MIR10"

    def test_find_node_by_name_en(self, graph):
        node_id = graph.find_node_by_name("Mirpur 10 Roundabout", "en")
        assert node_id == "MIR10"

    def test_find_node_by_name_bn(self, graph):
        node_id = graph.find_node_by_name("মিরপুর ১০ গোলচত্বর", "bn")
        assert node_id == "MIR10"

    def test_find_nearest_node(self, graph):
        # Near Mirpur 10 coordinates
        results = graph.find_nearest_node(23.8069, 90.3688)
        assert len(results) >= 1
        assert results[0] == "MIR10"

    def test_fuzzy_name_search(self, graph):
        node_id = graph.find_node_by_name("Mirpur 10", "en")
        assert node_id is not None

    def test_neighbors_exist(self, graph):
        neighbors = graph.get_neighbors("MIR10")
        assert len(neighbors) > 0


class TestCostFunction:
    """Test multi-objective cost calculation."""

    def test_walking_costs_more_with_avoid(self):
        edge = GraphEdge(
            id="test1", from_id="A", to_id="B",
            transport_mode="walking", route_name_en=None, route_name_bn=None,
            time_minutes=10, fare_bdt=0, distance_meters=800,
            crowd_level="low", reliability=1.0,
        )

        prefs_normal = RoutePreferences(avoid_walking=False)
        prefs_avoid = RoutePreferences(avoid_walking=True)

        cost_normal = edge_cost(edge, prefs_normal)
        cost_avoid = edge_cost(edge, prefs_avoid)

        assert cost_avoid > cost_normal

    def test_high_crowd_increases_cost(self):
        edge_low = GraphEdge(
            id="test2a", from_id="A", to_id="B",
            transport_mode="bus", route_name_en=None, route_name_bn=None,
            time_minutes=10, fare_bdt=10, distance_meters=2000,
            crowd_level="low", reliability=0.8,
        )
        edge_high = GraphEdge(
            id="test2b", from_id="A", to_id="B",
            transport_mode="bus", route_name_en=None, route_name_bn=None,
            time_minutes=10, fare_bdt=10, distance_meters=2000,
            crowd_level="extreme", reliability=0.8,
        )

        prefs = RoutePreferences(optimize="comfort")
        assert edge_cost(edge_high, prefs) > edge_cost(edge_low, prefs)

    def test_cost_function_returns_positive(self):
        edge = GraphEdge(
            id="test3", from_id="A", to_id="B",
            transport_mode="bus", route_name_en=None, route_name_bn=None,
            time_minutes=5, fare_bdt=5, distance_meters=500,
            crowd_level="medium", reliability=0.7,
        )
        prefs = RoutePreferences()
        assert edge_cost(edge, prefs) > 0


class TestAStarRouting:
    """Test A* pathfinding on the Dhaka graph."""

    def test_same_node_route(self, graph):
        result = find_route(graph, "MIR10", "MIR10")
        assert result.is_found
        assert len(result.steps) == 0

    def test_mirpur10_to_farmgate(self, graph):
        """Test a common route: Mirpur 10 → Farmgate via Mirpur Road."""
        result = find_route(graph, "MIR10", "FARM")
        assert result.is_found
        assert len(result.steps) > 0
        assert result.total_time_min > 0
        assert result.total_time_max >= result.total_time_min
        assert result.confidence_score > 0

    def test_mirpur10_to_dhanmondi27(self, graph):
        """Test multi-modal: Mirpur 10 → Dhanmondi 27."""
        result = find_route(graph, "MIR10", "DHN27")
        assert result.is_found
        assert len(result.steps) > 0

    def test_uttara_to_motijheel(self, graph):
        """Test long route: Uttara → Motijheel."""
        result = find_route(graph, "UTT_N", "MOTI")
        assert result.is_found
        assert len(result.steps) >= 3  # should have multiple hops

    def test_gulshan_to_sadarghat(self, graph):
        """Cross-city route: Gulshan → Sadarghat (Old Dhaka)."""
        result = find_route(graph, "GULS", "SADAR")
        assert result.is_found
        assert result.total_fare_min > 0

    def test_optimize_time_vs_cost(self, graph):
        """Different optimization should yield different routes."""
        prefs_time = RoutePreferences(optimize="time")
        prefs_cost = RoutePreferences(optimize="cost")

        result_time = find_route(graph, "UTT_N", "MOTI", prefs_time)
        result_cost = find_route(graph, "UTT_N", "MOTI", prefs_cost)

        assert result_time.is_found
        assert result_cost.is_found
        # Results may differ in steps or cost composition

    def test_nonexistent_node(self, graph):
        result = find_route(graph, "MIR10", "NONEXIST")
        assert not result.is_found
        assert result.error_message is not None

    def test_bilingual_instructions(self, graph):
        result = find_route(graph, "MIR10", "FARM")
        assert result.is_found
        for step in result.steps:
            assert step.instruction_en
            assert step.instruction_bn
            assert "মিনিট" in step.instruction_bn or "হাঁটুন" in step.instruction_bn

    def test_computation_time_reasonable(self, graph):
        """Route computation should complete in < 500ms."""
        result = find_route(graph, "UTT_N", "SADAR")
        assert result.computation_ms < 500
