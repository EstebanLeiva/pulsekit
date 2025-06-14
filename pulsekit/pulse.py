from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Callable
import heapq
from collections import defaultdict
from pulsekit.graph import Graph, Link
from pulsekit.dijkstra import dijkstra

PriorityQueue = List[Tuple[float, Any]]

@dataclass
class Parameters:
    """
    Stores the parameters for the Pulse algorithm.

    Attributes:
        graph: The graph to be used in the algorithm.
        source_node: The index of the source node in the graph.
        target_node: The index of the target node in the graph.
        constants: A dictionary of constant values used in the algorithm.
        max_pulse_depth: The maximum depth of the pulse search.
        deterministic_weights: A list of deterministic weights to be used in the algorithm.
        random_weights: A dictionary mapping random variable names to lists of weights.
        prep_deterministic_weights: A list of deterministic weights for preprocessing.
        prep_random_weights: A dictionary mapping random variable names to lists of weights for preprocessing.
        exploration_order: A callable that defines the order in which nodes are explored.
        pruning_functions: A list of functions used to prune paths during exploration.
    """
    graph: Graph
    source_node: int
    target_node: int
    constants: Dict[str, float]
    max_pulse_depth: int
    deterministic_weights: List[str]
    random_weights: Dict[str, List[str]]
    prep_deterministic_weights: List[str]
    prep_random_weights: Dict[str, List[str]]
    info_update: Callable
    pulse_score: Callable
    exploration_order: Callable
    pruning_functions: List[Callable]

@dataclass
class Preprocessing:
    """
    Stores pre-calculated information, like the results from running
    Dijkstra's algorithm, to be used in pruning.

    Attributes:
        deterministic: A dictionary mapping deterministic weights to their pre-calculated costs.
        random: A dictionary mapping random variable names to dictionaries of their pre-calculated costs.
    """
    deterministic: Dict[str, List[float]]
    random: Dict[str, Dict[str, List[float]]]

@dataclass
class PathInformation:
    """
    Stores all relevant information about a path being explored.

    Attributes:
        deterministic: A dictionary mapping deterministic weights to their current values.
        random: A dictionary mapping random variable names to dictionaries of their current values.
        path: A list of node indices representing the current path being explored.
    """
    deterministic: Dict[str, float]
    random: Dict[str, Dict[str, float]]
    path: List[int] = field(default_factory=list)

class Pulse:
    """
    The main class that orchestrates the Pulse Algorithm. It holds the state,
    parameters, and core logic for finding the optimal path.

    Attributes:
        parameters: An instance of Parameters containing the algorithm's configuration.
        preprocessing: An instance of Preprocessing containing pre-calculated costs.
        dominance: A dictionary to track labels for dominance pruning.
        pulse_queue: A priority queue to manage paths being explored.
        optimal_path: The best path found during the search.
        optimal_objective: The objective value of the optimal path.
        current_optimal_path: The currently best path being explored.
        current_optimal_objective: The objective value of the currently best path.
        instance_info: A dictionary to store instance-specific information.
    """

    def __init__(self, parameters: Parameters):
        self.parameters = parameters

        # --- Validate that the weights specified in parameters exist in the graph ---
        det_keys, random_keys = self.parameters.graph.get_link_keys()
        if not set(self.parameters.prep_deterministic_weights).issubset(det_keys):
            raise ValueError(f"Deterministic weights for preprocessing are not valid. Choose from: {det_keys}")

        def is_dict_subset(sub_dict, super_dict):
            """Helper to check if one dictionary of lists is a subset of another."""
            for key, values in sub_dict.items():
                if key not in super_dict or not set(values).issubset(super_dict[key]):
                    return False
            return True

        if not is_dict_subset(self.parameters.prep_random_weights, random_keys):
             raise ValueError("Random weights for preprocessing are not valid.")

        self.preprocessing = Preprocessing(deterministic={}, random={})
        self.dominance = {}
        self.pulse_queue: PriorityQueue = []
        self.optimal_path: List[int] = []
        self.optimal_objective: float = float('inf')
        self.current_optimal_path: List[int] = []
        self.current_optimal_objective: float = float('inf')
        self.instance_info: Dict[str, int] = defaultdict(int)

    def _order_nodes(self, link_dict: Dict[int, Link]) -> List[int]:
        """Sorts neighboring nodes based on the exploration_order function."""
        return sorted(link_dict.keys(), key=lambda node_idx: self.parameters.exploration_order(self, node_idx))
    
    def preprocess(self):
        """Runs preprocessing algorithms (e.g., Dijkstra) to aid in pruning."""

        graph = self.parameters.graph
        source, target = self.parameters.source_node, self.parameters.target_node

        for cost in self.parameters.prep_deterministic_weights:
            costs_from_target = dijkstra(graph, target, cost_key=cost)
            self.preprocessing.deterministic[cost] = costs_from_target
            if costs_from_target[source] == float('inf'):
                raise RuntimeError("Source node not reachable from target")

        for rand_var, costs in self.parameters.prep_random_weights.items():
            self.preprocessing.random[rand_var] = {}
            for cost in costs:
                costs_from_target = dijkstra(graph, target, rand_var=rand_var, cost_key=cost)
                self.preprocessing.random[rand_var][cost] = costs_from_target
                if costs_from_target[source] == float('inf'):
                    raise RuntimeError("Source node not reachable from target")

    def _propagate_pulse(
        self,
        current_node: int,
        current_path_info: PathInformation,
        current_depth: int
    ):
        """Recursively explores paths from the current node, applying pruning.
        
        Args:
            current_node: The index of the current node in the graph.
            current_path_info: The PathInformation object containing the current path and weights.
            current_depth: The current depth in the pulse search.
        """
        pruned = any(prune(self, 
                           current_node, 
                           current_path_info) for prune in self.parameters.pruning_functions)

        if not pruned:
            current_path_info.path.append(current_node)
            link_dict = self.parameters.graph.nodes[current_node].links
            if current_node != self.parameters.target_node:
                if current_depth < self.parameters.max_pulse_depth:
                    ordered_reachable_nodes = self._order_nodes(link_dict)
                    for reachable_node in ordered_reachable_nodes:
                        if reachable_node not in current_path_info.path:
                            new_path = current_path_info.path.copy()
                            new_determistic_info, new_random_info = self.parameters.info_update(self.parameters.graph,
                                                                                                current_node,
                                                                                                reachable_node,
                                                                                                new_path,
                                                                                                current_path_info.deterministic.copy(),
                                                                                                current_path_info.random.copy())
                            new_path_info = PathInformation(new_determistic_info, new_random_info, path=new_path)
                            self._propagate_pulse(reachable_node, 
                                                  new_path_info, 
                                                  current_depth + 1)
            else:
                score = self.parameters.pulse_score(self, current_path_info)
                heapq.heappush(self.pulse_queue, (score, current_path_info))
    def run(
        self,
        init_optimal_path: Optional[List[int]] = [],
        init_objective: float = float('inf')
    ):
        """Main method to execute the pulse algorithm.
        
        Args:
            init_optimal_path: An initial path to start the search from.
            init_objective: The initial objective value for the optimal path.
        """
        self.current_optimal_path = init_optimal_path
        self.current_optimal_objective = init_objective

        initial_path_info = PathInformation(
            deterministic={key: 0.0 for key in self.parameters.deterministic_weights},
            random={rand_var: {key: 0.0 for key in keys} for rand_var, keys in self.parameters.random_weights.items()}
        )

        self._propagate_pulse(self.parameters.source_node, initial_path_info, 0)

        while len(self.pulse_queue) > 0:
            _, explore_path_info = heapq.heappop(self.pulse_queue)
            link_dict = self.parameters.graph.nodes[explore_path_info.path[-1]].links
            ordered_reachable_nodes = self._order_nodes(link_dict)
            for reachable_node in ordered_reachable_nodes:
                if reachable_node not in explore_path_info.path:
                    new_path = explore_path_info.path.copy()
                    new_deterministic_info, new_random_info = self.parameters.info_update(
                        self.parameters.graph,
                        explore_path_info.path[-1],
                        reachable_node,
                        new_path,
                        explore_path_info.deterministic.copy(),
                        explore_path_info.random.copy()
                    )
                    new_path_info = PathInformation(new_deterministic_info, new_random_info, new_path)
                    self._propagate_pulse(reachable_node, new_path_info, 0)

        self.optimal_path = self.current_optimal_path
        self.optimal_objective = self.current_optimal_objective