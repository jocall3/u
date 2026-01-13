import random
import uuid

class QuantumStateManager:
    """
    Manages the allocation, deallocation, and manipulation of quantum states (qubits).
    This class provides a high-level interface for quantum operations, abstracting
    away the underlying hardware or simulation details.
    """

    def __init__(self, num_qubits=0, backend="simulator"):
        """
        Initializes the QuantumStateManager.

        Args:
            num_qubits (int): The initial number of qubits to allocate. Defaults to 0.
            backend (str): The quantum backend to use (e.g., "simulator", "hardware").
                           Defaults to "simulator".
        """
        self.qubits = {}  # Dictionary to store qubit states, indexed by UUID.
        self.num_qubits = 0 # Track the total number of qubits allocated
        self.backend = backend
        self.allocate_qubits(num_qubits)

    def allocate_qubit(self):
        """
        Allocates a single qubit and returns its unique ID.

        Returns:
            str: The UUID of the allocated qubit.
        """
        qubit_id = str(uuid.uuid4())
        # Initialize to a random state (superposition)
        alpha = random.uniform(0, 1)
        beta = (1 - alpha**2)**0.5
        phase = random.uniform(0, 2 * 3.14159)  # Random phase
        self.qubits[qubit_id] = {"alpha": alpha, "beta": beta * complex(random.choice([-1,1]), random.choice([-1,1])), "phase": phase}
        self.num_qubits += 1
        return qubit_id

    def allocate_qubits(self, num_qubits):
        """
        Allocates a specified number of qubits.

        Args:
            num_qubits (int): The number of qubits to allocate.

        Returns:
            list[str]: A list of UUIDs for the allocated qubits.
        """
        qubit_ids = []
        for _ in range(num_qubits):
            qubit_ids.append(self.allocate_qubit())
        return qubit_ids

    def deallocate_qubit(self, qubit_id):
        """
        Deallocates a qubit, releasing its resources.

        Args:
            qubit_id (str): The UUID of the qubit to deallocate.

        Raises:
            ValueError: If the qubit ID is invalid or the qubit is already deallocated.
        """
        if qubit_id not in self.qubits:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

        del self.qubits[qubit_id]
        self.num_qubits -= 1

    def get_qubit_state(self, qubit_id):
        """
        Retrieves the current state of a qubit.

        Args:
            qubit_id (str): The UUID of the qubit.

        Returns:
            dict: A dictionary representing the qubit's state (e.g., {"alpha": ..., "beta": ...}).

        Raises:
            ValueError: If the qubit ID is invalid.
        """
        if qubit_id not in self.qubits:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")
        return self.qubits[qubit_id]

    def set_qubit_state(self, qubit_id, alpha, beta, phase=0.0):
        """
        Sets the state of a qubit.

        Args:
            qubit_id (str): The UUID of the qubit.
            alpha (float): The amplitude of the |0> state.
            beta (complex): The amplitude of the |1> state.
            phase (float): The phase of the qubit (optional).

        Raises:
            ValueError: If the qubit ID is invalid or the provided amplitudes are invalid.
        """
        if qubit_id not in self.qubits:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

        if not abs(alpha**2 + abs(beta)**2 - 1) < 1e-6:  # Check for normalization
            raise ValueError("Invalid amplitudes: alpha^2 + |beta|^2 must equal 1.")

        self.qubits[qubit_id] = {"alpha": alpha, "beta": beta, "phase": phase}

    def apply_gate(self, qubit_id, gate_name, *args):
        """
        Applies a quantum gate to a qubit.

        Args:
            qubit_id (str): The UUID of the qubit.
            gate_name (str): The name of the gate to apply (e.g., "H", "X", "CNOT").
            *args: Additional arguments for the gate (e.g., target qubit for CNOT).

        Raises:
            ValueError: If the qubit ID is invalid or the gate is not supported.
        """
        if qubit_id not in self.qubits:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

        if gate_name == "H":  # Hadamard gate
            alpha = self.qubits[qubit_id]["alpha"]
            beta = self.qubits[qubit_id]["beta"]
            self.qubits[qubit_id]["alpha"] = (alpha + beta) / 2**0.5
            self.qubits[qubit_id]["beta"] = (alpha - beta) / 2**0.5
        elif gate_name == "X":  # Pauli-X gate
            alpha = self.qubits[qubit_id]["alpha"]
            beta = self.qubits[qubit_id]["beta"]
            self.qubits[qubit_id]["alpha"] = beta
            self.qubits[qubit_id]["beta"] = alpha
        elif gate_name == "Z": # Pauli-Z gate
            beta = self.qubits[qubit_id]["beta"]
            self.qubits[qubit_id]["beta"] = -beta
        elif gate_name == "CNOT": # CNOT gate
            control_qubit_id = qubit_id
            target_qubit_id = args[0]

            if target_qubit_id not in self.qubits:
                raise ValueError(f"Invalid target qubit ID: {target_qubit_id}")

            control_state = self.get_qubit_state(control_qubit_id)
            target_state = self.get_qubit_state(target_qubit_id)

            if control_state["alpha"] == 1:
                alpha = target_state["alpha"]
                beta = target_state["beta"]
                self.set_qubit_state(target_qubit_id, beta, alpha)
        else:
            raise ValueError(f"Unsupported gate: {gate_name}")

    def measure_qubit(self, qubit_id):
        """
        Measures a qubit and collapses its state.

        Args:
            qubit_id (str): The UUID of the qubit.

        Returns:
            int: The measurement result (0 or 1).

        Raises:
            ValueError: If the qubit ID is invalid.
        """
        if qubit_id not in self.qubits:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

        alpha = self.qubits[qubit_id]["alpha"]
        probability_0 = abs(alpha)**2
        if random.random() < probability_0:
            self.qubits[qubit_id]["alpha"] = 1.0
            self.qubits[qubit_id]["beta"] = 0.0
            return 0
        else:
            self.qubits[qubit_id]["alpha"] = 0.0
            self.qubits[qubit_id]["beta"] = 1.0
            return 1

    def get_num_qubits(self):
        """
        Returns the number of allocated qubits.
        """
        return self.num_qubits