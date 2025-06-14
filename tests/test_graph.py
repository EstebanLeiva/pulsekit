import pytest
from pulsekit.graph import Graph

def test_create_node():
    """Test node creation in the graph."""
    g = Graph()
    index = g.create_node("A")
    assert index == 0
    assert g.nodes[0].name == "A"
    assert g.name_to_index["A"] == 0

def test_find_node(graph_instance):
    """Test finding an existing and non-existing node."""
    assert graph_instance.find_node("A") == 0
    assert graph_instance.find_node("D") == -1

def test_find_or_add_node(graph_instance):
    """Test finding an existing node and adding a new one."""
    assert graph_instance.find_or_add_node("B") == 1
    new_index = graph_instance.find_or_add_node("D")
    assert new_index == 3
    assert graph_instance.nodes[3].name == "D"

def test_add_link():
    """Test adding a link to the graph."""
    g = Graph()
    g.add_link("A", "B", 
               deterministic={"weight": 15}, 
               random={"time": {"mu": 1.5, "sigma": 0.6}})
    
    u = g.find_node("A")
    v = g.find_node("B")
    
    assert v in g.nodes[u].links
    link = g.nodes[u].links[v]
    
    assert link.deterministic["weight"] == 15
    assert link.random["time"]["mu"] == 1.5

def test_get_links_info(graph_instance):
    """Test retrieving link information from the graph."""
    links_info = graph_instance.get_links_info()
    
    # Node indices for A, B, C are 1, 2, 3
    assert (0, 1) in links_info
    assert (0, 2) in links_info
    assert (1, 2) in links_info
    
    det, rand = links_info[(0, 1)]
    assert det["weight"] == 10
    assert rand["time"]["sigma"] == 0.5

def test_reverse_graph(graph_instance):
    """Test reversing the graph."""
    reversed_g = graph_instance.reverse_graph()
    
    assert len(reversed_g.nodes) == len(graph_instance.nodes)
    assert reversed_g.name_to_index == graph_instance.name_to_index

    u_rev, v_rev = reversed_g.find_node("B"), reversed_g.find_node("A")
    assert v_rev in reversed_g.nodes[u_rev].links
    
    original_link = graph_instance.nodes[0].links[1]
    reversed_link = reversed_g.nodes[u_rev].links[v_rev]
    
    assert original_link.deterministic == reversed_link.deterministic
    assert original_link.random == reversed_link.random

def test_get_link_keys(graph_instance):
    """Test getting deterministic and random keys from links."""
    det_keys, rand_keys = graph_instance.get_link_keys()
    
    assert det_keys == ["weight"]
    assert "time" in rand_keys
    assert rand_keys["time"] == ["mu", "sigma"]