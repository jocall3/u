import unittest
import numpy as np
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.quantum_info import Statevector
from qiskit.providers.aer.noise import NoiseModel, depolarizing_error, pauli_error
from qiskit.result import Result

class QuantumStabilityTests(unittest.TestCase):

    def setUp(self):
        """Setup for the tests."""
        self.simulator = Aer.get_backend('qasm_simulator')
        self.statevector_simulator = Aer.get_backend('statevector_simulator')
        self.n_qubits = 3
        self.qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        self.qc.h(0)
        self.qc.cx(0, 1)
        self.qc.cx(1, 2)
        self.qc.measure(range(self.n_qubits), range(self.n_qubits))
        self.transpiled_qc = transpile(self.qc, self.simulator)

    def test_ideal_execution(self):
        """Test ideal execution without noise."""
        job = execute(self.transpiled_qc, self.simulator, shots=1024)
        result = job.result()
        counts = result.get_counts(self.qc)
        self.assertIsInstance(counts, dict)
        self.assertGreater(sum(counts.values()), 0)

    def test_depolarizing_noise(self):
        """Test execution with depolarizing noise."""
        noise_model = NoiseModel()
        error = depolarizing_error(0.05, 1)  # 5% depolarizing error on each qubit
        noise_model.add_all_qubit_quantum_error(error, ['u1', 'u2', 'u3', 'cx'])

        job = execute(self.transpiled_qc, self.simulator,
                      noise_model=noise_model, shots=1024)
        result = job.result()
        counts = result.get_counts(self.qc)
        self.assertIsInstance(counts, dict)
        self.assertGreater(sum(counts.values()), 0)

    def test_pauli_noise(self):
        """Test execution with Pauli noise."""
        noise_model = NoiseModel()
        error = pauli_error([('I', 0.9), ('X', 0.1)])  # 10% chance of X error
        noise_model.add_all_qubit_quantum_error(error, ['u1', 'u2', 'u3', 'cx'])

        job = execute(self.transpiled_qc, self.simulator,
                      noise_model=noise_model, shots=1024)
        result = job.result()
        counts = result.get_counts(self.qc)
        self.assertIsInstance(counts, dict)
        self.assertGreater(sum(counts.values()), 0)

    def test_intentional_decoherence(self):
        """Test intentional decoherence by adding a reset gate."""
        qc_decoherence = QuantumCircuit(self.n_qubits, self.n_qubits)
        qc_decoherence.h(0)
        qc_decoherence.cx(0, 1)
        qc_decoherence.cx(1, 2)
        qc_decoherence.reset(1)  # Introduce decoherence on qubit 1
        qc_decoherence.measure(range(self.n_qubits), range(self.n_qubits))
        transpiled_qc_decoherence = transpile(qc_decoherence, self.simulator)

        job = execute(transpiled_qc_decoherence, self.simulator, shots=1024)
        result = job.result()
        counts = result.get_counts(qc_decoherence)
        self.assertIsInstance(counts, dict)
        self.assertGreater(sum(counts.values()), 0)

        # Verify that the counts are different from the ideal case
        job_ideal = execute(self.transpiled_qc, self.simulator, shots=1024)
        result_ideal = job_ideal.result()
        counts_ideal = result_ideal.get_counts(self.qc)

        self.assertNotEqual(counts, counts_ideal)

    def test_statevector_simulation_correctness(self):
        """Test statevector simulation for correctness."""
        qc_statevector = QuantumCircuit(self.n_qubits)
        qc_statevector.h(0)
        qc_statevector.cx(0, 1)
        qc_statevector.cx(1, 2)

        job = execute(qc_statevector, self.statevector_simulator)
        result = job.result()
        statevector = result.get_statevector(qc_statevector)
        self.assertIsInstance(statevector, np.ndarray)
        self.assertEqual(len(statevector), 2**self.n_qubits)

        # Check if the statevector is normalized
        norm = np.linalg.norm(statevector)
        self.assertAlmostEqual(norm, 1.0, places=7)

    def test_result_object_integrity(self):
        """Test the integrity of the Result object."""
        job = execute(self.transpiled_qc, self.simulator, shots=100)
        result = job.result()

        self.assertIsInstance(result, Result)
        self.assertEqual(result.status, 'COMPLETED')
        self.assertIsNotNone(result.results)
        self.assertEqual(len(result.results), 1)  # Assuming one circuit

        # Check metadata
        metadata = result.results[0].metadata
        self.assertIsInstance(metadata, dict)

    def test_empty_circuit_execution(self):
        """Test execution of an empty circuit."""
        empty_qc = QuantumCircuit(2, 2)
        empty_qc.measure([0, 1], [0, 1])
        transpiled_empty_qc = transpile(empty_qc, self.simulator)
        job = execute(transpiled_empty_qc, self.simulator, shots=100)
        result = job.result()
        counts = result.get_counts(empty_qc)
        self.assertIsInstance(counts, dict)
        self.assertIn('00', counts)

if __name__ == '__main__':
    unittest.main()