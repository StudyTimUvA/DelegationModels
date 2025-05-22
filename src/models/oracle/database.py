import networkx as nx
import matplotlib.pyplot as plt
from typing import List

from ..base import database as BaseDatabase


class Database(BaseDatabase.Database):
    """
    Database class for managing evidence and revocations.
    Inherits from the base Database class.
    """

    def __init__(self):
        super().__init__()

        self.graph = nx.MultiDiGraph()

    def add_parties(self, party_ids: List[str]):
        """
        Add multiple parties to the database.

        Params:
            party_ids: a list of party IDs to be added.
        """
        for party_id in party_ids:
            if not self.graph.has_node(party_id):
                self.graph.add_node(party_id)

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
            (u, v): f"{','.join(d.get('resources'))}\n({','.join(d.get('actions'))})"
            for u, v, d in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)
        plt.title("Oracle Delegation Graph")
        plt.axis("off")
        plt.savefig(filename)
