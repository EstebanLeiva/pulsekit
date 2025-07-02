from pulsekit.dijkstra import dijkstra, dijkstra_between_nodes

def test_dijkstra(pulse_graph_instance):
    """Test Dijkstra's algorithm on a simple graph."""
    target_node = pulse_graph_instance.find_node("e")
    costs = dijkstra(pulse_graph_instance, target_node=target_node, cost_key="cost")
    cost_sol = [3.0, 5.0, 4.0, 2.0, 1.0, 3.0, 0.0]
    assert len(costs) == len(pulse_graph_instance.nodes)
    for i, cost in enumerate(costs):
        assert cost == cost_sol[i], f"Cost mismatch at node {i}: expected {cost_sol[i]}, got {cost}"

    means = dijkstra(pulse_graph_instance, target_node=target_node, cost_key="mean", rand_var="time")
    mean_sol = [2.0, 9.0, 1.0, 5.0, 2.0, 2.0, 0.0]
    assert len(means) == len(pulse_graph_instance.nodes)
    for i, mean in enumerate(means):
        assert mean == mean_sol[i], f"Mean mismatch at node {i}: expected {mean_sol[i]}, got {mean}"

def test_dijkstra_between_nodes(pulse_graph_instance):
    """Test Dijkstra's algorithm for a specific path between two nodes."""
    start_node = pulse_graph_instance.find_node("s")
    target_node = pulse_graph_instance.find_node("e")
    path, cost = dijkstra_between_nodes(pulse_graph_instance, start_node=start_node, target_node=target_node, cost_key="cost")
    
    expected_path = [5, 3, 4, 6]
    assert path == expected_path, f"Path mismatch: expected {expected_path}, got {path}"
    expected_cost = 0
    for i in range(len(expected_path) - 1):
        u = expected_path[i]
        v = expected_path[i + 1]
        expected_cost += pulse_graph_instance.nodes[u].links[v].deterministic["cost"]
    assert cost == expected_cost, f"Cost mismatch: expected {expected_cost}, got {cost}"

    costs = dijkstra(pulse_graph_instance, target_node=target_node, cost_key="cost")
    assert costs[start_node] == cost, f"Cost from start node {start_node} to target node {target_node} should match the path cost, expected {cost}, got {costs[start_node]}"