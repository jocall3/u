import unittest
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.providers.basic_provider import BasicSimulator
from qiskit.circuit.library import EfficientSU2
from qiskit.algorithms import TimeEvolutionProblem, TrotterQRTE
from qiskit.algorithms.evolvers import Trotter, TrotterSuzuki, LieTrotter
from qiskit.opflow import (
    I,
    X,
    Y,
    Z,
    H,
    CX,
    CY,
    CZ,
    Swap,
    Zero,
    One,
    Plus,
    Minus,
    StateFn,
    CircuitOp,
    MatrixOp,
    PauliOp,
    SummedOp,
    TensoredOp,
    op_converter,
)
from qiskit.opflow.primitive_ops import MatrixOp
from qiskit.quantum_info import Statevector

class TestHalTrotterization(unittest.TestCase):

    def setUp(self):
        self.simulator = BasicSimulator()
        self.num_qubits = 2
        self.dt = 0.1  # Time step for Trotterization

    def test_trotter_evolution_simple_hamiltonian(self):
        """Tests Trotter evolution with a simple Hamiltonian (e.g., XX + YY)."""
        # Define a simple Hamiltonian: XX + YY
        hamiltonian = (X ^ X) + (Y ^ Y)
        
        # Initial state
        initial_state = Statevector.from_label('00')

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Trotter evolution
        trotter = Trotter(n=1)  # First-order Trotter
        trotter_op = trotter.convert(hamiltonian, self.dt)

        # Convert to a matrix operator for comparison
        trotter_matrix = trotter_op.to_matrix()

        # Evolve the initial state using Trotter
        trotter_state = trotter_matrix @ initial_state

        # Compare the results
        np.testing.assert_allclose(trotter_state, exact_state, atol=1e-2)

    def test_trotter_suzuki_evolution(self):
        """Tests Trotter-Suzuki evolution."""
        # Define a Hamiltonian (e.g., X + Z on each qubit)
        hamiltonian = (X ^ I) + (I ^ X) + (Z ^ I) + (I ^ Z)

        # Initial state
        initial_state = Statevector.from_label('00')

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Trotter-Suzuki evolution (second order)
        trotter_suzuki = TrotterSuzuki(reps=1, order=2)
        trotter_op = trotter_suzuki.convert(hamiltonian, self.dt)

        # Convert to a matrix operator for comparison
        trotter_matrix = trotter_op.to_matrix()

        # Evolve the initial state using Trotter
        trotter_state = trotter_matrix @ initial_state

        # Compare the results
        np.testing.assert_allclose(trotter_state, exact_state, atol=1e-2)

    def test_lie_trotter_evolution(self):
        """Tests Lie-Trotter evolution."""
        # Define a Hamiltonian (e.g., X + Z on each qubit)
        hamiltonian = (X ^ I) + (I ^ X) + (Z ^ I) + (I ^ Z)

        # Initial state
        initial_state = Statevector.from_label('00')

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Lie-Trotter evolution
        lie_trotter = LieTrotter(reps=1)
        trotter_op = lie_trotter.convert(hamiltonian, self.dt)

        # Convert to a matrix operator for comparison
        trotter_matrix = trotter_op.to_matrix()

        # Evolve the initial state using Trotter
        trotter_state = trotter_matrix @ initial_state

        # Compare the results
        np.testing.assert_allclose(trotter_state, exact_state, atol=1e-2)

    def test_trotter_qrte_algorithm(self):
        """Tests the TrotterQRTE algorithm."""
        # Define a Hamiltonian (e.g., XX + YY + ZZ)
        hamiltonian = (X ^ X) + (Y ^ Y) + (Z ^ Z)

        # Initial state
        initial_state = Statevector.from_label('00')

        # Time evolution problem
        problem = TimeEvolutionProblem(hamiltonian, time=self.dt, initial_state=initial_state)

        # TrotterQRTE algorithm
        trotter_qrte = TrotterQRTE(
            sampler=self.simulator,
            trotter_steps=1,
            evolution=Trotter(n=1)
        )

        # Solve the problem
        result = trotter_qrte.solve(problem)

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Compare the results
        np.testing.assert_allclose(result.evolved_state, exact_state, atol=1e-2)

    def test_trotter_with_circuit_hamiltonian(self):
        """Tests Trotter evolution with a Hamiltonian defined as a QuantumCircuit."""
        # Create a simple circuit Hamiltonian (e.g., H on each qubit)
        circuit_hamiltonian = QuantumCircuit(self.num_qubits)
        for i in range(self.num_qubits):
            circuit_hamiltonian.h(i)

        # Convert the circuit to an Operator
        hamiltonian_op = Operator(circuit_hamiltonian)

        # Initial state
        initial_state = Statevector.from_label('00')

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian_op).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Trotter evolution
        trotter = Trotter(n=1)
        trotter_op = trotter.convert(hamiltonian_op, self.dt)

        # Convert to a matrix operator for comparison
        trotter_matrix = trotter_op.to_matrix()

        # Evolve the initial state using Trotter
        trotter_state = trotter_matrix @ initial_state

        # Compare the results
        np.testing.assert_allclose(trotter_state, exact_state, atol=1e-2)

    def test_trotter_with_pauli_sum_hamiltonian(self):
        """Tests Trotter evolution with a PauliSumOp Hamiltonian."""
        # Define a Hamiltonian as a sum of Pauli strings (e.g., X + Y + Z on each qubit)
        hamiltonian = PauliOp(X) + PauliOp(Y) + PauliOp(Z)

        # Initial state
        initial_state = Statevector.from_label('0')

        # Exact evolution operator
        exact_op = (self.dt * hamiltonian).expm()
        exact_state = exact_op.to_matrix() @ initial_state

        # Trotter evolution
        trotter = Trotter(n=1)
        trotter_op = trotter.convert(hamiltonian, self.dt)

        # Convert to a matrix operator for comparison
        trotter_matrix = trotter_op.to_matrix()

        # Evolve the initial state using Trotter
        trotter_state = trotter_matrix @ initial_state

        # Compare the results
        np.testing.assert_allclose(trotter_state, exact_state, atol=1e-2)

if __name__ == '__main__':
    unittest.main()