import unittest
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.providers.basic_provider import BasicSimulator

class TestNestedQuantumFunctions(unittest.TestCase):

    def setUp(self):
        self.simulator = BasicSimulator()

    def assert_unitary_equal(self, unitary1, unitary2, msg=None, atol=1e-8):
        """Assert that two unitary matrices are equal to within a tolerance."""
        self.assertTrue(np.allclose(unitary1, unitary2, atol=atol), msg=msg)

    def create_simple_circuit(self, func):
        """Creates a simple quantum circuit with a given function applied."""
        qc = QuantumCircuit(1)
        func(qc, 0)  # Apply the function to qubit 0
        return qc

    def get_unitary(self, circuit):
        """Returns the unitary matrix representation of a quantum circuit."""
        compiled_circuit = transpile(circuit, self.simulator)
        job = self.simulator.run(compiled_circuit)
        result = job.result()
        unitary = Operator(result.get_unitary(compiled_circuit)).data
        return unitary

    def test_single_qubit_gates(self):
        """Tests basic single-qubit gates as unitary operators."""

        def hadamard(qc, qubit):
            qc.h(qubit)

        def pauli_x(qc, qubit):
            qc.x(qubit)

        def pauli_y(qc, qubit):
            qc.y(qubit)

        def pauli_z(qc, qubit):
            qc.z(qubit)

        h_circuit = self.create_simple_circuit(hadamard)
        x_circuit = self.create_simple_circuit(pauli_x)
        y_circuit = self.create_simple_circuit(pauli_y)
        z_circuit = self.create_simple_circuit(pauli_z)

        h_unitary = self.get_unitary(h_circuit)
        x_unitary = self.get_unitary(x_circuit)
        y_unitary = self.get_unitary(y_circuit)
        z_unitary = self.get_unitary(z_circuit)

        expected_h = np.array([[1/np.sqrt(2), 1/np.sqrt(2)], [1/np.sqrt(2), -1/np.sqrt(2)]])
        expected_x = np.array([[0, 1], [1, 0]])
        expected_y = np.array([[0, -1j], [1j, 0]])
        expected_z = np.array([[1, 0], [0, -1]])

        self.assert_unitary_equal(h_unitary, expected_h, msg="Hadamard gate test failed")
        self.assert_unitary_equal(x_unitary, expected_x, msg="Pauli-X gate test failed")
        self.assert_unitary_equal(y_unitary, expected_y, msg="Pauli-Y gate test failed")
        self.assert_unitary_equal(z_unitary, expected_z, msg="Pauli-Z gate test failed")

    def test_nested_function_composition(self):
        """Tests composition of nested quantum functions as matrix multiplication."""

        def inner_function(qc, qubit):
            qc.h(qubit)
            qc.x(qubit)

        def outer_function(qc, qubit):
            qc.z(qubit)
            inner_function(qc, qubit)
            qc.y(qubit)

        composed_circuit = self.create_simple_circuit(outer_function)
        composed_unitary = self.get_unitary(composed_circuit)

        # Calculate the expected unitary by multiplying the individual unitaries
        h_unitary = np.array([[1/np.sqrt(2), 1/np.sqrt(2)], [1/np.sqrt(2), -1/np.sqrt(2)]])
        x_unitary = np.array([[0, 1], [1, 0]])
        y_unitary = np.array([[0, -1j], [1j, 0]])
        z_unitary = np.array([[1, 0], [0, -1]])

        expected_unitary = y_unitary @ x_unitary @ h_unitary @ z_unitary

        self.assert_unitary_equal(composed_unitary, expected_unitary, msg="Nested function composition test failed")

    def test_conditional_gates_in_nested_functions(self):
        """Tests nested functions with conditional gates."""

        def controlled_x(qc, control_qubit, target_qubit):
            qc.cx(control_qubit, target_qubit)

        def outer_function(qc, control_qubit, target_qubit):
            qc.h(control_qubit)
            controlled_x(qc, control_qubit, target_qubit)
            qc.h(control_qubit)

        qc = QuantumCircuit(2)
        outer_function(qc, 0, 1)
        composed_unitary = self.get_unitary(qc)

        expected_unitary = np.array([
            [0.5 + 0.5j,  0.5 - 0.5j,  0.5 - 0.5j,  0.5 + 0.5j],
            [0.5 - 0.5j,  0.5 + 0.5j,  0.5 + 0.5j,  0.5 - 0.5j],
            [0.5 - 0.5j,  0.5 + 0.5j,  0.5 + 0.5j,  0.5 - 0.5j],
            [0.5 + 0.5j,  0.5 - 0.5j,  0.5 - 0.5j,  0.5 + 0.5j]
        ])

        self.assert_unitary_equal(composed_unitary, expected_unitary, msg="Conditional gates in nested functions test failed")

    def test_multi_qubit_nested_functions(self):
        """Tests nested functions operating on multiple qubits."""

        def inner_function(qc, qubit1, qubit2):
            qc.cx(qubit1, qubit2)

        def outer_function(qc, qubit1, qubit2):
            qc.h(qubit1)
            inner_function(qc, qubit1, qubit2)
            qc.h(qubit1)

        qc = QuantumCircuit(2)
        outer_function(qc, 0, 1)
        composed_unitary = self.get_unitary(qc)

        expected_unitary = np.array([
            [0.5 + 0.5j,  0.5 - 0.5j,  0.5 - 0.5j,  0.5 + 0.5j],
            [0.5 - 0.5j,  0.5 + 0.5j,  0.5 + 0.5j,  0.5 - 0.5j],
            [0.5 - 0.5j,  0.5 + 0.5j,  0.5 + 0.5j,  0.5 - 0.5j],
            [0.5 + 0.5j,  0.5 - 0.5j,  0.5 - 0.5j,  0.5 + 0.5j]
        ])

        self.assert_unitary_equal(composed_unitary, expected_unitary, msg="Multi-qubit nested functions test failed")

if __name__ == '__main__':
    unittest.main()