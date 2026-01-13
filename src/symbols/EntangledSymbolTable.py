import cmath
import random
from typing import Dict, List, Tuple, Any, Optional

# --- Conceptual Quantum State Representation ---
class QuantumState:
    """
    Represents a quantum superposition of classical values.
    Each state is a tuple of (classical_value, complex_amplitude).
    The sum of squared magnitudes of amplitudes should be 1 (normalized).
    """
    def __init__(self, initial_states: List[Tuple[Any, complex]]):
        if not initial_states:
            raise ValueError("QuantumState must be initialized with at least one state.")
        self._states = initial_states
        self._normalize_amplitudes()

    def _normalize_amplitudes(self):
        """
        Normalizes the amplitudes such that the sum of |amplitude|^2 is 1.
        This ensures that probabilities sum to 1.
        """
        total_magnitude_squared = sum(abs(amp)**2 for _, amp in self._states)
        
        if total_magnitude_squared == 0:
            # This state is effectively empty or invalid.
            # In a real quantum system, this would imply an unphysical state.
            raise ValueError("Cannot normalize a state with zero total amplitude magnitude.")
        
        factor = 1.0 / cmath.sqrt(total_magnitude_squared)
        self._states = [(val, amp * factor) for val, amp in self._states]

    def add_state(self, value: Any, amplitude: complex):
        """
        Adds a new classical state to the superposition or updates an existing one.
        If the value already exists, its amplitude is combined (summed) with the new one.
        This is a simplification; in true quantum mechanics, adding a state
        might lead to interference effects depending on phases.
        """
        found = False
        for i, (existing_val, existing_amp) in enumerate(self._states):
            if existing_val == value:
                self._states[i] = (value, existing_amp + amplitude)
                found = True
                break
        if not found:
            self._states.append((value, amplitude))
        self._normalize_amplitudes()

    def measure(self) -> Any:
        """
        Performs a 'measurement' on the quantum state, collapsing it to a single
        classical value based on probabilities derived from amplitudes.
        The probability of measuring a specific state is |amplitude|^2.
        """
        probabilities = [abs(amp)**2 for _, amp in self._states]
        
        # Conceptual collapse: Pick one state based on these probabilities.
        # In a real quantum system, this would be handled by the quantum hardware/simulator.
        
        # Create a cumulative distribution for random selection
        cumulative_probabilities = []
        current_sum = 0.0
        for p in probabilities:
            current_sum += p
            cumulative_probabilities.append(current_sum)
        
        # Due to floating point inaccuracies, ensure the last cumulative probability is exactly 1.0
        if cumulative_probabilities:
            cumulative_probabilities[-1] = 1.0

        rand_val = random.random()
        for i, cum_p in enumerate(cumulative_probabilities):
            if rand_val < cum_p:
                return self._states[i][0]
        
        # Fallback: Should not be reached if probabilities are correctly normalized and handled.
        # Returns the value of the last state as a safeguard.
        return self._states[-1][0]

    def get_amplitudes(self) -> List[Tuple[Any, complex]]:
        """Returns the current states and their complex amplitudes."""
        return list(self._states)

    def __repr__(self):
        """Provides a string representation of the QuantumState."""
        state_reprs = []
        for val, amp in self._states:
            # Format complex numbers for readability
            state_reprs.append(f"('{val}', {amp.real:.4f}{'+' if amp.imag >= 0 else ''}{amp.imag:.4f}j)")
        return f"QuantumState([{', '.join(state_reprs)}])"


# --- Entangled Symbol Table ---
class EntangledSymbolTable:
    """
    A conceptual symbol table where entries are represented by quantum states
    and lookups involve 'measurement', potentially collapsing superpositions.
    This pseudocode demonstrates the *idea* of quantum state entries and
    measurement-based lookup, not a true quantum simulation requiring
    specialized quantum computing libraries.
    """
    def __init__(self):
        # Stores symbol names mapped to their QuantumState objects.
        self._symbols: Dict[str, QuantumState] = {}
        # For conceptual entanglement: a registry of groups of symbol names
        # that are considered entangled. In a real quantum system, entanglement
        # is a property of the overall quantum register, not individual symbol objects.
        self._entangled_groups: List[List[str]] = []

    def add_symbol(self, name: str, initial_value: Any, initial_amplitude: complex = 1.0 + 0j):
        """
        Adds a new symbol to the table with an initial classical value
        and its corresponding amplitude, creating a new QuantumState.
        If the symbol already exists, its state is updated by adding the new value
        to its superposition.
        """
        if name in self._symbols:
            self._symbols[name].add_state(initial_value, initial_amplitude)
        else:
            self._symbols[name] = QuantumState([(initial_value, initial_amplitude)])

    def add_superposition_symbol(self, name: str, states: List[Tuple[Any, complex]]):
        """
        Adds a symbol that is initially in a superposition of multiple states.
        The provided states will be normalized to form a valid quantum state.
        If the symbol already exists, its current quantum state is overwritten.
        """
        if name in self._symbols:
            print(f"Warning: Symbol '{name}' already exists. Overwriting its quantum state with a new superposition.")
        self._symbols[name] = QuantumState(states)

    def get_symbol_state(self, name: str) -> Optional[QuantumState]:
        """
        Retrieves the QuantumState object associated with a symbol.
        This operation does NOT perform a measurement and thus does not
        collapse the superposition. It returns the current quantum state.
        """
        return self._symbols.get(name)

    def measure_symbol(self, name: str) -> Any:
        """
        'Measures' the specified symbol, collapsing its quantum state
        to a single classical value based on probabilities. This value is returned.
        
        CRITICAL CONCEPT: In a true quantum system, measurement of one part
        of an entangled system would instantaneously collapse the states of
        all other entangled parts. This pseudocode *simulates* that by
        identifying entangled groups and printing a conceptual message.
        Actual state collapse for other entangled symbols would require
        a more sophisticated quantum state simulator.
        """
        if name not in self._symbols:
            raise KeyError(f"Symbol '{name}' not found in the table.")
        
        # Perform the measurement on the symbol's own state
        measured_value = self._symbols[name].measure()

        # --- Conceptual Entanglement Collapse ---
        # If this symbol is part of an entangled group, its measurement
        # might influence or collapse the states of other symbols in that group.
        # This is a highly simplified conceptualization for pseudocode.
        for group in self._entangled_groups:
            if name in group:
                # For all other symbols in this group, their states might
                # now be constrained or collapsed based on 'name's measurement.
                # Example: If symbol 'A' and 'B' are entangled such that if 'A' is 0, 'B' must be 1.
                # If 'A' is measured as 0, then 'B's state would collapse to 1.
                # Implementing this fully requires defining specific entanglement rules
                # and a mechanism to modify other QuantumState objects based on these rules.
                print(f"Conceptual Entanglement Effect: Measurement of '{name}' to '{measured_value}' "
                      f"would instantaneously affect entangled symbols in group: {group}. "
                      f"Their states would collapse consistent with this measurement.")
                # Placeholder for actual entanglement logic:
                # For example, one might iterate through other symbols in the group
                # and update their QuantumState objects to reflect the collapse.
                # This would involve filtering their possible states or adjusting amplitudes.
                pass 

        return measured_value

    def entangle_symbols(self, symbol_names: List[str]):
        """
        Conceptually entangles a group of symbols.
        In a real quantum system, this would involve creating a multi-qubit
        state where the qubits corresponding to these symbols are entangled.
        Here, it registers a group that *should* exhibit entanglement behavior
        upon measurement. If the new group overlaps with existing entangled groups,
        they are merged into a single larger entangled group.
        """
        if not symbol_names or len(symbol_names) < 2:
            raise ValueError("At least two symbols are required for entanglement.")

        for name in symbol_names:
            if name not in self._symbols:
                raise KeyError(f"Cannot entangle: Symbol '{name}' not found in the table.")
        
        new_group_set = set(symbol_names)
        updated_groups = []
        
        # Check for existing groups and merge if there's overlap
        found_overlap = False
        for existing_group in self._entangled_groups:
            if not new_group_set.isdisjoint(existing_group):
                new_group_set.update(existing_group) # Merge the groups
                found_overlap = True
            else:
                updated_groups.append(existing_group) # Keep non-overlapping groups
        
        updated_groups.append(list(new_group_set)) # Add the (potentially merged) new group
        self._entangled_groups = updated_groups
        
        print(f"Conceptual: Symbols {symbol_names} are now considered entangled.")
        print(f"Current entangled groups: {self._entangled_groups}")

    def __len__(self):
        """Returns the number of symbols in the table."""
        return len(self._symbols)

    def __contains__(self, name: str):
        """Checks if a symbol exists in the table."""
        return name in self._symbols

    def __repr__(self):
        """Provides a string representation of the EntangledSymbolTable."""
        symbol_reprs = []
        for name, q_state in self._symbols.items():
            symbol_reprs.append(f"  '{name}': {q_state}")
        
        entangled_groups_repr = ", ".join([str(g) for g in self._entangled_groups])
        
        return (
            "EntangledSymbolTable(\n"
            + "Symbols:\n" + ",\n".join(symbol_reprs) + "\n"
            + f"Entangled Groups: [{entangled_groups_repr}]\n"
            + ")"
        )

# --- Example Usage (for testing/demonstration, not part of the core class) ---
if __name__ == "__main__":
    print("--- Initializing Entangled Symbol Table ---")
    est = EntangledSymbolTable()

    # 1. Add a simple symbol (classical-like, always measures to the same value)
    est.add_symbol("concept_A", "initial_idea")
    print(f"\nSymbol 'concept_A' state: {est.get_symbol_state('concept_A')}")
    print(f"Measuring 'concept_A': {est.measure_symbol('concept_A')}") # Should always be 'initial_idea'

    # 2. Add a symbol in a superposition state
    print("\n--- Adding a symbol in superposition (e.g., a qubit in |+> state) ---")
    est.add_superposition_symbol(
        "quantum_state_B",
        [
            ("state_0", 1/cmath.sqrt(2) + 0j),      # Amplitude for 'state_0'
            ("state_1", 0 + 1/cmath.sqrt(2)*1j)     # Amplitude for 'state_1' (i/sqrt(2))
        ]
    )
    print(f"Symbol 'quantum_state_B' state: {est.get_symbol_state('quantum_state_B')}")

    print("Measuring 'quantum_state_B' multiple times (expect ~50/50 split):")
    results_b = {"state_0": 0, "state_1": 0}
    for _ in range(1000):
        result = est.measure_symbol("quantum_state_B")
        results_b[result] += 1
    print(f"Measurement results for 'quantum_state_B' (1000 trials): {results_b}")
    # Expected: roughly 500 for 'state_0', 500 for 'state_1' (since |1/sqrt(2)|^2 = 0.5)

    # 3. Add another symbol with different superposition probabilities
    est.add_superposition_symbol(
        "quantum_state_C",
        [
            ("up", 0.8 + 0j),   # Amplitude 0.8
            ("down", 0.6 + 0j)  # Amplitude 0.6 (will be normalized)
        ]
    )
    print(f"\nSymbol 'quantum_state_C' state: {est.get_symbol_state('quantum_state_C')}")
    print("Measuring 'quantum_state_C' multiple times (expect ~64/36 split):")
    results_c = {"up": 0, "down": 0}
    for _ in range(1000):
        result = est.measure_symbol("quantum_state_C")
        results_c[result] += 1
    print(f"Measurement results for 'quantum_state_C' (1000 trials): {results_c}")
    # Expected: 'up' ~640, 'down' ~360 (since normalized amplitudes would be ~0.8 and ~0.6,
    # and probabilities are 0.8^2 = 0.64 and 0.6^2 = 0.36)

    # 4. Demonstrate conceptual entanglement
    print("\n--- Demonstrating Conceptual Entanglement ---")
    est.add_superposition_symbol(
        "entangled_X",
        [("left", 1/cmath.sqrt(2)), ("right", 1/cmath.sqrt(2))]
    )
    est.add_superposition_symbol(
        "entangled_Y",
        [("up", 1/cmath.sqrt(2)), ("down", 1/cmath.sqrt(2))]
    )
    est.add_superposition_symbol(
        "entangled_Z",
        [("forward", 1/cmath.sqrt(2)), ("backward", 1/cmath.sqrt(2))]
    )

    # Entangle X and Y
    est.entangle_symbols(["entangled_X", "entangled_Y"])
    # Entangle Y and Z (this should merge the group to X, Y, Z)
    est.entangle_symbols(["entangled_Y", "entangled_Z"])

    print(f"\nState of 'entangled_X' before measurement: {est.get_symbol_state('entangled_X')}")
    print(f"State of 'entangled_Y' before measurement: {est.get_symbol_state('entangled_Y')}")
    print(f"State of 'entangled_Z' before measurement: {est.get_symbol_state('entangled_Z')}")

    print("\nMeasuring 'entangled_X'...")
    measured_x = est.measure_symbol("entangled_X")
    print(f"Measured 'entangled_X': {measured_x}")
    # The conceptual entanglement message from `measure_symbol` should appear here,
    # indicating that 'entangled_Y' and 'entangled_Z' would also be affected.

    # IMPORTANT: In this pseudocode, the QuantumState objects for 'entangled_Y' and 'entangled_Z'
    # themselves are NOT modified by the measurement of 'entangled_X'.
    # Their next measurement will still be probabilistic based on their original superposition.
    # This highlights the "pseudocode" nature; a true quantum simulator would update their states.
    print(f"State of 'entangled_Y' after 'entangled_X' measurement (conceptually affected): {est.get_symbol_state('entangled_Y')}")
    print(f"Measuring 'entangled_Y' after 'entangled_X' was measured: {est.measure_symbol('entangled_Y')}")
    print(f"Measuring 'entangled_Z' after 'entangled_X' was measured: {est.measure_symbol('entangled_Z')}")

    print("\n--- Full Symbol Table State ---")
    print(est)