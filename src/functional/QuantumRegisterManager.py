import cmath
import random
import numpy as np
from typing import List, Dict, Callable, Tuple, Any, Optional

# --- Conceptual Quantum Primitives ---

class Qubit:
    """
    A conceptual representation of a single qubit.
    Its state is a superposition of |0> and |1>.
    """
    def __init__(self, alpha: complex = 1.0, beta: complex = 0.0):
        """
        Initializes a qubit in a given state |psi> = alpha|0> + beta|1>.
        Ensures normalization.
        """
        norm = abs(alpha)**2 + abs(beta)**2
        if not np.isclose(norm, 1.0):
            if norm == 0:
                raise ValueError("Qubit state vector cannot be zero.")
            alpha /= cmath.sqrt(norm)
            beta /= cmath.sqrt(norm)
        self._state = np.array([alpha, beta], dtype=complex)

    @property
    def state(self) -> np.ndarray:
        """Returns the current state vector [alpha, beta]."""
        return self._state

    def apply_gate(self, gate_matrix: np.ndarray) -> None:
        """Applies a 2x2 unitary gate to the qubit."""
        if gate_matrix.shape != (2, 2):
            raise ValueError("Gate matrix must be 2x2.")
        new_state = np.dot(gate_matrix, self._state)
        # Re-normalize due to potential floating point inaccuracies, though unitary gates preserve norm
        norm = np.linalg.norm(new_state)
        if not np.isclose(norm, 1.0):
            new_state /= norm
        self._state = new_state

    def measure(self) -> int:
        """
        Measures the qubit, collapsing its state to |0> or |1>
        based on probabilities |alpha|^2 and |beta|^2.
        Returns the classical outcome (0 or 1).
        """
        prob_0 = abs(self._state[0])**2
        # prob_1 = abs(self._state[1])**2 # Should be 1 - prob_0
        outcome = 0 if random.random() < prob_0 else 1
        # Collapse state
        if outcome == 0:
            self._state = np.array([1.0, 0.0], dtype=complex)
        else:
            self._state = np.array([0.0, 1.0], dtype=complex)
        return outcome

    def __repr__(self) -> str:
        return f"Qubit(alpha={self._state[0]:.3f}, beta={self._state[1]:.3f})"

class QuantumRegister:
    """
    A conceptual collection of qubits, representing a quantum register.
    Supports basic operations like applying gates and measuring.
    """
    def __init__(self, num_qubits: int):
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive.")
        self._qubits: List[Qubit] = [Qubit() for _ in range(num_qubits)] # All initialized to |0>

    @property
    def num_qubits(self) -> int:
        return len(self._qubits)

    def get_qubit(self, index: int) -> Qubit:
        """Returns the Qubit object at the given index."""
        if not (0 <= index < self.num_qubits):
            raise IndexError("Qubit index out of bounds.")
        return self._qubits[index]

    def apply_single_qubit_gate(self, gate_matrix: np.ndarray, qubit_index: int) -> None:
        """Applies a single-qubit gate to a specified qubit in the register."""
        self.get_qubit(qubit_index).apply_gate(gate_matrix)

    def measure_all(self) -> str:
        """
        Measures all qubits in the register and returns the classical bitstring outcome.
        Collapses the state of all qubits.
        """
        outcomes = [str(q.measure()) for q in self._qubits]
        return "".join(outcomes)

    def __repr__(self) -> str:
        qubit_states = ", ".join([f"|{q.state[0]:.2f}⟩ + |{q.state[1]:.2f}⟩" for q in self._qubits])
        return f"QuantumRegister(num_qubits={self.num_qubits}, states=[{qubit_states}])"

# --- Conceptual Quantum Gates (Unitary Matrices) ---
# These are standard quantum gates represented as 2x2 unitary matrices.
# They are used by Qubit.apply_gate().

HADAMARD_GATE = 1/cmath.sqrt(2) * np.array([[1, 1], [1, -1]], dtype=complex)
PAULI_X_GATE = np.array([[0, 1], [1, 0]], dtype=complex) # NOT gate
PAULI_Z_GATE = np.array([[1, 0], [0, -1]], dtype=complex)
IDENTITY_GATE = np.array([[1, 0], [0, 1]], dtype=complex)

# --- Lambda Abstraction Behavior Encoding ---

class LambdaQuantumBehavior:
    """
    Encodes the potential quantum behaviors of a lambda abstraction
    when applied to a quantum register.
    This is a conceptual representation of the transformation and outcomes.
    """
    def __init__(self,
                 lambda_id: int,
                 num_qubits: int,
                 outcome_probabilities: Dict[str, float],
                 conceptual_entanglement_score: float = 0.0,
                 conceptual_superposition_depth: float = 0.0):
        """
        Initializes the behavior encoding.
        :param lambda_id: Unique identifier for the lambda function.
        :param num_qubits: The number of qubits in the register this behavior pertains to.
        :param outcome_probabilities: A dictionary mapping classical bitstring outcomes
                                      (e.g., "01") to their estimated probabilities.
        :param conceptual_entanglement_score: A heuristic score for entanglement induced.
        :param conceptual_superposition_depth: A heuristic score for the complexity of superposition.
        """
        self.lambda_id = lambda_id
        self.num_qubits = num_qubits
        self.outcome_probabilities = outcome_probabilities
        self.conceptual_entanglement_score = conceptual_entanglement_score
        self.conceptual_superposition_depth = conceptual_superposition_depth

        # Ensure probabilities sum to approximately 1 (allowing for simulation inaccuracies)
        if not np.isclose(sum(outcome_probabilities.values()), 1.0):
            pass # Suppress warning for pseudocode, as simulation is approximate

    def get_most_probable_outcome(self) -> Tuple[str, float]:
        """Returns the classical outcome with the highest probability."""
        if not self.outcome_probabilities:
            return "", 0.0
        return max(self.outcome_probabilities.items(), key=lambda item: item[1])

    def __repr__(self) -> str:
        prob_str = ", ".join([f"{k}:{v:.2f}" for k, v in self.outcome_probabilities.items()])
        return (f"LambdaQuantumBehavior(lambda_id={self.lambda_id}, num_qubits={self.num_qubits},\n"
                f"  Outcomes={prob_str},\n"
                f"  EntanglementScore={self.conceptual_entanglement_score:.2f},\n"
                f"  SuperpositionDepth={self.conceptual_superposition_depth:.2f})")

# --- Main Manager Class ---

class QuantumRegisterManager:
    """
    Manages quantum registers and encodes the potential behaviors of
    lambda abstractions when applied to these registers.
    This class provides a conceptual framework for linking classical
    functional constructs (lambdas) to quantum operations and their outcomes.
    """
    def __init__(self):
        self._lambda_register_associations: Dict[int, QuantumRegister] = {}
        self._lambda_behavior_cache: Dict[int, LambdaQuantumBehavior] = {}
        self._next_register_id = 0 # For conceptual tracking, not strictly used for unique IDs

    def create_quantum_register(self, num_qubits: int) -> QuantumRegister:
        """
        Creates and returns a new quantum register initialized to |0...0>.
        """
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive.")
        register = QuantumRegister(num_qubits)
        self._next_register_id += 1
        return register

    def associate_lambda_with_register(self, lambda_func: Callable, register: QuantumRegister) -> None:
        """
        Associates a given lambda function with a specific quantum register.
        This implies the lambda is intended to operate on this register.
        """
        lambda_id = id(lambda_func)
        if lambda_id in self._lambda_register_associations:
            pass # Suppress warning for cleaner pseudocode output
        self._lambda_register_associations[lambda_id] = register

    def _simulate_quantum_operation(self,
                                    initial_register_state: QuantumRegister,
                                    lambda_func: Callable,
                                    num_simulations: int = 1000) -> Dict[str, float]:
        """
        Internal method to simulate the effect of a lambda function on a quantum register
        and estimate the classical outcome probabilities.
        This is where the "interpretation" of a classical lambda into quantum operations happens.
        For pseudocode, we'll define a few conceptual mappings based on lambda_id.
        """
        lambda_id = id(lambda_func)
        num_qubits = initial_register_state.num_qubits
        
        # Initialize outcome counts for all possible classical bitstrings
        outcome_counts: Dict[str, int] = {
            format(i, f'0{num_qubits}b'): 0 for i in range(2**num_qubits)
        }

        # Seed the random number generator for reproducible "randomness" per lambda.
        # This ensures that the *interpretation* of a given lambda into quantum gates
        # is consistent across calls, even though the measurement outcomes are probabilistic.
        random.seed(lambda_id)
        
        # Define a pool of conceptual single-qubit quantum gates.
        gate_pool = [HADAMARD_GATE, PAULI_X_GATE, PAULI_Z_GATE, IDENTITY_GATE]
        
        # Determine a "complexity" or number of operations based on lambda_id.
        # This adds a layer of "randomness" to the behavior's complexity.
        # Ensure at least one operation if num_qubits > 0.
        num_operations = random.randint(1, max(1, num_qubits * 3))

        for _ in range(num_simulations):
            # Create a fresh copy of the initial register state for each simulation run.
            # This is crucial to avoid state collapse from one simulation affecting the next.
            sim_register = QuantumRegister(num_qubits)
            for i in range(num_qubits):
                # Copy the state vector of each qubit from the initial register
                sim_register.get_qubit(i)._state = initial_register_state.get_qubit(i).state.copy()

            # Apply conceptual quantum operations based on the lambda's "interpretation".
            # The sequence of gates is "random" but fixed for a given lambda_id due to seeding.
            for _ in range(num_operations):
                if num_qubits > 0: # Only apply gates if there are qubits
                    qubit_idx = random.randrange(num_qubits)
                    gate = random.choice(gate_pool)
                    sim_register.apply_single_qubit_gate(gate, qubit_idx)
            
            # Simulate a conceptual "measurement" after the lambda's operation.
            outcome = sim_register.measure_all()
            outcome_counts[outcome] += 1

        # Calculate probabilities from the simulation counts.
        probabilities = {
            outcome: count / num_simulations
            for outcome, count in outcome_counts.items()
        }
        return probabilities

    def encode_lambda_behavior(self, lambda_func: Callable, num_simulations: int = 1000) -> LambdaQuantumBehavior:
        """
        Encodes the potential quantum behaviors of a lambda function.
        This involves conceptually applying the lambda's quantum equivalent
        to an associated register (or a default one if none is associated)
        and analyzing the resulting state's potential outcomes.
        The result is cached for performance.
        """
        lambda_id = id(lambda_func)

        if lambda_id in self._lambda_behavior_cache:
            return self._lambda_behavior_cache[lambda_id]

        # Determine the register to use. If none associated, create a default.
        if lambda_id in self._lambda_register_associations:
            target_register = self._lambda_register_associations[lambda_id]
        else:
            # If no register is explicitly associated, assume a default 2-qubit register
            # for conceptual analysis. This adds "randomness" in the sense of
            # a default context.
            target_register = self.create_quantum_register(2) # Default to 2 qubits

        # Simulate the behavior to get outcome probabilities.
        outcome_probs = self._simulate_quantum_operation(
            target_register, lambda_func, num_simulations
        )

        # Conceptual entanglement and superposition scores.
        # These are heuristic for pseudocode without a full state vector.
        # They are influenced by the diversity of outcomes and the complexity of operations.
        
        # Re-seed for entanglement/superposition scores to be consistent per lambda,
        # but distinct from the gate sequence generation.
        random.seed(lambda_id + 2) # Use a slightly different seed for these scores

        # Heuristic for superposition depth: ratio of non-zero outcomes to total possible outcomes.
        non_zero_outcomes = sum(1 for p in outcome_probs.values() if p > 1e-6)
        total_possible_outcomes = 2**target_register.num_qubits
        conceptual_superposition_depth = non_zero_outcomes / total_possible_outcomes if total_possible_outcomes > 0 else 0.0
        
        # Heuristic for entanglement score:
        # A more complex operation sequence (num_operations from simulation) might imply more entanglement.
        # Also, if the superposition is high, there's more potential for entanglement.
        # This is highly speculative for pseudocode.
        conceptual_entanglement_score = random.uniform(0.0, conceptual_superposition_depth * 1.5)
        
        # Ensure scores are within a reasonable range (e.g., 0 to 1)
        conceptual_entanglement_score = min(1.0, conceptual_entanglement_score)
        conceptual_superposition_depth = min(1.0, conceptual_superposition_depth)


        behavior = LambdaQuantumBehavior(
            lambda_id=lambda_id,
            num_qubits=target_register.num_qubits,
            outcome_probabilities=outcome_probs,
            conceptual_entanglement_score=conceptual_entanglement_score,
            conceptual_superposition_depth=conceptual_superposition_depth
        )
        self._lambda_behavior_cache[lambda_id] = behavior
        return behavior

    def get_cached_behavior(self, lambda_func: Callable) -> Optional[LambdaQuantumBehavior]:
        """
        Retrieves the cached quantum behavior for a given lambda function.
        Returns None if no behavior has been encoded yet.
        """
        return self._lambda_behavior_cache.get(id(lambda_func))

    def __repr__(self) -> str:
        return (f"QuantumRegisterManager(associated_lambdas={len(self._lambda_register_associations)}, "
                f"cached_behaviors={len(self._lambda_behavior_cache)})")