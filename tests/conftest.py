import pytest
from pulsekit.graph import Graph

@pytest.fixture
def graph_instance():
    """Pytest fixture to create a reusable Graph instance for tests."""
    g = Graph()
    g.add_link("A", "B", 
               deterministic={"weight": 10}, 
               random={"time": {"mu": 1, "sigma": 0.5}})
    g.add_link("A", "C", 
               deterministic={"weight": 20}, 
               random={"time": {"mu": 2, "sigma": 0.7}})
    g.add_link("B", "C", 
               deterministic={"weight": 5}, 
               random={"time": {"mu": 3, "sigma": 0.2}})
    return g

@pytest.fixture
def pulse_graph_instance():
    """
    Pytest fixture to create a reusable Graph instance for pulse tests.
    """
    g = Graph()
    g.create_node("1")
    g.create_node("2")
    g.create_node("3")
    g.create_node("4")
    g.create_node("5")
    g.create_node("s")
    g.create_node("e")
    
    g.add_link("s", "1", 
               deterministic={"cost": 2.0}, 
               random={"time": {"mean": 2.0, "variance": 3.0}})
    g.add_link("1", "e", 
               deterministic={"cost": 3.0}, 
               random={"time": {"mean": 2.0, "variance": 0.5}})
    g.add_link("s", "2", 
               deterministic={"cost": 3.0}, 
               random={"time": {"mean": 2.0, "variance": 1.0}})
    g.add_link("2", "e", 
               deterministic={"cost": 5.0}, 
               random={"time": {"mean": 9.0, "variance": 1.0}})
    g.add_link("s", "3", 
               deterministic={"cost": 2.0}, 
               random={"time": {"mean": 1.0, "variance": 0.5}})
    g.add_link("3", "e", 
               deterministic={"cost": 4.0}, 
               random={"time": {"mean": 1.0, "variance": 0.5}})
    g.add_link("s", "4", 
               deterministic={"cost": 1.0}, 
               random={"time": {"mean": 2.0, "variance": 3.0}})
    g.add_link("4", "5", 
               deterministic={"cost": 1.0}, 
               random={"time": {"mean": 3.0, "variance": 3.0}})
    g.add_link("5", "e", 
               deterministic={"cost": 1.0}, 
               random={"time": {"mean": 2.0, "variance": 2.0}})
    return g