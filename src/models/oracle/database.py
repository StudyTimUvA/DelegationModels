import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..base import database as BaseDatabase

class Database(BaseDatabase.Database):
    """
    Database class for managing evidence and revocations.
    Inherits from the base Database class.
    """

    def __init__(self):
        super().__init__()
        
        self.graph = nx.DiGraph()

    def add_party(self, party_id: str):
        """
        Add a party to the database.

        Params:
            party_id: the ID of the party to be added.
        """
        if party_id not in self.graph:
            self.graph.add_node(party_id)
        else:
            raise ValueError(f"Party with ID {party_id} already exists.")
        
    def add_delegation(self, delegator_id: str, delegatee_id: str, resources: List[str], actions: List[str], expires: datetime):
        """
        Add a delegation to the database.

        Params:
            delegator_id: the ID of the delegator.
            delegatee_id: the ID of the delegatee.
            resource: the resources being delegated.
            expires: the expiration date of the delegation.
        """
        if not self.graph.has_node(delegator_id):
            raise ValueError(f"Delegator with ID {delegator_id} does not exist.")
        if not self.graph.has_node(delegatee_id):
            raise ValueError(f"Delegatee with ID {delegatee_id} does not exist.")
        
        self.graph.add_edge(delegator_id, delegatee_id, resources=resources, expires=expires, actions=actions)

    def visualize_graph(self, filename: str):
        """
        Visualize the graph and save it to a file.

        Params:
            filename: the name of the file to save the graph to.
        """
        pos = nx.spring_layout(self.graph, k=1)
        nx.draw(self.graph, pos, with_labels=True)
        edge_labels = {
            (u,v): f"{','.join(d.get('resources'))}\n({','.join(d.get('actions'))})"
            for u,v,d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)
        plt.title("Oracle Delegation Graph")
        plt.axis("off")
        plt.savefig(filename)
