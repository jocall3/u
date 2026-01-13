import numpy as np
from typing import Callable, Union, List, Tuple

class FunctionToUnitaryMapper:
    """
    Maps classical functions to their unitary operator representations.

    This class provides methods to construct unitary matrices that implement
    classical functions in a reversible manner, suitable for quantum computation.
    """

    def __init__(self, num_qubits: int):
        """
        Initializes the FunctionToUnitaryMapper.

        Args:
            num_qubits: The number of qubits required to represent the function.
        """
        self.num_qubits = num_qubits
        self.dimension = 2**num_qubits

    def create_unitary(self, function: Callable[[int], int]) -> np.ndarray:
        """
        Creates a unitary matrix that implements the given classical function.

        Args:
            function: A callable that maps an integer input to an integer output.
                      The input and output integers are assumed to be representable
                      using the number of qubits specified in the constructor.

        Returns:
            A unitary matrix (NumPy array) representing the function.

        Raises:
            ValueError: If the function's output is not within the representable range.
        """

        unitary_matrix = np.zeros((self.dimension, self.dimension), dtype=complex)

        for input_state in range(self.dimension):
            output_state = function(input_state)

            if not (0 <= output_state < self.dimension):
                raise ValueError(f"Function output {output_state} is out of range for {self.num_qubits} qubits.")

            unitary_matrix[output_state, input_state] = 1.0

        if not self.is_unitary(unitary_matrix):
            raise ValueError("Generated matrix is not unitary. Check the function mapping.")

        return unitary_matrix

    def is_unitary(self, matrix: np.ndarray) -> bool:
        """
        Checks if a given matrix is unitary.

        Args:
            matrix: The matrix to check.

        Returns:
            True if the matrix is unitary, False otherwise.
        """
        rows, cols = matrix.shape
        if rows != cols:
            return False
        adjoint = np.conjugate(matrix.transpose())
        identity = np.eye(rows)
        return np.allclose(matrix @ adjoint, identity)

    def controlled_unitary(self, unitary: np.ndarray, control_qubit: int, target_qubits: Union[int, List[int]]) -> np.ndarray:
        """
        Creates a controlled unitary gate.

        Args:
            unitary: The unitary matrix to be controlled.
            control_qubit: The index of the control qubit (0-indexed).
            target_qubits: The index or indices of the target qubits.

        Returns:
            A controlled unitary matrix.
        """
        num_qubits = int(np.log2(unitary.shape[0]))  # Number of qubits the unitary acts on
        full_size = 2**(self.num_qubits)
        controlled_unitary_matrix = np.eye(full_size, dtype=complex)

        for i in range(unitary.shape[0]):
            for j in range(unitary.shape[1]):
                # Construct the indices where the unitary should be applied
                index_i = bin(i)[2:].zfill(num_qubits)
                index_j = bin(j)[2:].zfill(num_qubits)

                # Iterate through all possible control qubit states
                for control_state in [0, 1]:
                    control_string = bin(control_state)[2:].zfill(1)
                    full_index_i = control_string + index_i
                    full_index_j = control_string + index_j

                    full_index_i_int = int(full_index_i, 2)
                    full_index_j_int = int(full_index_j, 2)

                    if control_state == 1:
                        controlled_unitary_matrix[full_index_i_int, full_index_j_int] = unitary[i, j]
                    else:
                        if full_index_i_int == full_index_j_int:
                            controlled_unitary_matrix[full_index_i_int, full_index_j_int] = 1.0

        return controlled_unitary_matrix

    def quantum_fourier_transform(self) -> np.ndarray:
        """
        Generates the Quantum Fourier Transform (QFT) matrix.

        Returns:
            The QFT matrix.
        """
        N = self.dimension
        qft_matrix = np.zeros((N, N), dtype=complex)
        for i in range(N):
            for j in range(N):
                qft_matrix[i, j] = np.exp(2j * np.pi * i * j / N) / np.sqrt(N)
        return qft_matrix

    def phase_estimation(self, unitary: np.ndarray, eigenvector: np.ndarray, num_estimation_qubits: int) -> Tuple[np.ndarray, float]:
        """
        Performs Quantum Phase Estimation (QPE).

        Args:
            unitary: The unitary operator whose eigenvalue we want to estimate.
            eigenvector: An eigenvector of the unitary operator.
            num_estimation_qubits: The number of qubits used for phase estimation.

        Returns:
            A tuple containing:
            - The measurement probabilities for each state.
            - The estimated phase.
        """
        # Simplified QPE - assumes perfect eigenvector and no noise
        N = 2**num_estimation_qubits
        qft_dagger = np.conjugate(self.quantum_fourier_transform())

        # Apply controlled-U operations (simplified - assumes we can apply U^2^j directly)
        # In a real implementation, this would involve repeated applications of U
        combined_state = np.kron(np.ones(N) / np.sqrt(N), eigenvector) # Initial state: |0>^n |psi>

        for j in range(num_estimation_qubits):
            for k in range(2**j):
                controlled_u = self.controlled_unitary(unitary, 0, 1) # Simplified: control on qubit 0, target on qubit 1
                combined_state = controlled_u @ combined_state

        # Apply inverse QFT
        estimation_qubits = combined_state[:N]
        final_state = qft_dagger @ estimation_qubits

        # Measure (simulate measurement by taking probabilities)
        probabilities = np.abs(final_state)**2

        # Estimate the phase
        estimated_phase = np.argmax(probabilities) / N

        return probabilities, estimated_phase