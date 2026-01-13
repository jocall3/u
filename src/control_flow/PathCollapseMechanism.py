import cmath
import random
from typing import List, Dict, Any, Callable, TypeVar, Generic, Optional

# Define a generic type for the state of an execution path. This allows the framework
# to be agnostic about the actual data structure representing the program's state.
StateType = TypeVar('StateType')

class ExecutionPath(Generic[StateType]):
    """
    Represents a single, potential execution path within a superposition of states.

    Each path is analogous to a basis state in a quantum system, characterized by its
    state vector and a complex probability amplitude. The probability of this path
    being the outcome upon collapse is the squared magnitude of its amplitude.
    """

    def __init__(self, state: StateType, amplitude: complex = 1.0, history: Optional[List[str]] = None):
        """
        Initializes a new execution path.

        Args:
            state (StateType): The specific state of the system for this path.
                               This could be a dictionary of variables, an object, etc.
            amplitude (complex): The probability amplitude associated with this path.
                                 Defaults to 1.0, representing a certain state initially.
            history (Optional[List[str]]): A log of operations or decisions that led to this path.
        """
        if not isinstance(amplitude, complex):
            amplitude = complex(amplitude)

        self.state: StateType = state
        self.amplitude: complex = amplitude
        self.history: List[str] = history if history is not None else []

    @property
    def probability(self) -> float:
        """
        Calculates the probability of this path being realized upon measurement.
        It is the squared magnitude of the complex amplitude, as per the Born rule.
        """
        return self.amplitude.real**2 + self.amplitude.imag**2

    def __repr__(self) -> str:
        return (f"ExecutionPath(state={self.state}, "
                f"amplitude={self.amplitude:.4f}, "
                f"probability={self.probability:.4f})")

    def evolve(self, operation_description: str, new_state: StateType, amplitude_modifier: complex) -> 'ExecutionPath[StateType]':
        """
        Creates a new path by evolving the current one through an operation.

        This method is immutable; it returns a new ExecutionPath instance rather
        than modifying the current one.

        Args:
            operation_description (str): A description of the operation being applied.
            new_state (StateType): The resulting state after the operation.
            amplitude_modifier (complex): A complex number to multiply the current amplitude by.

        Returns:
            ExecutionPath[StateType]: A new ExecutionPath instance representing the state after the operation.
        """
        new_amplitude = self.amplitude * amplitude_modifier
        new_history = self.history + [operation_description]
        return ExecutionPath(state=new_state, amplitude=new_amplitude, history=new_history)


class Superposition(Generic[StateType]):
    """
    Manages a collection of coexisting ExecutionPaths.

    This class represents the state of the system before a measurement or collapse,
    where multiple outcomes are simultaneously possible. It provides methods to
    manipulate the set of paths and ensure quantum-mechanical principles like
    normalization are maintained.
    """

    def __init__(self, paths: List[ExecutionPath[StateType]]):
        """
        Initializes the superposition with a list of execution paths.

        Args:
            paths (List[ExecutionPath[StateType]]): The initial set of paths.
        """
        self.paths: List[ExecutionPath[StateType]] = paths
        self.normalize()

    @classmethod
    def from_single_state(cls, initial_state: StateType) -> 'Superposition[StateType]':
        """Creates a superposition starting from a single, certain classical state."""
        return cls([ExecutionPath(state=initial_state, amplitude=1.0)])

    def normalize(self):
        """
        Normalizes the amplitudes of all paths in the superposition.

        The sum of the probabilities (squared magnitudes of amplitudes) of all paths
        must equal 1. This method scales all amplitudes to enforce this constraint,
        conserving probability.
        """
        total_probability = sum(path.probability for path in self.paths)
        if total_probability <= 1e-9:  # Use a small epsilon to handle floating point inaccuracies
            # If total probability is effectively zero, we cannot normalize.
            # This can happen if all paths are pruned or have zero amplitude.
            return

        norm_factor = cmath.sqrt(total_probability)
        for path in self.paths:
            path.amplitude /= norm_factor

    def apply_gate(self, gate: Callable[[StateType], List[tuple[StateType, complex]]]):
        """
        Applies a quantum-like gate to the entire superposition.

        A 'gate' is a function that takes a single state and returns a list of
        possible resulting states, each with a corresponding amplitude modifier.
        This is how branching (superposition) and interference are introduced.

        Args:
            gate (Callable[[StateType], List[tuple[StateType, complex]]]):
                A function mapping an input state to a list of (output_state, amplitude_modifier) tuples.
        """
        new_paths: List[ExecutionPath[StateType]] = []
        for path in self.paths:
            # Each path evolves according to the gate's transformation
            evolutions = gate(path.state)
            for new_state, amp_mod in evolutions:
                op_desc = f"Applied gate '{gate.__name__}' -> state {new_state}"
                new_paths.append(path.evolve(op_desc, new_state, amp_mod))

        # A full quantum simulator would handle interference by combining paths with identical states.
        # For this pseudocode, we assume states are unique after a gate or that merging is
        # handled by a higher-level process.
        self.paths = new_paths
        self.normalize()

    def __repr__(self) -> str:
        if not self.paths:
            return "Superposition(paths=[])"
        path_reprs = "\n  ".join(repr(p) for p in self.paths)
        return f"Superposition(paths=[\n  {path_reprs}\n])"


class PathCollapseMechanism:
    """
    Implements the logic for collapsing a Superposition into a single, definite ExecutionPath.

    This mechanism acts as the "observer" in the system. It can use various strategies
    to resolve the quantum uncertainty, effectively choosing one reality from the
    many possibilities encoded in the superposition.
    """

    def __init__(self, strategy: Callable[['Superposition'], ExecutionPath]):
        """
        Initializes the collapse mechanism with a specific strategy.

        Args:
            strategy (Callable[['Superposition'], ExecutionPath]): A function that takes
                a Superposition and returns a single ExecutionPath. Pre-defined
                strategies are available as static methods (e.g., probabilistic_collapse).
        """
        self.strategy = strategy

    def collapse(self, superposition: Superposition[StateType]) -> ExecutionPath[StateType]:
        """
        Performs the collapse operation on a given superposition.

        Args:
            superposition (Superposition[StateType]): The superposition of states to collapse.

        Returns:
            ExecutionPath[StateType]: The single, resolved path chosen from the superposition.
        """
        if not superposition.paths:
            raise ValueError("Cannot collapse an empty superposition.")

        # Ensure the state is normalized before collapse, as probabilities must sum to 1.
        superposition.normalize()
        return self.strategy(superposition)

    @staticmethod
    def probabilistic_collapse(superposition: Superposition[StateType]) -> ExecutionPath[StateType]:
        """
        Strategy: Collapses the superposition based on quantum probabilities.

        A path is chosen randomly, with the likelihood of each path being selected
        proportional to its calculated probability (the squared magnitude of its amplitude).
        This mimics the measurement postulate of quantum mechanics.
        """
        probabilities = [path.probability for path in superposition.paths]
        chosen_path = random.choices(superposition.paths, weights=probabilities, k=1)[0]
        
        # After collapse, the chosen path becomes the new reality with probability 1.
        # We return a new instance to represent this definite state.
        return ExecutionPath(state=chosen_path.state, amplitude=1.0, history=chosen_path.history + ["Collapsed (Probabilistic)"])

    @staticmethod
    def constraint_driven_collapse(
        constraint: Callable[[StateType], bool]
    ) -> Callable[['Superposition'], ExecutionPath[StateType]]:
        """
        Factory for a strategy: Filters paths based on a constraint, then collapses the remainder.

        This represents a measurement that asks a specific question (the constraint).
        All paths inconsistent with the answer are eliminated (decoherence), and the
        system collapses into one of the remaining valid states.

        Args:
            constraint (Callable[[StateType], bool]): A function that returns True if a
                state satisfies the constraint, False otherwise.

        Returns:
            A collapse strategy function.
        """
        def strategy(superposition: Superposition[StateType]) -> ExecutionPath[StateType]:
            # Filter paths that satisfy the constraint
            valid_paths = [path for path in superposition.paths if constraint(path.state)]

            if not valid_paths:
                raise ValueError(f"No path satisfies the given constraint '{constraint.__name__}'. The system is in an impossible state.")

            # Create a new superposition from the valid paths and re-normalize
            filtered_superposition = Superposition(valid_paths)
            
            # Collapse the remaining superposition using the standard probabilistic method
            collapsed_path = PathCollapseMechanism.probabilistic_collapse(filtered_superposition)
            collapsed_path.history.append(f"Collapsed (Constraint: {constraint.__name__})")
            return collapsed_path

        return strategy

    @staticmethod
    def maximal_value_collapse(
        value_func: Callable[[StateType], float]
    ) -> Callable[['Superposition'], ExecutionPath[StateType]]:
        """
        Factory for a strategy: Collapses to the path that maximizes a certain value.

        This is a deterministic collapse strategy, useful for optimization problems where
        the "best" path is chosen rather than a random one. It's less physically realistic
        but pragmatically useful in computational contexts.

        Args:
            value_func (Callable[[StateType], float]): A function that computes a scalar
                value from a state.

        Returns:
            A collapse strategy function.
        """
        def strategy(superposition: Superposition[StateType]) -> ExecutionPath[StateType]:
            if not superposition.paths:
                raise ValueError("Cannot collapse an empty superposition.")

            chosen_path = max(superposition.paths, key=lambda p: value_func(p.state))
            
            return ExecutionPath(state=chosen_path.state, amplitude=1.0, history=chosen_path.history + [f"Collapsed (Max Value: {value_func.__name__})"])

        return strategy


# --- Example Usage ---
if __name__ == '__main__':
    # This section demonstrates the concepts in a simplified, illustrative manner.

    # Define a simple state as a dictionary
    MyState = Dict[str, Any]

    # 1. INITIALIZATION: Start with a single, definite state.
    print("--- 1. Initialization ---")
    initial_state: MyState = {'position': 0, 'momentum': 0}
    system_superposition = Superposition.from_single_state(initial_state)
    print(f"Initial System State:\n{system_superposition}\n")

    # 2. SUPERPOSITION CREATION: Apply a "gate" that creates multiple paths.
    # Let's define a Hadamard-like gate for our system.
    # It splits a path into two, one moving left, one right, with equal amplitude.
    def move_split_gate(state: MyState) -> List[tuple[MyState, complex]]:
        """A gate that splits a particle's path."""
        # State where particle moves left
        state_left = state.copy()
        state_left['position'] -= 1
        state_left['momentum'] = -1
        
        # State where particle moves right
        state_right = state.copy()
        state_right['position'] += 1
        state_right['momentum'] = 1
        
        # Return both outcomes, each with an amplitude modifier of 1/sqrt(2)
        modifier = 1 / cmath.sqrt(2)
        return [(state_left, modifier), (state_right, modifier)]

    print("--- 2. Applying a Gate to Create Superposition ---")
    system_superposition.apply_gate(move_split_gate)
    print(f"System after 'move_split_gate':\n{system_superposition}\n")
    # Note: Each path now has a probability of 0.5 ( (1/sqrt(2))^2 )

    # Apply the gate again to create more paths and demonstrate interference potential
    system_superposition.apply_gate(move_split_gate)
    print(f"System after second 'move_split_gate':\n{system_superposition}\n")
    # We would expect paths: pos=-2, pos=0, pos=0, pos=2.
    # A full implementation would merge the two pos=0 paths. For this pseudocode, we see them separately.

    # 3. COLLAPSE: Use a mechanism to resolve the superposition into one reality.

    # --- Scenario A: Probabilistic Collapse ---
    print("--- 3a. Probabilistic Collapse ---")
    probabilistic_collapser = PathCollapseMechanism(strategy=PathCollapseMechanism.probabilistic_collapse)
    final_state_A = probabilistic_collapser.collapse(system_superposition)
    print(f"Collapsed to a single reality (probabilistic):\n{final_state_A}\n")
    print(f"History of the chosen reality:\n" + "\n".join(f"  - {h}" for h in final_state_A.history))
    print("-" * 20)

    # --- Scenario B: Constraint-Driven Collapse ---
    print("\n--- 3b. Constraint-Driven Collapse ---")
    # Let's define a constraint: we "measure" the particle and find it's on the right side (position > 0).
    def is_on_right_side(state: MyState) -> bool:
        return state['position'] > 0

    constraint_strategy = PathCollapseMechanism.constraint_driven_collapse(constraint=is_on_right_side)
    constraint_collapser = PathCollapseMechanism(strategy=constraint_strategy)
    
    try:
        final_state_B = constraint_collapser.collapse(system_superposition)
        print(f"Collapsed to a reality where position > 0:\n{final_state_B}\n")
        print(f"History of the chosen reality:\n" + "\n".join(f"  - {h}" for h in final_state_B.history))
    except ValueError as e:
        print(f"Collapse failed: {e}")
    print("-" * 20)

    # --- Scenario C: Deterministic Collapse based on a value ---
    print("\n--- 3c. Maximal Value Collapse ---")
    # Let's say we want to collapse to the state with the highest momentum (a trivial example).
    # A better example would be a state that minimizes a cost function.
    def get_position(state: MyState) -> float:
        return float(state['position'])

    # Collapse to the path with the maximum position
    max_pos_strategy = PathCollapseMechanism.maximal_value_collapse(value_func=get_position)
    max_pos_collapser = PathCollapseMechanism(strategy=max_pos_strategy)
    final_state_C = max_pos_collapser.collapse(system_superposition)
    print(f"Collapsed to the reality with maximum position:\n{final_state_C}\n")
    print(f"History of the chosen reality:\n" + "\n".join(f"  - {h}" for h in final_state_C.history))
    print("-" * 20)