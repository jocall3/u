class QuantumState:
    """
    Represents the state of a quantum system at a given point in time.
    This is a placeholder; a real implementation would need to handle
    quantum data structures (e.g., wavefunctions, density matrices).
    """
    def __init__(self, data=None, metadata=None):
        self.data = data  # Placeholder for quantum data
        self.metadata = metadata or {}  # Metadata about the state (e.g., time)

    def __repr__(self):
        return f"QuantumState(data={self.data}, metadata={self.metadata})"


class QuantumOperation:
    """
    Represents a quantum operation applied to the system.
    This is a placeholder; a real implementation would need to handle
    quantum gates, measurements, etc.
    """
    def __init__(self, name, parameters=None):
        self.name = name
        self.parameters = parameters or {}

    def __repr__(self):
        return f"QuantumOperation(name={self.name}, parameters={self.parameters})"


class QuantumDebuggerCore:
    """
    Core class for the Quantum Debugger, providing forward and backward stepping.
    """

    def __init__(self, quantum_program):
        """
        Initializes the debugger with a quantum program.

        Args:
            quantum_program: A list of QuantumOperation objects representing the program.
        """
        self.quantum_program = quantum_program
        self.history = []  # List of QuantumState objects representing the system's history
        self.current_state = QuantumState(data="Initial State", metadata={"time": 0})
        self.current_step = 0
        self.history.append(self.current_state)

    def forward_step(self):
        """
        Executes the next quantum operation in the program and updates the state.
        """
        if self.current_step < len(self.quantum_program):
            operation = self.quantum_program[self.current_step]
            print(f"Executing: {operation}")  # Simulate execution

            # Placeholder for applying the operation to the current state
            # In a real implementation, this would involve quantum simulation.
            new_data = f"State after {operation.name} at step {self.current_step + 1}"
            new_metadata = {"time": self.current_step + 1}
            self.current_state = QuantumState(data=new_data, metadata=new_metadata)
            self.history.append(self.current_state)

            self.current_step += 1
            return self.current_state
        else:
            print("End of program.")
            return None

    def backward_step(self):
        """
        Reverts to the previous quantum state in the history.
        """
        if self.current_step > 0:
            self.current_step -= 1
            self.history.pop()  # Remove the current state from history
            self.current_state = self.history[-1]
            print(f"Reverted to step {self.current_step}, State: {self.current_state}")
            return self.current_state
        else:
            print("Already at the beginning of the program.")
            return None

    def get_current_state(self):
        """
        Returns the current quantum state.
        """
        return self.current_state

    def get_current_step(self):
        """
        Returns the current step number.
        """
        return self.current_step

    def reset(self):
        """
        Resets the debugger to the initial state.
        """
        self.history = [self.history[0]]  # Keep only the initial state
        self.current_state = self.history[0]
        self.current_step = 0
        print("Debugger reset to initial state.")

if __name__ == '__main__':
    # Example Usage
    program = [
        QuantumOperation("Hadamard", {"qubit": 0}),
        QuantumOperation("CNOT", {"control": 0, "target": 1}),
        QuantumOperation("Measurement", {"qubit": 0})
    ]

    debugger = QuantumDebuggerCore(program)

    print("Initial State:", debugger.get_current_state())

    debugger.forward_step()
    print("State after step 1:", debugger.get_current_state())

    debugger.forward_step()
    print("State after step 2:", debugger.get_current_state())

    debugger.backward_step()
    print("State after backward step:", debugger.get_current_state())

    debugger.reset()
    print("State after reset:", debugger.get_current_state())