from dataclasses import dataclass, field
from typing import Dict, List, Tuple, DefaultDict
from collections import defaultdict

@dataclass
class Link:
    """
    Simple link structure with deterministic and random link information.
    
    Attributes:
        deterministic: Dictionary holding deterministic link information.
        random: Dictionary holding random link information.
    """
    deterministic: Dict[str, float]
    random: Dict[str, Dict[str, float]]

@dataclass
class Node:
    """
    Simple node structure.
    
    Attributes:
        name: The name of the node.
        links: A dictionary mapping destination node indices to Link objects.
    """
    name: str
    links: Dict[int, Link] = field(default_factory=dict)

class Graph:
    """
    Simple graph structure.
    
    Attributes:
        nodes: A dictionary mapping node indices to Node objects.
        name_to_index: A dictionary mapping node names to their indices.
        covariance: A defaultdict for storing covariance information.
    """
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.name_to_index: Dict[str, int] = {}
        self.covariance: Dict[str, DefaultDict] = defaultdict(int)

    def create_node(self, name: str) -> int:
        """
        Create a new node in the graph.
        
        If an index is not provided, it's auto-incremented.
        
        Args:
            name: The name of the node.
            index: An optional specific index for the new node.
            
        Returns:
            The index of the newly created node.
        """
        n = len(self.nodes)
        node = Node(name=name)
        self.nodes[n] = node
        self.name_to_index[name] = n
        return n

    def find_node(self, name: str) -> int:
        """
        Find the node index given the node name.
        
        Args:
            name: The name of the node to find.
            
        Returns:
            The index of the node, or -1 if not found.
        """
        return self.name_to_index.get(name, -1)

    def find_or_add_node(self, name: str) -> int:
        """
        Find the node index given the node name. If the node does not exist, create a new one.
        
        Args:
            name: The name of the node.
            index: An optional index to use if the node is created.
            
        Returns:
            The index of the found or newly created node.
        """
        n = self.find_node(name)
        if n < 0:
            n = self.create_node(name)
        return n

    def add_link(
        self,
        src_name: str,
        dst_name: str,
        deterministic: Dict[str, float],
        random: Dict[str, Dict[str, float]]):
        """
        Add a link between two nodes.
        
        Args:
            src_name: Name of the source node.
            dst_name: Name of the destination node.
            deterministic: Dictionary of deterministic link attributes.
            random: Dictionary of random link attributes.
        """
        u = self.find_or_add_node(src_name)
        v = self.find_or_add_node(dst_name)
        self.nodes[u].links[v] = Link(deterministic, random)

    def get_links_info(self) -> Dict[Tuple[int, int], Tuple[Dict[str, float], Dict[str, Dict[str, float]]]]:
        """
        Return a dictionary with the link information.
        
        Returns:
            A dictionary where keys are (source_node, dest_node) tuples and
            values are tuples containing the deterministic and random dictionaries.
        """
        links = {}
        for u, node in self.nodes.items():
            for v, link in node.links.items():
                links[(u, v)] = (link.deterministic, link.random)
        return links

    def reverse_graph(self) -> 'Graph':
        """
        Creates a new graph that is the reverse of the current one.
        
        Returns:
            A new Graph instance with all links reversed.
        """
        new_graph = Graph()
        # First, create all nodes in the new graph to ensure they exist
        for u, node in self.nodes.items():
            new_graph.create_node(node.name)
        
        # Second, add the reversed links
        for u, node in self.nodes.items():
            for v, link in node.links.items():
                src_name_rev = self.nodes[v].name
                dst_name_rev = self.nodes[u].name
                new_graph.add_link(
                    src_name=src_name_rev, 
                    dst_name=dst_name_rev, 
                    deterministic=link.deterministic,
                    random=link.random)
        return new_graph
    
    def get_link_keys(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Gets the keys used in the deterministic and random attribute dictionaries
        from the first link found in the graph.
        
        Returns:
            A tuple containing a list of deterministic keys and a dictionary of
            random variable keys to their attribute keys. Returns empty
            structures if the graph has no links.
        """
        for node in self.nodes.values():
            if node.links:
                # Get the first link from the dictionary of links
                first_link = next(iter(node.links.values()))
                
                det_keys = list(first_link.deterministic.keys())
                random_variables = list(first_link.random.keys())
                
                rand_keys: Dict[str, List[str]] = {}
                for random_variable in random_variables:
                    rand_keys[random_variable] = list(first_link.random[random_variable].keys())
                    
                return det_keys, rand_keys
                
        return [], {}