import time
import random
import statistics
from qiskit import QuantumCircuit, transpile, assemble, Aer, execute
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram

class RuntimeQuantumProfiler:
    """
    A class for profiling the runtime performance of quantum circuits using quantum gates.
    Applies quantum gates and measures execution time to provide performance insights.
    """

    def __init__(self, num_qubits=4, backend='qasm_simulator', shots=1024):
        """
        Initializes the RuntimeQuantumProfiler.

        Args:
            num_qubits (int): The number of qubits in the quantum circuit.
            backend (str): The backend to use for quantum circuit execution (e.g., 'qasm_simulator', 'ibmq_qasm_simulator').
            shots (int): The number of shots to run the quantum circuit.
        """
        self.num_qubits = num_qubits
        self.backend_name = backend
        self.shots = shots
        self.backend = Aer.get_backend(self.backend_name)  # Default to Aer simulator
        self.results = []  # Store profiling results

    def _create_random_circuit(self, depth=5):
        """
        Creates a random quantum circuit with a specified depth.

        Args:
            depth (int): The depth of the quantum circuit (number of gate layers).

        Returns:
            QuantumCircuit: A randomly generated quantum circuit.
        """
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        for _ in range(depth):
            for qubit in range(self.num_qubits):
                gate_type = random.choice(['h', 'x', 'y', 'z', 'rx', 'ry', 'rz'])
                if gate_type == 'h':
                    qc.h(qubit)
                elif gate_type == 'x':
                    qc.x(qubit)
                elif gate_type == 'y':
                    qc.y(qubit)
                elif gate_type == 'z':
                    qc.z(qubit)
                elif gate_type == 'rx':
                    angle = random.uniform(0, 3.14159)
                    qc.rx(angle, qubit)
                elif gate_type == 'ry':
                    angle = random.uniform(0, 3.14159)
                    qc.ry(angle, qubit)
                elif gate_type == 'rz':
                    angle = random.uniform(0, 3.14159)
                    qc.rz(angle, qubit)

            # Add some entanglement
            if self.num_qubits > 1:
                control_qubit = random.randint(0, self.num_qubits - 2)
                target_qubit = control_qubit + 1
                qc.cx(control_qubit, target_qubit)

        qc.measure(range(self.num_qubits), range(self.num_qubits))
        return qc

    def profile_circuit(self, circuit=None, num_trials=5):
        """
        Profiles the runtime performance of a given quantum circuit.

        Args:
            circuit (QuantumCircuit): The quantum circuit to profile. If None, a random circuit is generated.
            num_trials (int): The number of times to run the circuit for averaging.

        Returns:
            dict: A dictionary containing profiling results (mean, median, std dev).
        """
        if circuit is None:
            circuit = self._create_random_circuit()

        execution_times = []
        for _ in range(num_trials):
            start_time = time.time()
            job = execute(circuit, self.backend, shots=self.shots)
            job.result()  # Wait for the job to complete
            end_time = time.time()
            execution_times.append(end_time - start_time)

        mean_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        std_dev_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0

        self.results.append({
            'circuit_depth': circuit.depth(),
            'num_gates': circuit.size(),
            'mean_execution_time': mean_time,
            'median_execution_time': median_time,
            'std_dev_execution_time': std_dev_time
        })

        return {
            'mean_execution_time': mean_time,
            'median_execution_time': median_time,
            'std_dev_execution_time': std_dev_time
        }

    def get_results(self):
        """
        Returns the accumulated profiling results.

        Returns:
            list: A list of dictionaries, where each dictionary contains profiling results for a circuit.
        """
        return self.results

    def reset_results(self):
        """
        Resets the accumulated profiling results.
        """
        self.results = []

    def analyze_results(self):
        """
        Analyzes the accumulated results and provides insights.

        Returns:
            str: A string containing a summary of the profiling results.
        """
        if not self.results:
            return "No profiling results available."

        summary = "Quantum Circuit Profiling Summary:\n"
        for i, result in enumerate(self.results):
            summary += f"Circuit {i+1}:\n"
            summary += f"  Depth: {result['circuit_depth']}\n"
            summary += f"  Number of Gates: {result['num_gates']}\n"
            summary += f"  Mean Execution Time: {result['mean_execution_time']:.4f} seconds\n"
            summary += f"  Median Execution Time: {result['median_execution_time']:.4f} seconds\n"
            summary += f"  Standard Deviation: {result['std_dev_execution_time']:.4f} seconds\n"
            summary += "\n"

        return summary

if __name__ == '__main__':
    # Example Usage
    profiler = RuntimeQuantumProfiler(num_qubits=3, backend='qasm_simulator', shots=2048)

    # Profile a few random circuits
    for i in range(3):
        print(f"Profiling random circuit {i+1}...")
        results = profiler.profile_circuit()
        print(f"Results: {results}")

    # Profile a custom circuit
    custom_circuit = QuantumCircuit(3, 3)
    custom_circuit.h(0)
    custom_circuit.cx(0, 1)
    custom_circuit.cx(1, 2)
    custom_circuit.measure([0, 1, 2], [0, 1, 2])

    print("Profiling custom circuit...")
    results = profiler.profile_circuit(circuit=custom_circuit)
    print(f"Results: {results}")

    # Analyze and print the overall results
    analysis = profiler.analyze_results()
    print(analysis)