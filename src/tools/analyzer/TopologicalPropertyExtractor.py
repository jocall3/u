import networkx as nx
import numpy as np
from qiskit import QuantumCircuit

class TopologicalPropertyExtractor:
    """
    Extracts topological properties from quantum circuits represented as graphs.

    This class analyzes the connectivity and structure of quantum circuits to
    derive meaningful topological features. These features can be used for
    circuit classification, optimization, and hardware mapping.
    """

    def __init__(self, circuit: QuantumCircuit):
        """
        Initializes the TopologicalPropertyExtractor with a quantum circuit.

        Args:
            circuit: The Qiskit QuantumCircuit to analyze.
        """
        self.circuit = circuit
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.Graph:
        """
        Builds a graph representation of the quantum circuit.

        Nodes represent qubits, and edges represent entangling gates (e.g., CNOT, CZ).
        """
        graph = nx.Graph()
        for q in range(self.circuit.num_qubits):
            graph.add_node(q)

        for gate in self.circuit.data:
            if len(gate.qubits) == 2:  # Consider only two-qubit gates for entanglement
                q1 = self.circuit.find_bit(gate.qubits[0]).index
                q2 = self.circuit.find_bit(gate.qubits[1]).index
                graph.add_edge(q1, q2)
        return graph

    def get_degree_distribution(self) -> dict:
        """
        Calculates the degree distribution of the graph.

        Returns:
            A dictionary where keys are degrees and values are the number of nodes with that degree.
        """
        degrees = [d for n, d in self.graph.degree()]
        degree_counts = {}
        for degree in degrees:
            if degree in degree_counts:
                degree_counts[degree] += 1
            else:
                degree_counts[degree] = 1
        return degree_counts

    def get_average_degree(self) -> float:
        """
        Calculates the average degree of the graph.
        """
        degrees = [d for n, d in self.graph.degree()]
        return np.mean(degrees) if degrees else 0.0

    def get_density(self) -> float:
        """
        Calculates the density of the graph.

        Density is the ratio of the number of edges to the number of possible edges.
        """
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        if num_nodes <= 1:
            return 0.0
        return 2 * num_edges / (num_nodes * (num_nodes - 1))

    def get_global_clustering_coefficient(self) -> float:
        """
        Calculates the global clustering coefficient of the graph.

        This measures the proportion of closed triplets in the graph.
        """
        return nx.transitivity(self.graph) if self.graph.number_of_edges() > 0 else 0.0

    def get_average_shortest_path_length(self) -> float:
        """
        Calculates the average shortest path length between all pairs of nodes.

        Returns:
            The average shortest path length, or None if the graph is disconnected.
        """
        if not nx.is_connected(self.graph):
            return float('inf')  # Or handle disconnected graphs differently
        return nx.average_shortest_path_length(self.graph)

    def get_diameter(self) -> int:
        """
        Calculates the diameter of the graph.

        The diameter is the longest shortest path between any two nodes.
        """
        if not nx.is_connected(self.graph):
            return -1 # Or handle disconnected graphs differently
        return nx.diameter(self.graph)

    def get_number_of_connected_components(self) -> int:
        """
        Calculates the number of connected components in the graph.
        """
        return nx.number_connected_components(self.graph)

    def get_is_planar(self) -> bool:
        """
        Checks if the graph is planar.

        Note: Planarity testing can be computationally expensive for large graphs.
        """
        try:
            return nx.check_planarity(self.graph)[0]
        except nx.NetworkXException:
            return False  # Handle cases where planarity check fails

    def get_graph_properties(self) -> dict:
        """
        Calculates and returns a dictionary of various graph properties.
        """
        properties = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "degree_distribution": self.get_degree_distribution(),
            "average_degree": self.get_average_degree(),
            "density": self.get_density(),
            "global_clustering_coefficient": self.get_global_clustering_coefficient(),
            "average_shortest_path_length": self.get_average_shortest_path_length(),
            "diameter": self.get_diameter(),
            "num_connected_components": self.get_number_of_connected_components(),
            "is_planar": self.get_is_planar(),
        }
        return properties

if __name__ == '__main__':
    # Example usage:
    from qiskit import QuantumCircuit

    # Create a sample quantum circuit
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.t(0)
    qc.tdg(3)

    # Create a TopologicalPropertyExtractor instance
    extractor = TopologicalPropertyExtractor(qc)

    # Extract and print graph properties
    properties = extractor.get_graph_properties()
    for key, value in properties.items():
        print(f"{key}: {value}")