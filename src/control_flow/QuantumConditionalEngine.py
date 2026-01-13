import numpy as np
from typing import List, Callable, Tuple

# Pseudocode for a Quantum Conditional Engine
# This engine demonstrates the conceptual application of amplitude amplification
# for resolving branching logic in a quantum context.
# It does not implement a full quantum simulator but illustrates the principles.

class QuantumConditionalEngine:
    """
    A conceptual engine demonstrating quantum conditional logic using amplitude amplification.

    This class provides pseudocode for how one might design a quantum system
    to make a 'branching' decision by amplifying the probability of a desired
    outcome state, rather than classical if/else constructs.

    The core idea is to:
    1. Encode potential branch outcomes into quantum states (basis states of a register).
    2. Prepare the system in a uniform superposition of all possible branch states.
    3. Define a quantum oracle that marks the 'desired' branch state(s) based
       on a quantum condition by applying a phase shift.
    4. Apply amplitude amplification (Grover-like iterations) to boost the
       probability of measuring the marked state(s).
    5. Measure the system to collapse into the amplified desired branch with high probability.
    """

    def __init__(self, num_branches: int):
        """
        Initializes the Quantum Conditional Engine.

        Args:
            num_branches (int): The number of potential branches (outcomes)
                                 the quantum system can decide between.
                                 These are represented by basis states |0>, |1>, ..., |num_branches-1>.
        """
        if num_branches < 2:
            raise ValueError("At least two branches are required for conditional logic.")

        self.num_branches = num_branches
        # Determine the minimum number of qubits required to represent all branches.
        # E.g., 2 branches -> 1 qubit, 3-4 branches -> 2 qubits, 5-8 branches -> 3 qubits.
        self.num_qubits = int(np.ceil(np.log2(num_branches)))
        
        # The total number of basis states available in the quantum register.
        # This will be 2^num_qubits.
        self.total_basis_states = 2**self.num_qubits

        # Represents the quantum state of the system as a vector of amplitudes.
        # Initially, all basis states are in a uniform superposition.
        # Conceptually, this is achieved by applying Hadamard gates to all qubits
        # initialized in the |0> state.
        self.amplitudes = np.ones(self.total_basis_states, dtype=complex) / np.sqrt(self.total_basis_states)
        
        print(f"Engine initialized for {num_branches} branches ({self.num_qubits} qubits).")
        print(f"Total basis states available: {self.total_basis_states}")
        print(f"Initial state (uniform superposition): {self.amplitudes}")

    def _quantum_oracle(self, condition_function: Callable[[int], bool]) -> None:
        """
        Conceptual quantum oracle that marks states satisfying a given condition.

        In a real quantum circuit, this would apply a phase shift (e.g., -1)
        to the amplitude of states |x> for which condition_function(x) is True.
        The oracle only considers states up to `self.num_branches - 1`.

        Args:
            condition_function (Callable[[int], bool]): A classical function
                                                        representing the quantum
                                                        condition. It takes an
                                                        integer (representing a
                                                        branch index) and returns
                                                        True if that branch satisfies
                                                        the condition, False otherwise.
        """
        print(f"\nApplying quantum oracle with condition: {condition_function.__name__}")
        marked_states = []
        for i in range(self.num_branches): # Only iterate over valid branches
            if condition_function(i):
                self.amplitudes[i] *= -1  # Apply a phase flip
                marked_states.append(i)
        print(f"States marked by oracle: {marked_states}")
        print(f"State after oracle: {self.amplitudes}")

    def _diffusion_operator(self) -> None:
        """
        Conceptual diffusion operator (Grover's inversion about the mean).

        This operator amplifies the amplitudes of the marked states and
        decreases the amplitudes of the unmarked states.
        It's defined as 2|s><s| - I, where |s> is the uniform superposition
        of all *valid* basis states (0 to total_basis_states-1).
        """
        print("\nApplying diffusion operator...")
        # Calculate the mean amplitude across all basis states
        mean_amplitude = np.mean(self.amplitudes)
        
        # Apply the diffusion transformation: |psi> -> 2<s|psi>|s> - |psi>
        # Where |s> is the uniform superposition state.
        for i in range(self.total_basis_states):
            self.amplitudes[i] = 2 * mean_amplitude - self.amplitudes[i]
        print(f"State after diffusion: {self.amplitudes}")

    def amplify_branch(self, condition_function: Callable[[int], bool], iterations: int = 1) -> None:
        """
        Applies amplitude amplification to boost the probability of branches
        satisfying the given quantum condition.

        The number of iterations is crucial for optimal amplification. For N total
        states and M marked (solution) states, the optimal number of iterations
        is approximately (pi/4) * sqrt(N/M). Too few iterations might not amplify
        enough, too many can cause the amplitude to overshoot and decrease again.

        Args:
            condition_function (Callable[[int], bool]): The quantum condition
                                                        function.
            iterations (int): The number of Grover-like iterations to perform.
        """
        print(f"\n--- Starting Amplitude Amplification for {iterations} iterations ---")
        for i in range(iterations):
            print(f"\n--- Iteration {i+1}/{iterations} ---")
            self._quantum_oracle(condition_function)
            self._diffusion_operator()
        print("\n--- Amplitude Amplification Complete ---")

    def measure_branch(self) -> int:
        """
        Measures the quantum state to determine the chosen branch.

        In a real quantum computer, this would involve a physical measurement
        collapsing the superposition. Here, we simulate probabilistic measurement
        based on the squared amplitudes.

        Returns:
            int: The index of the chosen branch (outcome).
        """
        print("\nMeasuring the quantum state to determine the branch...")
        probabilities = np.abs(self.amplitudes)**2
        # Normalize probabilities in case of floating point inaccuracies
        probabilities /= np.sum(probabilities)

        print(f"Final amplitudes: {self.amplitudes}")
        print(f"Probabilities of each basis state: {probabilities}")

        # Simulate measurement by picking an index based on probabilities
        chosen_basis_state = np.random.choice(self.total_basis_states, p=probabilities)

        # If num_branches is not a power of 2, some basis states might not correspond
        # to a defined branch. We re-measure until a valid branch is chosen.
        # In a real algorithm, one might design the oracle to only mark valid states
        # or ensure invalid states have zero amplitude.
        while chosen_basis_state >= self.num_branches:
            print(f"Warning: Measured basis state {chosen_basis_state} is outside the defined {self.num_branches} branches. Re-measuring...")
            chosen_basis_state = np.random.choice(self.total_basis_states, p=probabilities)

        print(f"Quantum measurement collapsed to Branch {chosen_basis_state}.")
        return chosen_basis_state

    def execute_branch_logic(self, chosen_branch: int, branch_actions: List[Callable[[], None]]) -> None:
        """
        Executes the classical logic associated with the chosen quantum branch.

        Args:
            chosen_branch (int): The index of the branch chosen by quantum measurement.
            branch_actions (List[Callable[[], None]]): A list of functions, where
                                                        each function corresponds
                                                        to the action of a specific branch.
        """
        if 0 <= chosen_branch < len(branch_actions):
            print(f"\nExecuting classical logic for Branch {chosen_branch}...")
            branch_actions[chosen_branch]()
        else:
            print(f"\nError: No classical action defined for Branch {chosen_branch}. This should not happen after re-measurement.")

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Quantum Conditional Engine Demonstration ---")
    print("This pseudocode illustrates the *concept* of quantum branching,")
    print("not a runnable quantum simulation on real hardware.")

    # Define classical actions for each branch
    def branch_action_0():
        print("Action for Branch 0: 'Initiate standard procedure.'")

    def branch_action_1():
        print("Action for Branch 1: 'Engage advanced security protocols.'")

    def branch_action_2():
        print("Action for Branch 2: 'Reroute power to auxiliary systems.'")

    def branch_action_3():
        print("Action for Branch 3: 'Prepare for quantum entanglement communication.'")

    def branch_action_4():
        print("Action for Branch 4: 'Activate temporal displacement field.'")

    def branch_action_5():
        print("Action for Branch 5: 'Synthesize exotic matter catalyst.'")

    all_branch_actions = [
        branch_action_0,
        branch_action_1,
        branch_action_2,
        branch_action_3,
        branch_action_4,
        branch_action_5,
    ]
    num_total_branches = len(all_branch_actions)

    # Scenario 1: Amplify a specific branch (e.g., Branch 1)
    print("\n\n" + "="*60)
    print("Scenario 1: Amplifying Branch 1 (Advanced Security)")
    print("="*60)
    engine1 = QuantumConditionalEngine(num_branches=num_total_branches)

    # Define a quantum condition: "Is the branch index 1?"
    def is_branch_1(branch_index: int) -> bool:
        return branch_index == 1

    # Apply amplitude amplification
    # For N=8 (total basis states for 6 branches), M=1 (Branch 1 is the only solution),
    # optimal iterations are approx (pi/4) * sqrt(N/M) = (pi/4) * sqrt(8/1) approx 0.785 * 2.828 approx 2.22.
    # So 2 iterations should be good.
    engine1.amplify_branch(condition_function=is_branch_1, iterations=2)

    # Measure and execute
    chosen_branch_1 = engine1.measure_branch()
    engine1.execute_branch_logic(chosen_branch_1, all_branch_actions)

    # Scenario 2: Amplify multiple branches (e.g., Branch 0 or Branch 3)
    print("\n\n" + "="*60)
    print("Scenario 2: Amplifying Branch 0 OR Branch 3 (Standard or Entanglement)")
    print("="*60)
    engine2 = QuantumConditionalEngine(num_branches=num_total_branches)

    # Define a quantum condition: "Is the branch index 0 or 3?"
    def is_branch_0_or_3(branch_index: int) -> bool:
        return branch_index == 0 or branch_index == 3

    # For N=8, M=2 solutions, optimal iterations are approx (pi/4) * sqrt(8/2) = (pi/4) * sqrt(4) approx 0.785 * 2 approx 1.57.
    # So 1 or 2 iterations are good. Let's use 1 to show a different iteration count.
    engine2.amplify_branch(condition_function=is_branch_0_or_3, iterations=1)

    # Measure and execute
    chosen_branch_2 = engine2.measure_branch()
    engine2.execute_branch_logic(chosen_branch_2, all_branch_actions)

    # Scenario 3: No amplification (should be close to uniform probability for valid branches)
    print("\n\n" + "="*60)
    print("Scenario 3: No Amplification (Random Branch Selection)")
    print("="*60)
    engine3 = QuantumConditionalEngine(num_branches=num_total_branches)

    # No amplification steps, just measure the initial uniform superposition
    chosen_branch_3 = engine3.measure_branch()
    engine3.execute_branch_logic(chosen_branch_3, all_branch_actions)

    # Scenario 4: Over-amplification (e.g., 4 iterations for Branch 2)
    print("\n\n" + "="*60)
    print("Scenario 4: Over-amplification (4 iterations for Branch 2)")
    print("="*60)
    engine4 = QuantumConditionalEngine(num_branches=num_total_branches)

    def is_branch_2(branch_index: int) -> bool:
        return branch_index == 2

    # Optimal is ~2.22 iterations. 4 iterations will likely overshoot and reduce probability.
    engine4.amplify_branch(condition_function=is_branch_2, iterations=4)

    chosen_branch_4 = engine4.measure_branch()
    engine4.execute_branch_logic(chosen_branch_4, all_branch_actions)

    # Scenario 5: Attempting to amplify a branch that doesn't exist in the initial `num_branches`
    # This scenario highlights the importance of the condition_function and problem setup.
    print("\n\n" + "="*60)
    print("Scenario 5: Attempting to amplify a non-existent branch (Branch 10)")
    print("="*60)
    engine5 = QuantumConditionalEngine(num_branches=num_total_branches)

    def is_branch_10(branch_index: int) -> bool:
        # This condition will never be true for branch_index < num_total_branches (6)
        return branch_index == 10

    # The oracle will mark nothing, so amplification won't happen for this specific branch.
    # The state will remain largely uniform superposition (or slightly perturbed).
    engine5.amplify_branch(condition_function=is_branch_10, iterations=2)

    chosen_branch_5 = engine5.measure_branch()
    engine5.execute_branch_logic(chosen_branch_5, all_branch_actions)