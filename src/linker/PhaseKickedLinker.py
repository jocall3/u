# src/linker/PhaseKickedLinker.py

import numpy as np
import cmath
import random
from typing import Dict, List, Tuple, Any

# --- Quantum Primitives (Simulated) ---

class SymbolQubit:
    """
    Represents a single symbol's quantum state as a qubit.
    A qubit is defined by two complex amplitudes, alpha and beta,
    for the basis states |0> and |1>, respectively.
    The state is represented as: |ψ> = α|0> + β|1>
    The normalization condition |α|^2 + |β|^2 = 1 must hold for a coherent state.
    """
    def __init__(self, alpha: complex, beta: complex):
        """
        Initializes the qubit and normalizes its state vector.
        """
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        if np.isclose(norm, 0):
            raise ValueError("Initial amplitudes cannot both be zero.")
        self.alpha = alpha / norm
        self.beta = beta / norm
        self.is_collapsed = False
        self.collapsed_value = None

    @classmethod
    def hadamard_state(cls) -> 'SymbolQubit':
        """Creates a qubit in a perfect superposition state (|0> + |1>)/sqrt(2)."""
        return cls(1/np.sqrt(2), 1/np.sqrt(2))

    @classmethod
    def from_classical(cls, bit: int) -> 'SymbolQubit':
        """Creates a qubit from a classical bit (0 or 1)."""
        if bit == 0:
            qubit = cls(1, 0)
        elif bit == 1:
            qubit = cls(0, 1)
        else:
            raise ValueError("Classical bit must be 0 or 1.")
        qubit.is_collapsed = True
        qubit.collapsed_value = bit
        return qubit

    @property
    def state_vector(self) -> np.ndarray:
        """Returns the state vector [alpha, beta] as a NumPy array."""
        return np.array([self.alpha, self.beta])

    def apply_gate(self, gate_matrix: np.ndarray):
        """
        Applies a 2x2 matrix (representing a quantum gate or noise) to the qubit.
        The state is updated by matrix multiplication: |ψ'> = U|ψ>.
        """
        if self.is_collapsed:
            # Cannot evolve a state that has already been measured and collapsed.
            return
        if gate_matrix.shape != (2, 2):
            raise ValueError("Gate matrix must be 2x2.")

        new_state = np.dot(gate_matrix, self.state_vector)
        self.alpha, self.beta = new_state[0], new_state[1]

    def measure(self) -> int:
        """
        Collapses the qubit's superposition to a classical state (0 or 1).
        The outcome is probabilistic, determined by the squared magnitudes of the
        amplitudes (Born rule). The state is permanently altered post-measurement.
        """
        if self.is_collapsed:
            return self.collapsed_value

        prob_0 = abs(self.alpha)**2
        
        result = 0 if random.random() < prob_0 else 1
        
        # Collapse the state to the measured outcome
        if result == 0:
            self.alpha, self.beta = 1.0 + 0j, 0.0 + 0j
        else:
            self.alpha, self.beta = 0.0 + 0j, 1.0 + 0j
            
        self.is_collapsed = True
        self.collapsed_value = result
        return result

    def __repr__(self) -> str:
        if self.is_collapsed:
            return f"|{self.collapsed_value}> (Collapsed)"
        return f"({self.alpha:.2f})|0> + ({self.beta:.2f})|1>"

# --- Contextual Operators (Simulated Quantum Gates) ---

def phase_kick_operator(angle: float) -> np.ndarray:
    """
    Creates a phase-shift gate (a rotation around the Z-axis on the Bloch sphere).
    This represents the contextual 'kick' applied to a symbol.
    Matrix form: [[1, 0], [0, e^(i*angle)]]
    """
    return np.array([
        [1, 0],
        [0, cmath.exp(1j * angle)]
    ])

def ambiguity_operator(noise_level: float) -> np.ndarray:
    """
    Creates a non-unitary operator representing environmental noise or ambiguity.
    This operator intentionally violates the conservation of probability
    (|α|^2 + |β|^2 = 1) to simulate decoherence.
    """
    # This is a conceptual, non-physical operator for simulation purposes.
    decay = 1.0 - noise_level
    cross_talk = random.uniform(0, noise_level)
    return np.array([
        [decay, cross_talk],
        [cross_talk, decay]
    ])

# --- The Quantum-Inspired Linker ---

class PhaseKickedLinker:
    """
    A conceptual model of a linker based on quantum principles.
    It resolves symbols (represented as qubits) by iteratively applying
    contextual 'phase kicks' and monitoring for decoherence, which
    manifests as a linker error.
    """
    def __init__(self, coherence_threshold: float = 0.99, max_iterations: int = 10):
        """
        Initializes the linker's quantum environment.
        
        Args:
            coherence_threshold: The minimum squared magnitude for a state vector
                                 to be considered coherent. Below this, the symbol
                                 is marked as decohered.
            max_iterations: The maximum number of passes the linker will make
                            over the symbol table.
        """
        self.symbol_table: Dict[str, SymbolQubit] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.coherence_threshold = coherence_threshold
        self.max_iterations = max_iterations
        self.resolved_symbols: Dict[str, int] = {}
        self.decohered_symbols: List[str] = []

    def register_symbol(self, name: str, dependencies: List[str] = None):
        """
        Registers a new, unresolved symbol in the linker's table.
        By default, it is initialized in a Hadamard state (perfect superposition),
        representing maximum uncertainty about its final resolution.
        """
        if name not in self.symbol_table:
            print(f"Registering '{name}' in superposition.")
            self.symbol_table[name] = SymbolQubit.hadamard_state()
            self.dependency_graph[name] = dependencies or []

    def _calculate_contextual_influence(self, symbol_name: str) -> float:
        """
        Calculates the total contextual influence on a symbol from its dependencies.
        In this simulation, influence is modeled as a phase angle.
        - A resolved dependency contributes a strong, definite phase.
        - An unresolved dependency contributes a weaker, probabilistic phase.
        """
        total_phase_influence = 0.0
        
        for dep_name in self.dependency_graph.get(symbol_name, []):
            if dep_name in self.resolved_symbols:
                # Strong influence from a resolved (classical) symbol
                # Hash the name to get a consistent but pseudo-random angle
                influence = (hash(dep_name) % 360) / 180.0 * np.pi
                total_phase_influence += influence * self.resolved_symbols[dep_name]
            elif dep_name in self.symbol_table:
                # Weaker, probabilistic influence from an unresolved (quantum) symbol
                dep_qubit = self.symbol_table[dep_name]
                prob_1 = abs(dep_qubit.beta)**2
                influence = (hash(dep_name) % 90) / 180.0 * np.pi # Smaller angle for uncertainty
                total_phase_influence += influence * prob_1
        
        return total_phase_influence

    def _detect_decoherence(self, symbol_name: str) -> bool:
        """
        Checks if a symbol's quantum state has lost coherence.
        Coherence is lost if the norm of the state vector (sum of squared
        amplitudes) deviates significantly from 1.
        """
        qubit = self.symbol_table[symbol_name]
        norm_sq = abs(qubit.alpha)**2 + abs(qubit.beta)**2
        if not np.isclose(norm_sq, 1.0, atol=1-self.coherence_threshold):
            print(f"WARNING: Decoherence detected for '{symbol_name}'! Norm^2 = {norm_sq:.4f}")
            return True
        return False

    def link(self, entry_points: List[str]):
        """
        Performs the iterative linking process.
        
        1. Iteratively apply phase kicks based on context from dependencies.
        2. Introduce environmental noise to simulate real-world ambiguity.
        3. Attempt to measure (resolve) symbols whose states have converged
           towards a classical value.
        4. Detect and report any symbols that have decohered.
        """
        print("--- Starting Quantum Linking Process ---")
        
        for i in range(self.max_iterations):
            print(f"\n--- Linking Iteration {i+1}/{self.max_iterations} ---")
            
            unresolved_symbols = [
                name for name in self.symbol_table 
                if name not in self.resolved_symbols and name not in self.decohered_symbols
            ]
            
            if not unresolved_symbols:
                print("All symbols resolved. Linking successful.")
                break

            for name in unresolved_symbols:
                qubit = self.symbol_table[name]

                # Step 1: Apply Phase Kick based on context
                phase_angle = self._calculate_contextual_influence(name)
                kick_gate = phase_kick_operator(phase_angle)
                qubit.apply_gate(kick_gate)
                
                # Step 2: Introduce Environmental Noise/Ambiguity
                # Noise increases slightly with each iteration, simulating entropy
                noise = random.uniform(0, 0.005) * (i + 1)
                noise_gate = ambiguity_operator(noise)
                qubit.apply_gate(noise_gate)

                # Step 3: Check for Decoherence
                if self._detect_decoherence(name):
                    self.decohered_symbols.append(name)
                    continue

                # Step 4: Attempt to Measure (Resolve)
                # A qubit is "certain" if its probability is close to 0 or 1.
                prob_0 = abs(qubit.alpha)**2
                if prob_0 > 0.99 or prob_0 < 0.01:
                    print(f"Resolving '{name}' with high certainty (P(|0>)={prob_0:.3f}).")
                    resolved_value = qubit.measure()
                    self.resolved_symbols[name] = resolved_value
                    print(f"'{name}' -> {resolved_value}")

        print("\n--- Linking Process Finished ---")
        self.report_status()

    def report_status(self):
        """Prints the final state of all symbols after the linking process."""
        print("\n--- Final Linker Status Report ---")
        print(f"Resolved Symbols: {len(self.resolved_symbols)}")
        for name, val in sorted(self.resolved_symbols.items()):
            print(f"  - {name}: {val}")
            
        unresolved = [
            name for name in self.symbol_table 
            if name not in self.resolved_symbols and name not in self.decohered_symbols
        ]
        print(f"\nUnresolved Symbols (Ambiguous): {len(unresolved)}")
        for name in sorted(unresolved):
            print(f"  - {name}: {self.symbol_table[name]}")
            
        print(f"\nDecohered Symbols (Linker Errors): {len(self.decohered_symbols)}")
        for name in sorted(self.decohered_symbols):
            print(f"  - {name}")
        print("--- End of Report ---")


if __name__ == '__main__':
    # --- DEMONSTRATION OF THE PSEUDOCODE ---
    # This section illustrates the linker's conceptual logic.
    
    # 1. Initialize the linker
    linker = PhaseKickedLinker(coherence_threshold=0.90, max_iterations=15)
    
    # 2. Define a dependency graph for a hypothetical program
    # 'main' depends on 'calculate_gravity' and 'render_output'.
    # 'calculate_gravity' depends on 'constants.G'.
    # 'render_output' depends on 'utils.format'.
    # An ambiguous symbol 'config.mode' is used by multiple components,
    # which may create conflicting contextual pressures.
    dependencies = {
        'main': ['calculate_gravity', 'render_output'],
        'calculate_gravity': ['constants.G', 'config.mode'],
        'render_output': ['utils.format', 'config.mode'],
        'feature_a': ['config.mode'],
        'feature_b': ['config.mode'],
        'constants.G': [],
        'utils.format': [],
        'config.mode': []
    }
    
    for symbol, deps in dependencies.items():
        linker.register_symbol(symbol, deps)

    # 3. Pre-resolve some symbols to simulate linking against a static library
    # where some symbols are already defined with classical values.
    print("\nPre-resolving 'constants.G' and 'utils.format' as classical values.")
    linker.symbol_table['constants.G'] = SymbolQubit.from_classical(1)
    linker.resolved_symbols['constants.G'] = 1
    linker.symbol_table['utils.format'] = SymbolQubit.from_classical(0)
    linker.resolved_symbols['utils.format'] = 0
    
    # 4. Run the linking process starting from the program's entry points.
    linker.link(entry_points=['main', 'feature_a', 'feature_b'])