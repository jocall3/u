import random
import time
from typing import Dict, Any, List, Optional, Tuple, Callable

# Define a type for a quantum state: a mapping of possible values to their probabilities.
# Probabilities should sum to 1.0 (or very close due to floating point inaccuracies).
QuantumState = Dict[Any, float]

class QuantumSymbol:
    """
    Represents a quantum-inspired symbol that can exist in a superposition of states
    until a measurement collapses it to a definite value.
    """
    def __init__(self, symbol_id: str, initial_state: QuantumState):
        if not isinstance(symbol_id, str) or not symbol_id:
            raise ValueError("Symbol ID must be a non-empty string.")
        if not isinstance(initial_state, dict) or not initial_state:
            raise ValueError("Initial state must be a non-empty dictionary.")
        if not all(isinstance(prob, (float, int)) and 0 <= prob <= 1 for prob in initial_state.values()):
            raise ValueError("Probabilities in initial state must be between 0 and 1.")
        if not abs(sum(initial_state.values()) - 1.0) < 1e-9:  # Allow for floating point inaccuracies
            raise ValueError("Probabilities in initial state must sum to 1.0.")

        self.id: str = symbol_id
        self._superposition: QuantumState = initial_state
        self._collapsed_value: Optional[Any] = None
        self._is_measured: bool = False
        self.entangled_with: List[str] = []  # Other symbol IDs this one is conceptually entangled with
        self.measurement_history: List[Tuple[float, Any]] = []  # (timestamp, measured_value)

    def is_superposed(self) -> bool:
        """Checks if the symbol is currently in a superposition of states."""
        return not self._is_measured

    def get_current_state(self) -> QuantumState:
        """
        Returns the current state of the symbol.
        If measured, returns a state with 1.0 probability for the collapsed value.
        If in superposition, returns the current superposition probabilities.
        """
        if self._is_measured and self._collapsed_value is not None:
            return {self._collapsed_value: 1.0}
        return self._superposition

    def get_collapsed_value(self) -> Optional[Any]:
        """Returns the definite value if the symbol has been measured, otherwise None."""
        return self._collapsed_value

    def collapse(self, observed_value: Any):
        """
        Forces the symbol to collapse to a specific observed value.
        This method is typically called internally by the measurement engine.
        """
        if observed_value not in self._superposition:
            raise ValueError(f"Observed value '{observed_value}' is not a possible state for symbol '{self.id}'.")
        self._collapsed_value = observed_value
        self._is_measured = True
        # Once collapsed, its superposition effectively becomes 100% for the observed value
        self._superposition = {observed_value: 1.0}

    def update_superposition(self, new_superposition: QuantumState):
        """
        Updates the superposition of the symbol. This is used for entanglement effects.
        Can only update if the symbol is not yet measured.
        """
        if self._is_measured:
            # A measured symbol cannot have its superposition altered.
            # Its state is definite.
            return

        if not isinstance(new_superposition, dict) or not new_superposition:
            raise ValueError("New superposition must be a non-empty dictionary.")
        if not all(isinstance(prob, (float, int)) and 0 <= prob <= 1 for prob in new_superposition.values()):
            raise ValueError("Probabilities in new superposition must be between 0 and 1.")
        if not abs(sum(new_superposition.values()) - 1.0) < 1e-9:
            raise ValueError("Probabilities in new superposition must sum to 1.0.")

        self._superposition = new_superposition

    def __repr__(self) -> str:
        if self._is_measured:
            return f"QuantumSymbol(id='{self.id}', collapsed_value={self._collapsed_value})"
        return f"QuantumSymbol(id='{self.id}', superposition={self._superposition})"


class SymbolMeasurementEngine:
    """
    The core engine that performs quantum-inspired measurements during symbol lookup
    and manages the resulting environment alterations, including entanglement effects.

    In this conceptual model, "quantum becomes the law" implies that symbol states
    are probabilistic until observed, and observations can have non-local effects.
    """

    def __init__(self):
        self._symbols: Dict[str, QuantumSymbol] = {}
        self._measurement_log: List[Dict[str, Any]] = []
        # Entanglement rules are functions that take (measured_symbol_id, measured_value, all_symbols_dict)
        # and modify the superposition of other symbols.
        self._entanglement_rules: Dict[str, Callable[[str, Any, Dict[str, QuantumSymbol]], None]] = {}

    def register_symbol(self, symbol_id: str, initial_state: QuantumState,
                        entangled_with: Optional[List[str]] = None) -> QuantumSymbol:
        """
        Registers a new quantum symbol with its initial superposition of states.

        Args:
            symbol_id: A unique identifier for the symbol.
            initial_state: A dictionary mapping possible values to their probabilities.
                           Probabilities must sum to 1.0.
            entangled_with: An optional list of symbol IDs that are "entangled" with this symbol.
                            Measuring this symbol might affect their states.

        Returns:
            The newly created QuantumSymbol object.

        Raises:
            ValueError: If the symbol_id is already registered or initial_state is invalid.
        """
        if symbol_id in self._symbols:
            raise ValueError(f"Symbol '{symbol_id}' already registered.")
        
        symbol = QuantumSymbol(symbol_id, initial_state)
        if entangled_with:
            # Validate that entangled_with symbols exist or will exist
            for eid in entangled_with:
                if eid == symbol_id:
                    raise ValueError(f"Symbol '{symbol_id}' cannot be entangled with itself.")
            symbol.entangled_with = entangled_with
        self._symbols[symbol_id] = symbol
        return symbol

    def define_entanglement_rule(self, measured_symbol_id: str,
                                 rule_function: Callable[[str, Any, Dict[str, QuantumSymbol]], None]):
        """
        Defines a custom rule for how other symbols' superpositions are altered
        when a specific symbol is measured. This allows for complex, domain-specific
        "quantum laws" to govern interactions.

        Args:
            measured_symbol_id: The ID of the symbol whose measurement triggers this rule.
            rule_function: A callable that takes (measured_symbol_id, measured_value, all_symbols_dict)
                           and modifies the superposition of other symbols in the `all_symbols_dict`.
                           The function should directly call `update_superposition` on affected `QuantumSymbol` objects.

        Raises:
            ValueError: If the measured_symbol_id is not registered.
        """
        if measured_symbol_id not in self._symbols:
            raise ValueError(f"Symbol '{measured_symbol_id}' is not registered.")
        self._entanglement_rules[measured_symbol_id] = rule_function

    def measure_symbol(self, symbol_id: str) -> Any:
        """
        Performs a "quantum measurement" on a specified symbol.
        This collapses its superposition to a single definite value based on probabilities.
        The act of measurement also triggers potential entanglement effects on other symbols.

        Args:
            symbol_id: The ID of the symbol to measure.

        Returns:
            The observed (collapsed) value of the symbol.

        Raises:
            ValueError: If the symbol is not registered.
        """
        if symbol_id not in self._symbols:
            raise ValueError(f"Symbol '{symbol_id}' is not registered.")

        symbol = self._symbols[symbol_id]

        if symbol.is_superposed():
            # Perform probabilistic collapse based on current superposition
            possible_values = list(symbol._superposition.keys())
            probabilities = list(symbol._superposition.values())

            # Use random.choices to select a value based on probabilities
            collapsed_value = random.choices(possible_values, weights=probabilities, k=1)[0]
            symbol.collapse(collapsed_value)  # Update the symbol's internal state
        else:
            # If already measured, just return its collapsed value
            collapsed_value = symbol.get_collapsed_value()

        # Record the measurement event
        self._record_measurement(symbol_id, collapsed_value)

        # Propagate entanglement effects to other symbols
        self._propagate_entanglement(symbol_id, collapsed_value)

        return collapsed_value

    def get_symbol_state(self, symbol_id: str) -> QuantumState:
        """
        Retrieves the current state of a symbol.
        If measured, returns a state with 1.0 probability for the collapsed value.
        If in superposition, returns the current superposition probabilities.

        Args:
            symbol_id: The ID of the symbol.

        Returns:
            A QuantumState dictionary.

        Raises:
            ValueError: If the symbol is not registered.
        """
        if symbol_id not in self._symbols:
            raise ValueError(f"Symbol '{symbol_id}' is not registered.")
        return self._symbols[symbol_id].get_current_state()

    def get_collapsed_value(self, symbol_id: str) -> Optional[Any]:
        """
        Retrieves the collapsed value of a symbol, if it has been measured.

        Args:
            symbol_id: The ID of the symbol.

        Returns:
            The collapsed value, or None if the symbol is still in superposition.

        Raises:
            ValueError: If the symbol is not registered.
        """
        if symbol_id not in self._symbols:
            raise ValueError(f"Symbol '{symbol_id}' is not registered.")
        return self._symbols[symbol_id].get_collapsed_value()

    def get_measurement_log(self) -> List[Dict[str, Any]]:
        """Returns the historical log of all measurements performed by the engine."""
        return self._measurement_log

    def _record_measurement(self, symbol_id: str, value: Any):
        """Internal method to log a measurement event and update symbol history."""
        timestamp = time.time()
        log_entry = {
            "timestamp": timestamp,
            "symbol_id": symbol_id,
            "measured_value": value
        }
        self._measurement_log.append(log_entry)
        # The symbol's own history is updated during its collapse method,
        # but we can also add it here for redundancy or if collapse was external.
        # For consistency, it's better to ensure `collapse` updates it.
        # self._symbols[symbol_id].measurement_history.append((timestamp, value))

    def