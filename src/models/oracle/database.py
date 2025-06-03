import networkx as nx
import matplotlib.pyplot as plt
from typing import List
from collections import deque

from ..base import database as BaseDatabase
from . import evidence


class Bridge:
    def __init__(self, identifier, from_node, to_node, objects, rights):
        self.id = identifier
        self.from_node = from_node
        self.to_node = to_node
        self.objects = objects
        self.rights = rights


class Database(BaseDatabase.Database):
    """
    Database class for managing evidence and revocations.
    Inherits from the base Database class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.graph = nx.MultiDiGraph()
        self.outgoing_bridges = {
            # node -> list[Bridge]
        }

    def visualize_graph(self, filename: str):
        """
        Visualize the graph and save it to a file.

        Params:
            filename: the name of the file to save the graph to.
        """
        # pos = nx.spring_layout(self.graph, k=1.5)
        pos = nx.circular_layout(self.graph, scale=1.5)
        nx.draw(self.graph, pos, with_labels=True)
        edge_labels = {
            (u, v): f"{','.join(d.get('objects', []))}\n({','.join(d.get('rights', []))})"
            for u, v, d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)
        plt.title("Oracle Delegation Graph")
        plt.axis("off")
        plt.savefig(filename)
        
    def add_node(self, node):
        self.graph.add_node(node)

    def add_parties(self, nodes: List[str]):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, u, v, objects: List[str], rights=None):
        if not self.graph.has_node(u):
            raise ValueError(f"Node '{u}' does not exist in the graph.")
        
        identifier = self.get_next_identifier()

        if not self.graph.has_node(v): # Create a bridge
            self.outgoing_bridges[u] = self.outgoing_bridges.get(u, [])
            self.outgoing_bridges[u].append(Bridge(identifier, u, v, objects, rights))
            return evidence.Evidence(identifier)
        
        # Add an edge in the local graph
        self.graph.add_edge(u, v, id=identifier, objects=objects, rights=rights or [])
        return evidence.Evidence(identifier)
    
    def _in_graph_path_valid(self, owner_id, party_id, resource, action):
        paths = list(nx.all_simple_paths(self.graph, source=owner_id, target=party_id))
        for path in paths:
            valid_path = True
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.graph.get_edge_data(u, v)

                if edge_data is None:
                    valid_path = False
                    break
                edge_data = edge_data[0] 

                if edge_data.get('id') is None:
                    valid_path = False
                    break
                if edge_data.get('id') in self.revocations:
                    valid_path = False
                    break
                if resource not in edge_data.get('objects', []) or action not in edge_data.get('rights', []):
                    valid_path = False
                    break

            if valid_path:
                return True
            
        return False


    def _build_recursive_graph(self, party_id, resource, action, visited=None):
        """Recursively build a graph using the graph, to find all root parties that can access the resource with the action."""
        if visited is None:
            visited = set()
        if party_id in visited:
            return []
        
        visited.add(party_id)
        roots = []

        if self.graph.has_node(party_id):
            for u in self.graph.predecessors(party_id):
                edge_data_list = self.graph.get_edge_data(u, party_id)
                if not edge_data_list:
                    continue

                valid_edge = any(
                    edge.get("id") not in self.revocations and
                    resource in edge.get("objects", []) and
                    action in edge.get("rights", [])
                    for edge in edge_data_list.values()
                )
                if not valid_edge:
                    continue

                roots.extend(self._build_recursive_graph(u, resource, action, visited))

        if not roots:
            roots.append(party_id)
        
        return roots


    def has_access(self, party_id: str, owner_id: str, resource: str, action: str):
        """Need to find a path from owner_id to party_id.
        
        Returns True if there is a valid path between the owner and party with the correct resource and action.

        If there is no complete path, a list of parties is returned that, if any of them has access, the party_id will have access as well.
        """

        # Check if there is a path in the current graph (single AR)
        nodes_in_graph = self.graph.has_node(owner_id) and self.graph.has_node(party_id)
        if nodes_in_graph and nx.has_path(self.graph, owner_id, party_id):
            if self._in_graph_path_valid(owner_id, party_id, resource, action):
                return True
                
        # No complete path found, utilize bridges
        return self._build_recursive_graph(party_id, resource, action)
    
    def has_bridges_to(self, node):
        """Check if there are any outgoing bridges from the given node."""
        return node in self.outgoing_bridges and len(self.outgoing_bridges[node]) > 0


class DatabaseBroker(BaseDatabase.DatabaseBroker):
    """
    Database broker for the Oracle model.
    Inherits from the base DatabaseBroker class.
    """
    def add_link(self, from_db, from_node, to_node, objects, actions):
        if from_db not in self.databases:
            raise ValueError(f"Source DB {from_db} not registered.")
        
        return self.databases[from_db].add_edge(
            from_node, to_node, objects=objects or [], rights=actions or []
        )

    def has_access(self, party_id: str, owner_id: str, resource: str, action: str, db_name: str) -> bool:
        """Check if a party has access to a resource with a specific action."""
        db = self.databases.get(db_name)
        access_or_roots = db.has_access(party_id, owner_id, resource, action)

        if access_or_roots is True:
            return True
        
        # If the direct access check fails, recursively check for access through bridges
        for db in self.databases.values():
            for root in access_or_roots:
                if db.has_bridges_to(root):
                    found = self.has_access(
                        party_id=root,
                        owner_id=root,
                        resource=resource,
                        action=action,
                        db_name=db.name
                    )
                    if found:
                        return True
                    
        return False
    

