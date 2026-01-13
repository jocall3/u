import uuid
import time
import random
from typing import Any, Dict, List, Tuple, Optional

class QuantumState:
    """
    Represents a single quantum state in the program's execution history.
    """
    def __init__(self, state_id: uuid.UUID, timestamp: float, variables: Dict[str, Any], call_stack: List[str], entropy_level: float):
        self.state_id = state_id
        self.timestamp = timestamp
        self.variables = variables
        self.call_stack = call_stack
        self.entropy_level = entropy_level

    def __repr__(self):
        return f"QuantumState(id={self.state_id}, time={self.timestamp}, entropy={self.entropy_level})"

class QuantumHistoryRecorder:
    """
    Records and manages the quantum history of program states.
    """

    def __init__(self, max_history_size: int = 1000):
        """
        Initializes the QuantumHistoryRecorder.

        Args:
            max_history_size: The maximum number of states to store in the history.
        """
        self.history: List[QuantumState] = []
        self.max_history_size = max_history_size
        self.current_entropy_level = 0.5  # Initial entropy level

    def record_state(self, variables: Dict[str, Any], call_stack: List[str]) -> uuid.UUID:
        """
        Records a new quantum state.

        Args:
            variables: A dictionary of variable names and their values.
            call_stack: A list of function names representing the call stack.

        Returns:
            The UUID of the newly recorded state.
        """
        state_id = uuid.uuid4()
        timestamp = time.time()
        self.current_entropy_level = self._calculate_entropy(variables) # Update entropy based on variables
        state = QuantumState(state_id, timestamp, variables, call_stack, self.current_entropy_level)
        self.history.append(state)

        # Enforce maximum history size
        if len(self.history) > self.max_history_size:
            self.history.pop(0)  # Remove the oldest state

        return state_id

    def get_state(self, state_id: uuid.UUID) -> Optional[QuantumState]:
        """
        Retrieves a specific quantum state by its ID.

        Args:
            state_id: The UUID of the state to retrieve.

        Returns:
            The QuantumState object if found, otherwise None.
        """
        for state in self.history:
            if state.state_id == state_id:
                return state
        return None

    def get_history(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[QuantumState]:
        """
        Retrieves a range of quantum states based on a time window.

        Args:
            start_time: The start time of the window (inclusive). If None, starts from the beginning.
            end_time: The end time of the window (inclusive). If None, ends at the end.

        Returns:
            A list of QuantumState objects within the specified time window.
        """
        filtered_history: List[QuantumState] = []
        for state in self.history:
            if (start_time is None or state.timestamp >= start_time) and \
               (end_time is None or state.timestamp <= end_time):
                filtered_history.append(state)
        return filtered_history

    def clear_history(self) -> None:
        """
        Clears the entire quantum history.
        """
        self.history = []
        self.current_entropy_level = 0.5

    def _calculate_entropy(self, variables: Dict[str, Any]) -> float:
        """
        Calculates a simple entropy level based on the variability of the variables.
        This is a placeholder and can be replaced with a more sophisticated entropy calculation.

        Args:
            variables: A dictionary of variable names and their values.

        Returns:
            A float representing the entropy level (between 0 and 1).
        """
        num_variables = len(variables)
        if num_variables == 0:
            return 0.5  # Default entropy if no variables

        unique_values = set()
        for value in variables.values():
            unique_values.add(str(value))  # Convert to string for hashing

        num_unique_values = len(unique_values)
        entropy = num_unique_values / num_variables if num_variables > 0 else 0.0
        return min(1.0, max(0.0, entropy)) # Ensure entropy is between 0 and 1

    def get_latest_state(self) -> Optional[QuantumState]:
        """
        Returns the most recently recorded state.

        Returns:
            The most recent QuantumState object, or None if the history is empty.
        """
        if self.history:
            return self.history[-1]
        else:
            return None

    def get_state_by_index(self, index: int) -> Optional[QuantumState]:
        """
        Retrieves a state by its index in the history.

        Args:
            index: The index of the state to retrieve.

        Returns:
            The QuantumState object at the specified index, or None if the index is out of bounds.
        """
        if 0 <= index < len(self.history):
            return self.history[index]
        else:
            return None

    def get_states_with_entropy_above(self, threshold: float) -> List[QuantumState]:
        """
        Retrieves all states with an entropy level above a given threshold.

        Args:
            threshold: The minimum entropy level.

        Returns:
            A list of QuantumState objects with entropy above the threshold.
        """
        return [state for state in self.history if state.entropy_level > threshold]

    def get_states_containing_variable(self, variable_name: str) -> List[QuantumState]:
        """
        Retrieves all states that contain a specific variable.

        Args:
            variable_name: The name of the variable to search for.

        Returns:
            A list of QuantumState objects that contain the variable.
        """
        return [state for state in self.history if variable_name in state.variables]

    def get_average_entropy(self) -> float:
        """
        Calculates the average entropy level across all recorded states.

        Returns:
            The average entropy level, or 0.0 if the history is empty.
        """
        if not self.history:
            return 0.0

        total_entropy = sum(state.entropy_level for state in self.history)
        return total_entropy / len(self.history)