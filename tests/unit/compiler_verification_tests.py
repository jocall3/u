import unittest
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator
from qiskit.providers.basic_provider import BasicSimulator
from qiskit.circuit.library import HGate, SGate, TGate, CXGate
from qiskit.compiler import transpile

class TestCompilerVerification(unittest.TestCase):

    def setUp(self):
        self.simulator = BasicSimulator()
        self.seed = 42  # For reproducibility

    def assert_state_almost_equal(self, state1, state2, places=7):
        """Assert that two quantum states are almost equal."""
        np.testing.assert_almost_equal(np.abs(np.dot(state1.conjugate(), state2)), 1.0, decimal=places)

    def test_h_gate_verification(self):
        """Verify H gate transforms |0> to |+>."""
        qc = QuantumCircuit(1)
        qc.h(0)
        target_state = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

    def test_s_gate_verification(self):
        """Verify S gate transforms |+> to |+i>."""
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.s(0)
        target_state = Statevector([1/np.sqrt(2), 1j/np.sqrt(2)])
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

    def test_t_gate_verification(self):
        """Verify T gate transforms |0> to T|0>."""
        qc = QuantumCircuit(1)
        qc.t(0)
        target_state = Statevector([1, 0]) # T|0> = |0>
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

        qc = QuantumCircuit(1)
        qc.h(0)
        qc.t(0)
        target_state = Statevector([1/np.sqrt(2), (1+1j)/np.sqrt(2)/np.sqrt(2)])
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

    def test_cx_gate_verification(self):
        """Verify CX gate creates Bell state |00> + |11>."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        target_state = Statevector([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

    def test_magic_state_preparation(self):
        """Verify magic state |T> = T|0> preparation."""
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.t(0)
        qc.h(0)
        target_state = Statevector([0.85355339+0.j, 0.51763809-0.j])
        result = self.simulator.run(transpile(qc, self.simulator), shots=1000).result()
        final_state = Statevector.from_instruction(qc)
        self.assert_state_almost_equal(final_state, target_state)

    def test_transpilation_preserves_state(self):
        """Verify transpilation preserves the final state."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.t(0)
        qc.h(1)

        # Transpile the circuit
        transpiled_qc = transpile(qc, self.simulator)

        # Get the statevector of the original and transpiled circuits
        original_state = Statevector.from_instruction(qc)
        transpiled_state = Statevector.from_instruction(transpiled_qc)

        # Assert that the states are almost equal
        self.assert_state_almost_equal(original_state, transpiled_state)

    def test_complex_circuit_verification(self):
        """Verify a more complex circuit with multiple gates."""
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.t(1)
        qc.cx(1, 2)
        qc.h(2)

        # Define the expected unitary transformation (manually calculated)
        # This is a placeholder.  A real test would calculate this based on the circuit.
        # For example, using Operator(qc).data
        expected_unitary = np.array([
            [0.70710678+0.j, 0.70710678+0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.70710678+0.j, 0.70710678+0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.70710678+0.j, 0.70710678+0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.70710678+0.j, 0.70710678+0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j],
            [0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j, 0.        +0.j]
        ])

        # Get the unitary of the circuit
        circuit_unitary = Operator(qc).data

        # Assert that the unitaries are almost equal
        np.testing.assert_almost_equal(np.abs(np.trace(np.dot(expected_unitary.conjugate().T, circuit_unitary))), 8.0, decimal=7)

if __name__ == '__main__':
    unittest.main()