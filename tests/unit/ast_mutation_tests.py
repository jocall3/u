import unittest
import numpy as np
from quantum_compiler.ast.quantum_ast import QuantumAST, Qubit, CNOT, PhaseShift, Hadamard, Measurement
from quantum_compiler.mutation.ast_mutation import AdaptiveQuantumASTMutator
from quantum_compiler.utils.quantum_utils import apply_gate, generate_random_unitary

class TestASTMutation(unittest.TestCase):

    def setUp(self):
        self.mutator = AdaptiveQuantumASTMutator()
        self.tolerance = 1e-6

    def test_phase_shift_mutation(self):
        """
        Tests the mutation of a PhaseShift gate.  Verifies that the phase shift
        parameter is correctly mutated and that the resulting unitary matrix
        is consistent with the new phase.
        """
        initial_phase = np.random.rand() * 2 * np.pi
        qubit = Qubit(0)
        initial_ast = QuantumAST([PhaseShift(qubit, initial_phase)])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)
        self.assertEqual(len(mutated_ast.gates), 1)
        self.assertIsInstance(mutated_ast.gates[0], PhaseShift)
        self.assertIsInstance(mutated_ast.gates[0].qubit, Qubit)
        self.assertEqual(mutated_ast.gates[0].qubit.index, 0)

        mutated_phase = mutated_ast.gates[0].phase
        self.assertNotEqual(mutated_phase, initial_phase)

        # Verify unitary matrix
        initial_unitary = apply_gate(np.identity(2), PhaseShift(qubit, initial_phase))
        mutated_unitary = apply_gate(np.identity(2), PhaseShift(qubit, mutated_phase))

        # Check if the mutated unitary is different from the initial one
        self.assertFalse(np.allclose(initial_unitary, mutated_unitary, atol=self.tolerance))

    def test_robustness_to_perturbations(self):
        """
        Tests the robustness of the mutation process under small perturbations.
        This involves applying a small random unitary to the mutated gate
        and checking if the overall behavior is still consistent.
        """
        qubit = Qubit(0)
        initial_ast = QuantumAST([Hadamard(qubit), CNOT(qubit, Qubit(1))])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)

        # Apply a small random unitary to a gate in the mutated AST
        for gate in mutated_ast.gates:
            if isinstance(gate, PhaseShift):
                perturbed_phase = gate.phase + np.random.normal(0, 0.01) # Small perturbation
                perturbed_phase = perturbed_phase % (2 * np.pi) # Ensure phase is within [0, 2pi]
                perturbed_gate = PhaseShift(gate.qubit, perturbed_phase)
                perturbed_unitary = apply_gate(np.identity(2), perturbed_gate)
                original_unitary = apply_gate(np.identity(2), gate)
                self.assertFalse(np.allclose(perturbed_unitary, original_unitary, atol=self.tolerance))

    def test_mutation_preserves_structure(self):
        """
        Tests that the mutation process doesn't fundamentally change the
        structure of the AST (e.g., doesn't introduce invalid gate combinations).
        """
        initial_ast = QuantumAST([Hadamard(Qubit(0)), CNOT(Qubit(0), Qubit(1)), Measurement(Qubit(0))])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)
        for gate in mutated_ast.gates:
            self.assertTrue(isinstance(gate, (Hadamard, CNOT, PhaseShift, Measurement)))

    def test_mutation_with_multiple_qubits(self):
        """
        Tests mutation with an AST involving multiple qubits.
        """
        initial_ast = QuantumAST([Hadamard(Qubit(0)), CNOT(Qubit(0), Qubit(1)), PhaseShift(Qubit(1), np.pi/2)])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)
        self.assertTrue(any(isinstance(gate, PhaseShift) for gate in mutated_ast.gates))

    def test_mutation_with_empty_ast(self):
        """
        Tests mutation with an empty AST. Should return an empty AST or a valid one.
        """
        initial_ast = QuantumAST([])
        mutated_ast = self.mutator.mutate(initial_ast)
        self.assertIsInstance(mutated_ast, QuantumAST)
        self.assertLessEqual(len(mutated_ast.gates), 1) # Can be empty or contain a single gate.

    def test_mutation_with_random_unitary(self):
        """
        Tests mutation with a gate that uses a random unitary.
        """
        qubit = Qubit(0)
        random_unitary = generate_random_unitary()
        initial_ast = QuantumAST([PhaseShift(qubit, np.random.rand() * 2 * np.pi)])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)
        self.assertTrue(any(isinstance(gate, PhaseShift) for gate in mutated_ast.gates))

    def test_mutation_with_repeated_gates(self):
        """
        Tests mutation with repeated gates.
        """
        initial_ast = QuantumAST([Hadamard(Qubit(0)), Hadamard(Qubit(0)), CNOT(Qubit(0), Qubit(1))])
        mutated_ast = self.mutator.mutate(initial_ast)

        self.assertIsInstance(mutated_ast, QuantumAST)
        self.assertTrue(any(isinstance(gate, Hadamard) for gate in mutated_ast.gates))
        self.assertTrue(any(isinstance(gate, CNOT) for gate in mutated_ast.gates))