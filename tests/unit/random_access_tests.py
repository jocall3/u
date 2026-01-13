import unittest
import numpy as np
from quantum_algorithms import QuantumRegister, QuantumCircuit, H, CNOT, Measure

class RandomAccessTests(unittest.TestCase):

    def test_superposition_addressing_single_qubit(self):
        """Tests accessing a single qubit in superposition."""
        qr = QuantumRegister(1)
        qc = QuantumCircuit(qr)
        qc.apply(H, qr[0])  # Create superposition
        qc.measure(qr[0])
        result = qc.run(shots=1024)
        self.assertTrue(abs(result.get_counts()[0] / 1024 - 0.5) < 0.1)
        self.assertTrue(abs(result.get_counts()[1] / 1024 - 0.5) < 0.1)

    def test_superposition_addressing_two_qubits(self):
        """Tests accessing two qubits in superposition, verifying entanglement."""
        qr = QuantumRegister(2)
        qc = QuantumCircuit(qr)
        qc.apply(H, qr[0])
        qc.apply(CNOT, [qr[0], qr[1]])
        qc.measure(qr[0])
        qc.measure(qr[1])
        result = qc.run(shots=1024)
        counts = result.get_counts()
        self.assertTrue(abs(counts.get('00', 0) / 1024 - 0.5) < 0.1)
        self.assertTrue(abs(counts.get('11', 0) / 1024 - 0.5) < 0.1)
        self.assertTrue(counts.get('01', 0) == 0)
        self.assertTrue(counts.get('10', 0) == 0)

    def test_random_access_with_controlled_operations(self):
        """Tests random access using controlled operations based on superposition."""
        qr = QuantumRegister(3)
        qc = QuantumCircuit(qr)
        qc.apply(H, qr[0])
        qc.apply(CNOT, [qr[0], qr[1]])
        qc.apply(CNOT, [qr[0], qr[2]])
        qc.measure(qr[1])
        qc.measure(qr[2])
        result = qc.run(shots=1024)
        counts = result.get_counts()
        self.assertTrue(abs(counts.get('000', 0) / 1024 - 0.25) < 0.15)
        self.assertTrue(abs(counts.get('011', 0) / 1024 - 0.25) < 0.15)
        self.assertTrue(abs(counts.get('101', 0) / 1024 - 0.25) < 0.15)
        self.assertTrue(abs(counts.get('110', 0) / 1024 - 0.25) < 0.15)

    def test_random_access_with_multiple_superpositions(self):
        """Tests random access with multiple qubits in superposition."""
        qr = QuantumRegister(3)
        qc = QuantumCircuit(qr)
        qc.apply(H, qr[0])
        qc.apply(H, qr[1])
        qc.apply(CNOT, [qr[0], qr[2]])
        qc.apply(CNOT, [qr[1], qr[2]])
        qc.measure(qr[2])
        result = qc.run(shots=1024)
        counts = result.get_counts()
        self.assertTrue(abs(counts.get('000', 0) / 1024 - 0.25) < 0.15)
        self.assertTrue(abs(counts.get('011', 0) / 1024 - 0.15) < 0.15)
        self.assertTrue(abs(counts.get('101', 0) / 1024 - 0.15) < 0.15)
        self.assertTrue(abs(counts.get('110', 0) / 1024 - 0.15) < 0.15)

    def test_random_access_with_complex_entanglement(self):
        """Tests random access with complex entanglement patterns."""
        qr = QuantumRegister(4)
        qc = QuantumCircuit(qr)
        qc.apply(H, qr[0])
        qc.apply(H, qr[1])
        qc.apply(CNOT, [qr[0], qr[2]])
        qc.apply(CNOT, [qr[1], qr[3]])
        qc.apply(CNOT, [qr[2], qr[3]])
        qc.measure(qr[2])
        qc.measure(qr[3])
        result = qc.run(shots=1024)
        counts = result.get_counts()
        self.assertTrue(abs(counts.get('0000', 0) / 1024 - 0.25) < 0.15)
        self.assertTrue(abs(counts.get('0011', 0) / 1024 - 0.15) < 0.15)
        self.assertTrue(abs(counts.get('1100', 0) / 1024 - 0.15) < 0.15)
        self.assertTrue(abs(counts.get('1111', 0) / 1024 - 0.15) < 0.15)

if __name__ == '__main__':
    unittest.main()