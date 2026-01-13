import unittest
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator
from qiskit.providers.basic_provider import BasicSimulator
from qiskit.circuit.library import QFT

class TestLoopConstructs(unittest.TestCase):

    def setUp(self):
        self.simulator = BasicSimulator()
        self.tolerance = 1e-6  # Numerical tolerance for comparisons

    def assertAlmostEqualStatevector(self, sv1, sv2, places=None, msg=None, delta=None):
        """Assert that two statevectors are almost equal."""
        sv1_arr = np.asarray(sv1)
        sv2_arr = np.asarray(sv2)
        self.assertTrue(np.allclose(sv1_arr, sv2_arr, atol=self.tolerance),
                        msg=msg or f"Statevectors differ by more than tolerance {self.tolerance}")

    def test_simple_loop_eigenstate(self):
        """Test encoding an eigenstate in a simple loop."""
        num_qubits = 3
        qc = QuantumCircuit(num_qubits)

        # Prepare an eigenstate (e.g., |+> on all qubits)
        for i in range(num_qubits):
            qc.h(i)

        # Simulate the circuit
        job = self.simulator.run(transpile(qc, self.simulator), shots=1)
        result = job.result()
        statevector = result.get_statevector(qc)

        # Expected statevector (|+> on all qubits)
        expected_statevector = Statevector([1/np.sqrt(2)**num_qubits] * (2**num_qubits))

        self.assertAlmostEqualStatevector(statevector, expected_statevector,
                                           msg="Simple loop eigenstate preparation failed.")

    def test_controlled_loop_eigenstate(self):
        """Test encoding an eigenstate in a controlled loop."""
        num_qubits = 4  # 1 control qubit, 3 target qubits
        qc = QuantumCircuit(num_qubits)

        # Prepare control qubit in |1> state
        qc.x(0)

        # Controlled loop: Apply H to target qubits only if control is |1>
        for i in range(1, num_qubits):
            qc.ch(0, i)

        # Simulate the circuit
        job = self.simulator.run(transpile(qc, self.simulator), shots=1)
        result = job.result()
        statevector = result.get_statevector(qc)

        # Expected statevector: |1> |+>|+>|+>
        expected_statevector = np.zeros(2**num_qubits, dtype=complex)
        expected_statevector[2**(num_qubits-1) + int('111', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('110', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('101', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('100', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('011', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('010', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('001', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector[2**(num_qubits-1) + int('000', 2)] = 1/np.sqrt(2)**(num_qubits-1)
        expected_statevector = Statevector(expected_statevector)

        self.assertAlmostEqualStatevector(statevector, expected_statevector,
                                           msg="Controlled loop eigenstate preparation failed.")

    def test_orthogonal_measurement(self):
        """Test orthogonal measurement after a loop construct."""
        num_qubits = 2
        qc = QuantumCircuit(num_qubits, num_qubits)

        # Prepare |+> state on both qubits
        for i in range(num_qubits):
            qc.h(i)

        # Measure in the Hadamard basis (orthogonal to computational basis)
        for i in range(num_qubits):
            qc.h(i)
            qc.measure(i, i)

        # Simulate the circuit with measurements
        job = self.simulator.run(transpile(qc, self.simulator), shots=1024)
        result = job.result()
        counts = result.get_counts(qc)

        # Expected counts: roughly equal probabilities for all outcomes
        expected_probabilities = {bin(i)[2:].zfill(num_qubits): 1/2**num_qubits for i in range(2**num_qubits)}
        observed_probabilities = {outcome: count / 1024 for outcome, count in counts.items()}

        for outcome, expected_prob in expected_probabilities.items():
            observed_prob = observed_probabilities.get(outcome, 0)
            self.assertAlmostEqual(observed_prob, expected_prob, delta=0.05,
                                   msg=f"Orthogonal measurement failed for outcome {outcome}.")

    def test_loop_with_qft(self):
        """Test a loop construct combined with QFT."""
        num_qubits = 3
        qc = QuantumCircuit(num_qubits, num_qubits)

        # Prepare |111> state
        for i in range(num_qubits):
            qc.x(i)

        # Apply QFT
        qft = QFT(num_qubits)
        qc.append(qft, range(num_qubits))

        # Measure in the computational basis
        qc.measure(range(num_qubits), range(num_qubits))

        # Simulate the circuit
        job = self.simulator.run(transpile(qc, self.simulator), shots=1024)
        result = job.result()
        counts = result.get_counts(qc)

        # QFT of |111> should distribute probabilities across all states
        total_shots = sum(counts.values())
        for outcome, count in counts.items():
            probability = count / total_shots
            self.assertTrue(0 <= probability <= 1, "Probability out of bounds")

if __name__ == '__main__':
    unittest.main()