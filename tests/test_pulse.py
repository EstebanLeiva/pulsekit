import math
from scipy.stats import norm
from pulsekit.pulse import Pulse, Parameters
from pulsekit.graph import Graph
from typing import Tuple, List

def get_path_distribution(graph: Graph, path: List[int]) -> Tuple:
    """
    Computes the distribution of a given path in the graph.

    Args:
        graph: The Graph object.
        path: A list of node indices representing the path.
    
    Returns:
        A tuple containing the mean and variance of the path's random variables.
    """
    mean = 0.0
    variance = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        link = graph.nodes[u].links[v]
        
        mean += link.random["time"]["mean"]
        variance += link.random["time"]["variance"]

    return mean, variance

def info_update(graph, current_node, reachable_node, path, deterministic_info, random_info):
    """
    Updates path information when traversing a link.

    Args:
        graph: The graph instance.
        current_node: The starting node of the link.
        reachable_node: The ending node of the link.
        path: The current path (list of node indices).
        deterministic_info: Dictionary of deterministic path properties.
        random_info: Dictionary of random path properties.

    Returns:
        A tuple containing the updated deterministic and random info dictionaries.
    """
    link = graph.nodes[current_node].links[reachable_node]

    deterministic_info["cost"] += link.deterministic["cost"]
    random_info["time"]["mean"] += link.random["time"]["mean"]
    random_info["time"]["variance"] += link.random["time"]["variance"]

    return deterministic_info, random_info


def prune_feasibility(pulse_alg, current_node, current_path_info):
    """
    Prunes a path if it's not feasible based on probabilistic constraints.

    Args:
        pulse_alg: The Pulse algorithm instance.
        current_node: The current node being evaluated.
        current_path_info: The current path information.

    Returns:
        True if the path should be pruned, False otherwise.
    """
    random_info = current_path_info.random

    T_max = pulse_alg.parameters.constants["T_max"]
    alpha = pulse_alg.parameters.constants["alpha"]
    
    mean = random_info["time"]["mean"] + pulse_alg.preprocessing.random["time"]["mean"][current_node]
    variance = random_info["time"]["variance"] + pulse_alg.preprocessing.random["time"]["variance"][current_node]

    dist = norm(loc=mean, scale=math.sqrt(variance))
    prob = dist.cdf(T_max)

    if T_max >= mean and prob < alpha:
        return True
    if T_max < mean and alpha > 0.5:
        return True

    return False


def prune_bounds(pulse_alg, current_node, current_path_info):
    """
    Prunes a path if its cost exceeds the current best. Updates the best path
    if a better solution is found at the target.

    Args:
        pulse_alg: The Pulse algorithm instance.
        current_node: The current node being evaluated.
        current_path_info: The current path information.

    Returns:
        True if the path should be pruned, False otherwise.
    """
    current_path = current_path_info.path
    deterministic_info = current_path_info.deterministic
    
    if deterministic_info["cost"] + pulse_alg.preprocessing.deterministic["cost"][current_node] > pulse_alg.current_optimal_objective:
        return True
    
    if current_node == pulse_alg.parameters.target_node:
        if deterministic_info["cost"] < pulse_alg.current_optimal_objective:
            pulse_alg.current_optimal_objective = deterministic_info["cost"]
            new_path = current_path.copy()
            new_path.append(current_node)
            pulse_alg.current_optimal_path = new_path
            
    return False


def exploration_order(pulse_alg, node):
    """
    Defines the order in which to explore neighboring nodes.

    Args:
        pulse_alg: The Pulse algorithm instance.
        node: The node index.

    Returns:
        The pre-calculated cost to reach the target from the given node.
    """
    return pulse_alg.preprocessing.deterministic["cost"][node]


def pulse_score(pulse_alg, current_path_info):
    """
    Scores a path to determine its priority in the pulse queue.

    Args:
        pulse_alg: The Pulse algorithm instance.
        current_path_info: The current path information.

    Returns:
        The score of the path.
    """
    return pulse_alg.preprocessing.deterministic["cost"][current_path_info.path[-1]]

def test_sarp(pulse_graph_instance):
    """
    Test the SARP algorithm on a predefined graph instance.
    
    Args:
        pulse_graph_instance: A fixture providing a graph instance for testing.
    """
    target_index = pulse_graph_instance.find_node("e")
    source_index = pulse_graph_instance.find_node("s")

    parameters = Parameters(
        graph=pulse_graph_instance,
        source_node=source_index,
        target_node=target_index,
        constants={
            "T_max": 10.0,
            "alpha": 0.9
        },
        max_pulse_depth=1000,
        deterministic_weights=["cost"],
        random_weights={"time": ["mean", "variance"]},
        prep_deterministic_weights=["cost"],
        prep_random_weights={"time": ["mean", "variance"]},
        info_update=info_update,
        pulse_score=pulse_score,
        exploration_order=exploration_order,
        pruning_functions=[
            prune_feasibility,
            prune_bounds
        ]
    )
    
    pulse_alg = Pulse(parameters)
    pulse_alg.preprocess()
    pulse_alg.run()

    optimal_path = pulse_alg.optimal_path
    optimal_cost = pulse_alg.optimal_objective

    ind_1 = pulse_graph_instance.find_node("1")

    mean, variance = get_path_distribution(pulse_graph_instance, optimal_path)
    reliability = norm(loc=mean, scale=math.sqrt(variance)).cdf(parameters.constants["T_max"])

    assert optimal_path == [source_index, ind_1, target_index]
    assert math.isclose(optimal_cost, 5.0, rel_tol=1e-9)
    assert reliability >= 0.99