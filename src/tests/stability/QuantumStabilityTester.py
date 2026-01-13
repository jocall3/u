import numpy as np
import random

class QuantumStabilityTester:
    """
    Pseudocode for the Quantum Stability Tester.
    Injects artificial decoherence and verifies correctness of quantum computations.
    """

    def __init__(self, qubit_count: int, error_rate: float = 0.01):
        """
        Initializes the QuantumStabilityTester.

        Args:
            qubit_count: The number of qubits to simulate.
            error_rate: The probability of a decoherence event per gate operation.
        """
        self.qubit_count = qubit_count
        self.error_rate = error_rate
        self.quantum_state = np.array([1.0 + 0.0j] + [0.0 + 0.0j] * (2**qubit_count - 1))  # Initial state |000...0>
        self.gate_operations = [] # List to store applied gate operations
        self.rng = np.random.default_rng()


    def apply_hadamard(self, qubit_index: int):
        """
        Applies a Hadamard gate to the specified qubit.
        """
        if not (0 <= qubit_index < self.qubit_count):
            raise ValueError("Invalid qubit index.")

        gate_matrix = self._hadamard_gate(qubit_index)
        self.quantum_state = gate_matrix @ self.quantum_state
        self.gate_operations.append(("H", qubit_index))
        self._introduce_decoherence()


    def apply_cnot(self, control_qubit: int, target_qubit: int):
        """
        Applies a CNOT gate.
        """
        if not (0 <= control_qubit < self.qubit_count and 0 <= target_qubit < self.qubit_count):
            raise ValueError("Invalid qubit indices.")
        if control_qubit == target_qubit:
            return # No-op

        gate_matrix = self._cnot_gate(control_qubit, target_qubit)
        self.quantum_state = gate_matrix @ self.quantum_state
        self.gate_operations.append(("CNOT", control_qubit, target_qubit))
        self._introduce_decoherence()


    def apply_pauli_x(self, qubit_index: int):
        """
        Applies a Pauli-X gate (bit-flip) to the specified qubit.
        """
        if not (0 <= qubit_index < self.qubit_count):
            raise ValueError("Invalid qubit index.")

        gate_matrix = self._pauli_x_gate(qubit_index)
        self.quantum_state = gate_matrix @ self.quantum_state
        self.gate_operations.append(("X", qubit_index))
        self._introduce_decoherence()


    def apply_pauli_z(self, qubit_index: int):
        """
        Applies a Pauli-Z gate (phase-flip) to the specified qubit.
        """
        if not (0 <= qubit_index < self.qubit_count):
            raise ValueError("Invalid qubit index.")

        gate_matrix = self._pauli_z_gate(qubit_index)
        self.quantum_state = gate_matrix @ self.quantum_state
        self.gate_operations.append(("Z", qubit_index))
        self._introduce_decoherence()


    def _hadamard_gate(self, qubit_index: int) -> np.ndarray:
        """
        Generates the matrix for a Hadamard gate on a specific qubit.
        """
        hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        identity = np.eye(2)
        gate = identity

        for i in range(self.qubit_count):
            if i == qubit_index:
                gate = np.kron(gate, hadamard)
            else:
                gate = np.kron(gate, identity)
        return gate


    def _cnot_gate(self, control_qubit: int, target_qubit: int) -> np.ndarray:
        """
        Generates the matrix for a CNOT gate.
        """
        identity = np.eye(2)
        pauli_x = np.array([[0, 1], [1, 0]])
        control_matrix = np.array([[1, 0], [0, 0]])
        target_matrix = np.array([[0, 0], [0, 1]])
        gate = identity

        for i in range(self.qubit_count):
            if i == control_qubit:
                gate = np.kron(gate, control_matrix)
            elif i == target_qubit:
                gate = np.kron(gate, pauli_x)
            else:
                gate = np.kron(gate, identity)

        gate += np.kron(np.array([[0, 0], [0, 1]]), np.eye(2**self.qubit_count - 1))
        return gate


    def _pauli_x_gate(self, qubit_index: int) -> np.ndarray:
        """
        Generates the matrix for a Pauli-X gate.
        """
        pauli_x = np.array([[0, 1], [1, 0]])
        identity = np.eye(2)
        gate = identity

        for i in range(self.qubit_count):
            if i == qubit_index:
                gate = np.kron(gate, pauli_x)
            else:
                gate = np.kron(gate, identity)
        return gate


    def _pauli_z_gate(self, qubit_index: int) -> np.ndarray:
        """
        Generates the matrix for a Pauli-Z gate.
        """
        pauli_z = np.array([[1, 0], [0, -1]])
        identity = np.eye(2)
        gate = identity

        for i in range(self.qubit_count):
            if i == qubit_index:
                gate = np.kron(gate, pauli_z)
            else:
                gate = np.kron(gate, identity)
        return gate


    def _introduce_decoherence(self):
        """
        Simulates decoherence by applying a random unitary transformation.
        """
        if self.rng.random() < self.error_rate:
            # Simulate decoherence with a random unitary matrix
            unitary_matrix = self._random_unitary(2**self.qubit_count)
            self.quantum_state = unitary_matrix @ self.quantum_state


    def _random_unitary(self, size: int) -> np.ndarray:
        """
        Generates a random unitary matrix.
        """
        # Generate a random complex matrix
        random_matrix = np.random.rand(size, size) + 1j * np.random.rand(size, size)

        # Perform QR decomposition to obtain a unitary matrix
        q, _ = np.linalg.qr(random_matrix)

        # Ensure the determinant is 1 (optional, but often desired)
        determinant = np.linalg.det(q)
        q *= np.diag(np.power(np.abs(determinant), -1/size) * np.exp(-1j * np.angle(determinant) / size))

        return q


    def measure_qubit(self, qubit_index: int) -> int:
        """
        Measures a single qubit and returns the result (0 or 1).
        """
        if not (0 <= qubit_index < self.qubit_count):
            raise ValueError("Invalid qubit index.")

        # Calculate probabilities
        probabilities = self._calculate_probabilities()

        # Determine the measurement outcome
        outcome = self.rng.choice([0, 1], p=[probabilities[0], probabilities[1]])
        return outcome


    def _calculate_probabilities(self) -> np.ndarray:
        """
        Calculates the probabilities of measuring each qubit in the computational basis.
        """
        probabilities = []
        for i in range(self.qubit_count):
            # Calculate the probability of measuring 0 for the qubit
            probability_0 = 0.0
            for j in range(2**self.qubit_count):
                if (j >> i) & 1 == 0:  # Check if the i-th bit is 0
                    probability_0 += np.abs(self.quantum_state[j])**2
            probabilities.append(probability_0)

        # Calculate the probability of measuring 1 for the qubit
        probabilities_1 = []
        for i in range(self.qubit_count):
            probability_1 = 1.0 - probabilities[i]
            probabilities_1.append(probability_1)

        return np.array([probabilities[0], probabilities_1[0]]) # Return probabilities for the first qubit


    def get_state_vector(self) -> np.ndarray:
        """
        Returns the current quantum state vector.
        """
        return self.quantum_state


    def run_circuit(self, circuit_description: list):
        """
        Runs a quantum circuit described by a list of gate operations.
        Each element in the list is a tuple: (gate_type, *qubit_indices)
        """
        for gate_operation in circuit_description:
            gate_type = gate_operation[0]
            if gate_type == "H":
                self.apply_hadamard(gate_operation[1])
            elif gate_type == "CNOT":
                self.apply_cnot(gate_operation[1], gate_operation[2])
            elif gate_type == "X":
                self.apply_pauli_x(gate_operation[1])
            elif gate_type == "Z":
                self.apply_pauli_z(gate_operation[1])
            else:
                raise ValueError(f"Unknown gate type: {gate_type}")


    def verify_result(self, expected_result: int, measured_qubit: int, tolerance: float = 0.1) -> bool:
        """
        Verifies the correctness of a measurement against an expected result,
        considering potential decoherence.

        Args:
            expected_result: The expected measurement outcome (0 or 1).
            measured_qubit: The index of the qubit that was measured.
            tolerance: The acceptable deviation from the expected probability.

        Returns:
            True if the result is within the tolerance, False otherwise.
        """
        probabilities = self._calculate_probabilities()
        expected_probability = probabilities[expected_result]

        # Check if the probability is within the tolerance
        if expected_probability >= 1 - tolerance and expected_result == 1:
            return True
        elif expected_probability <= tolerance and expected_result == 0:
            return True
        else:
            return False