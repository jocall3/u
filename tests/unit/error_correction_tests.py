import unittest
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit.providers.aer import AerSimulator

class ErrorCorrectionTests(unittest.TestCase):

    def setUp(self):
        self.simulator = AerSimulator()

    def test_logical_qubit_insertion_simple(self):
        """
        Tests the insertion of a logical qubit encoded using a simple code (e.g., repetition code).
        Verifies that the encoded state is correctly created.
        """
        qr = QuantumRegister(3, 'q')
        cr = ClassicalRegister(3, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Encode |0> using a 3-qubit repetition code
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])

        # Measure
        circuit.measure(qr, cr)

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |000> and |111> states
        self.assertTrue(all(key in counts for key in ['000', '111']))
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000', 0) + counts.get('111', 0), 0.9 * total_counts)


    def test_error_correction_repetition_code_bit_flip(self):
        """
        Tests error correction using a 3-qubit repetition code against bit-flip errors.
        Simulates a bit-flip error and then corrects it.
        """
        qr = QuantumRegister(3, 'q')
        cr = ClassicalRegister(3, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Encode |0>
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])

        # Introduce a bit-flip error on qubit 1
        circuit.x(qr[1])

        # Syndrome measurement (error detection)
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.measure(qr[1], cr[0])
        circuit.measure(qr[2], cr[1])

        # Correct the error based on the syndrome
        with circuit.if_test((cr[0], 1)):
            circuit.x(qr[0])
        with circuit.if_test((cr[1], 1)):
            circuit.x(qr[0])

        # Measure
        circuit.measure(qr[0], cr[2])

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |000> state (corrected)
        self.assertTrue('000' in counts)
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000', 0), 0.9 * total_counts)


    def test_error_correction_repetition_code_phase_flip(self):
        """
        Tests error correction using a 3-qubit repetition code against phase-flip errors.
        Simulates a phase-flip error and then corrects it.  This test is more complex
        as it requires Hadamard gates and controlled-Z gates.
        """
        qr = QuantumRegister(3, 'q')
        cr = ClassicalRegister(3, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Encode |+> = H|0>
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])

        # Introduce a phase-flip error on qubit 1 (Z gate)
        circuit.z(qr[1])

        # Syndrome measurement (error detection)
        circuit.h(qr[0])
        circuit.h(qr[1])
        circuit.h(qr[2])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.h(qr[1])
        circuit.h(qr[2])
        circuit.measure(qr[1], cr[0])
        circuit.measure(qr[2], cr[1])

        # Correct the error based on the syndrome
        with circuit.if_test((cr[0], 1)):
            circuit.z(qr[0])
        with circuit.if_test((cr[1], 1)):
            circuit.z(qr[0])

        # Measure
        circuit.h(qr[0])
        circuit.measure(qr[0], cr[2])

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |+> state (corrected)
        self.assertTrue('000' in counts or '111' in counts) # Check for |+> or |- >
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000', 0) + counts.get('111', 0), 0.9 * total_counts)


    def test_error_correction_shor_code_bit_flip(self):
        """
        Tests error correction using the Shor code against bit-flip errors.
        This is a more complex test, involving multiple qubits and gates.
        """
        qr = QuantumRegister(9, 'q')
        cr = ClassicalRegister(6, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Shor code encoding
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.h(qr[3])
        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.h(qr[6])
        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])

        circuit.cx(qr[0], qr[3])
        circuit.cx(qr[0], qr[6])

        # Introduce a bit-flip error on qubit 4
        circuit.x(qr[4])

        # Syndrome measurement (error detection) - bit flip
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.measure(qr[1], cr[0])
        circuit.measure(qr[2], cr[1])

        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.measure(qr[4], cr[2])
        circuit.measure(qr[5], cr[3])

        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])
        circuit.measure(qr[7], cr[4])
        circuit.measure(qr[8], cr[5])

        # Correct the error based on the syndrome
        with circuit.if_test((cr[0], 1)):
            circuit.x(qr[0])
        with circuit.if_test((cr[1], 1)):
            circuit.x(qr[0])

        with circuit.if_test((cr[2], 1)):
            circuit.x(qr[3])
        with circuit.if_test((cr[3], 1)):
            circuit.x(qr[3])

        with circuit.if_test((cr[4], 1)):
            circuit.x(qr[6])
        with circuit.if_test((cr[5], 1)):
            circuit.x(qr[6])

        # Measure the logical qubit
        circuit.measure(qr[0], cr[0])
        circuit.measure(qr[3], cr[1])
        circuit.measure(qr[6], cr[2])

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |000> state (corrected)
        self.assertTrue('000000' in counts)
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000000', 0), 0.9 * total_counts)


    def test_error_correction_shor_code_phase_flip(self):
        """
        Tests error correction using the Shor code against phase-flip errors.
        This is a more complex test, involving multiple qubits and gates.
        """
        qr = QuantumRegister(9, 'q')
        cr = ClassicalRegister(6, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Shor code encoding
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.h(qr[3])
        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.h(qr[6])
        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])

        circuit.cx(qr[0], qr[3])
        circuit.cx(qr[0], qr[6])

        # Introduce a phase-flip error on qubit 4 (Z gate)
        circuit.z(qr[4])

        # Syndrome measurement (error detection) - phase flip
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.measure(qr[1], cr[0])
        circuit.measure(qr[2], cr[1])

        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.measure(qr[4], cr[2])
        circuit.measure(qr[5], cr[3])

        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])
        circuit.measure(qr[7], cr[4])
        circuit.measure(qr[8], cr[5])

        # Correct the error based on the syndrome
        with circuit.if_test((cr[0], 1)):
            circuit.x(qr[0])
        with circuit.if_test((cr[1], 1)):
            circuit.x(qr[0])

        with circuit.if_test((cr[2], 1)):
            circuit.x(qr[3])
        with circuit.if_test((cr[3], 1)):
            circuit.x(qr[3])

        with circuit.if_test((cr[4], 1)):
            circuit.x(qr[6])
        with circuit.if_test((cr[5], 1)):
            circuit.x(qr[6])

        # Measure the logical qubit
        circuit.measure(qr[0], cr[0])
        circuit.measure(qr[3], cr[1])
        circuit.measure(qr[6], cr[2])

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |000> state (corrected)
        self.assertTrue('000000' in counts)
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000000', 0), 0.9 * total_counts)


    def test_error_correction_shor_code_combined_errors(self):
        """
        Tests error correction using the Shor code against combined bit-flip and phase-flip errors.
        This is a more complex test, involving multiple qubits and gates.
        """
        qr = QuantumRegister(9, 'q')
        cr = ClassicalRegister(6, 'c')
        circuit = QuantumCircuit(qr, cr)

        # Shor code encoding
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.h(qr[3])
        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.h(qr[6])
        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])

        circuit.cx(qr[0], qr[3])
        circuit.cx(qr[0], qr[6])

        # Introduce a bit-flip error on qubit 4
        circuit.x(qr[4])

        # Introduce a phase-flip error on qubit 7 (Z gate)
        circuit.z(qr[7])

        # Syndrome measurement (error detection) - bit flip
        circuit.cx(qr[0], qr[1])
        circuit.cx(qr[0], qr[2])
        circuit.measure(qr[1], cr[0])
        circuit.measure(qr[2], cr[1])

        circuit.cx(qr[3], qr[4])
        circuit.cx(qr[3], qr[5])
        circuit.measure(qr[4], cr[2])
        circuit.measure(qr[5], cr[3])

        circuit.cx(qr[6], qr[7])
        circuit.cx(qr[6], qr[8])
        circuit.measure(qr[7], cr[4])
        circuit.measure(qr[8], cr[5])

        # Correct the error based on the syndrome
        with circuit.if_test((cr[0], 1)):
            circuit.x(qr[0])
        with circuit.if_test((cr[1], 1)):
            circuit.x(qr[0])

        with circuit.if_test((cr[2], 1)):
            circuit.x(qr[3])
        with circuit.if_test((cr[3], 1)):
            circuit.x(qr[3])

        with circuit.if_test((cr[4], 1)):
            circuit.x(qr[6])
        with circuit.if_test((cr[5], 1)):
            circuit.x(qr[6])

        # Measure the logical qubit
        circuit.measure(qr[0], cr[0])
        circuit.measure(qr[3], cr[1])
        circuit.measure(qr[6], cr[2])

        # Simulate
        job = self.simulator.run(circuit, shots=1024)
        result = job.result()
        counts = result.get_counts(circuit)

        # Assert that the counts are predominantly in the |000> state (corrected)
        self.assertTrue('000000' in counts)
        total_counts = sum(counts.values())
        self.assertGreaterEqual(counts.get('000000', 0), 0.9 * total_counts)