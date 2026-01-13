import numpy as np
import qiskit
from qiskit import QuantumCircuit, transpile, assemble, Aer, execute
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector

class QuantumGraphProcessor:
    """
    A class to represent and process graphs using quantum computing techniques,
    specifically focusing on Grover's search algorithm.
    """

    def __init__(self, adjacency_matrix):
        """
        Initializes the QuantumGraphProcessor with an adjacency matrix representing the graph.

        Args:
            adjacency_matrix (numpy.ndarray): A square matrix representing the graph's adjacency.
                                              Entry (i, j) is 1 if there's an edge between nodes i and j, 0 otherwise.
        """
        self.adjacency_matrix = np.array(adjacency_matrix)
        self.num_nodes = self.adjacency_matrix.shape[0]
        self.num_qubits = int(np.ceil(np.log2(self.num_nodes)))  # Number of qubits needed to represent nodes

        if self.adjacency_matrix.shape[0] != self.adjacency_matrix.shape[1]:
            raise ValueError("Adjacency matrix must be square.")

        if self.num_nodes != 2**self.num_qubits:
            print(f"Warning: Number of nodes ({self.num_nodes}) is not a power of 2.  Padding with isolated nodes may be necessary.")

    def _encode_node(self, node_index):
        """
        Encodes a node index into a binary string representation.

        Args:
            node_index (int): The index of the node to encode.

        Returns:
            str: A binary string representing the node index.
        """
        return bin(node_index)[2:].zfill(self.num_qubits)

    def _decode_node(self, binary_string):
        """
        Decodes a binary string representation back into a node index.

        Args:
            binary_string (str): The binary string to decode.

        Returns:
            int: The node index represented by the binary string.
        """
        return int(binary_string, 2)

    def create_grover_circuit(self, marked_nodes):
        """
        Creates a quantum circuit for Grover's search algorithm to find marked nodes in the graph.

        Args:
            marked_nodes (list): A list of node indices that are considered "marked" or solutions.

        Returns:
            qiskit.QuantumCircuit: A quantum circuit implementing Grover's algorithm.
        """

        qc = QuantumCircuit(self.num_qubits, self.num_qubits)

        # Initialize all qubits to superposition
        qc.h(range(self.num_qubits))

        # Oracle
        def oracle():
            oracle_circuit = QuantumCircuit(self.num_qubits)
            for node in marked_nodes:
                binary_representation = self._encode_node(node)
                for i, bit in enumerate(binary_representation):
                    if bit == '0':
                        oracle_circuit.x(i)
                oracle_circuit.mcp(np.pi, list(range(self.num_qubits - 1)), self.num_qubits - 1) # Multi-controlled phase flip
                for i, bit in enumerate(binary_representation):
                    if bit == '0':
                        oracle_circuit.x(i)
            return oracle_circuit.to_gate(label="Oracle")

        # Diffuser
        def diffuser():
            diffuser_circuit = QuantumCircuit(self.num_qubits)
            diffuser_circuit.h(range(self.num_qubits))
            diffuser_circuit.x(range(self.num_qubits))
            diffuser_circuit.h(self.num_qubits - 1)
            diffuser_circuit.mcp(np.pi, list(range(self.num_qubits - 1)), self.num_qubits - 1)
            diffuser_circuit.h(self.num_qubits - 1)
            diffuser_circuit.x(range(self.num_qubits))
            diffuser_circuit.h(range(self.num_qubits))
            return diffuser_circuit.to_gate(label="Diffuser")

        oracle_gate = oracle()
        diffuser_gate = diffuser()

        # Number of Grover iterations (approximation)
        iterations = int(np.floor(np.sqrt(self.num_nodes) * np.pi / (4 * np.arcsin(np.sqrt(len(marked_nodes) / self.num_nodes)))))

        for _ in range(iterations):
            qc.append(oracle_gate, range(self.num_qubits))
            qc.append(diffuser_gate, range(self.num_qubits))

        # Measure the qubits
        qc.measure(range(self.num_qubits), range(self.num_qubits))

        return qc

    def run_grover_search(self, marked_nodes, shots=1024):
        """
        Runs Grover's search algorithm on the graph to find marked nodes.

        Args:
            marked_nodes (list): A list of node indices that are considered "marked" or solutions.
            shots (int): The number of times to run the quantum circuit.

        Returns:
            dict: A dictionary containing the measurement results, with node indices as keys and counts as values.
        """
        qc = self.create_grover_circuit(marked_nodes)

        # Simulate the circuit
        simulator = Aer.get_backend('qasm_simulator')
        compiled_circuit = transpile(qc, simulator)
        job = simulator.run(compiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)

        # Convert binary strings to node indices
        node_counts = {self._decode_node(binary_string): count for binary_string, count in counts.items()}

        return node_counts

    def visualize_results(self, results):
        """
        Visualizes the results of Grover's search using a histogram.

        Args:
            results (dict): A dictionary containing the measurement results, with node indices as keys and counts as values.
        """
        plot_histogram(results, title="Grover's Search Results").show()

if __name__ == '__main__':
    # Example usage:
    adjacency_matrix = [
        [0, 1, 0, 0],
        [1, 0, 1, 1],
        [0, 1, 0, 0],
        [0, 1, 0, 0]
    ]

    graph_processor = QuantumGraphProcessor(adjacency_matrix)

    marked_nodes = [1]  # Node 1 is the marked node

    results = graph_processor.run_grover_search(marked_nodes)
    print("Grover's Search Results:", results)

    #graph_processor.visualize_results(results) # Requires matplotlib