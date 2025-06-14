import heapq
import numpy as np
from typing import Dict, List, Optional, Tuple, Union

from pulsekit.graph import Graph

def dijkstra(
    graph: Graph,
    target_node: int,
    cost_key: str,
    rand_var: Optional[str] = None,
) -> List[float]:
    """
    Calculates shortest paths from all nodes to a single target_node using Dijkstra's algorithm.
    
    This function runs the algorithm on a reversed graph to find the shortest paths
    towards the target. It can handle both deterministic and random costs.

    Args:
        graph: The Graph object to run the algorithm on.
        target_node: The index of the destination node.
        cost_key: The key for the cost attribute in the Link's data dictionary.
        rand_var: If provided, specifies the random variable key. The cost_key will
                  then be looked up within this random variable's dictionary.

    Returns:
        A list of costs from each node to the target_node. The index corresponds to the node ID.
        If no path exists, the cost will be float('inf') for that node.
    """
    reversed_graph = graph.reverse_graph()
    n = len(reversed_graph.nodes)
    cost = np.full((n,), float('inf'))
    cost[target_node] = 0.0
    queue = [(0.0, target_node)]
    predecessors = np.full((n,), -1)

    while len(queue) > 0:
        current_cost, current_node = heapq.heappop(queue)
        if current_cost > cost[current_node]:
            continue
        for neighbor, link in reversed_graph.nodes[current_node].links.items():
            if rand_var == None:
                link_cost = link.deterministic[cost_key]
            else:
                link_cost = link.random[rand_var][cost_key]
            new_cost = current_cost + link_cost
            if new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (new_cost, neighbor))
    return cost


def dijkstra_between_nodes(
    graph: Graph,
    start_node: int,
    target_node: int,
    cost_key: str,
    rand_var: Optional[str] = None
) -> Tuple[List[int], float]:
    """
    Calculates the single shortest path from a start_node to a target_node.

    Args:
        graph: The Graph object.
        start_node: The index of the starting node.
        target_node: The index of the destination node.
        cost_key: The key for the cost attribute in the Link's data dictionary.
        rand_var: If provided, specifies the random variable key.

    Returns:
        A list of node IDs representing the shortest path from start to target.
        Returns an empty list if no path exists.
    """
    reversed_graph = graph.reverse_graph()
    n = len(reversed_graph.nodes)
    cost = np.full((n,), float('inf'))
    cost[target_node] = 0.0
    queue = [(0.0, target_node)]
    predecessors = np.full((n,), -1)

    while len(queue) > 0:
        current_cost, current_node = heapq.heappop(queue)
        if current_cost > cost[current_node]:
            continue
        if current_node == target_node:
            break
        for neighbor, link in reversed_graph.nodes[current_node].links.items():
            if rand_var:
                link_cost = link.random[rand_var][cost_key]
            else:
                link_cost = link.deterministic[cost_key]
            new_cost = current_cost + link_cost
            if new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (new_cost, neighbor))
    path = []
    u= target_node
    if predecessors[u] != -1 or u == start_node:
        while u != -1:
            path.append(u)
            u = predecessors[u]
    path.reverse()
    return path, cost[start_node]