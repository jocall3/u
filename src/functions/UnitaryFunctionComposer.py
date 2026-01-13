import numpy as np

def unitary_function_composer(unitary_matrices):
    """
    Composes a sequence of unitary matrices into a single unitary matrix
    representing the combined transformation.  This function performs
    matrix multiplication to achieve function composition.

    Args:
        unitary_matrices (list of numpy.ndarray): A list of unitary matrices.
                                                 Each matrix should be a square
                                                 complex-valued NumPy array.
                                                 The matrices are applied in
                                                 the order they appear in the list.

    Returns:
        numpy.ndarray: A single unitary matrix representing the composition
                       of all input matrices. Returns None if the input list
                       is empty or if any matrix is not square or not unitary.
                       Returns the first matrix if the list contains only one matrix.

    Raises:
        TypeError: If the input is not a list or if any element in the list
                   is not a NumPy array.
        ValueError: If any matrix is not square or if the matrices have
                    incompatible dimensions for multiplication.
        AssertionError: If any matrix is not unitary (within a tolerance).
    """

    if not isinstance(unitary_matrices, list):
        raise TypeError("Input must be a list of unitary matrices.")

    if not unitary_matrices:
        return None  # Return None for an empty list

    if len(unitary_matrices) == 1:
        return unitary_matrices[0]

    composed_matrix = unitary_matrices[0]

    for i in range(1, len(unitary_matrices)):
        matrix = unitary_matrices[i]

        if not isinstance(matrix, np.ndarray):
            raise TypeError("Each element in the list must be a NumPy array.")

        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Each matrix must be square.")

        if composed_matrix.shape[1] != matrix.shape[0]:
            raise ValueError("Matrices have incompatible dimensions for multiplication.")

        # Check if the matrix is unitary (U * U_dagger = I)
        U_dagger = np.conjugate(matrix.T)
        identity = np.eye(matrix.shape[0])
        assert np.allclose(matrix @ U_dagger, identity), "Matrix is not unitary."

        composed_matrix = composed_matrix @ matrix

    # Final check to ensure the composed matrix is unitary
    U_dagger = np.conjugate(composed_matrix.T)
    identity = np.eye(composed_matrix.shape[0])
    assert np.allclose(composed_matrix @ U_dagger, identity), "Composed matrix is not unitary."

    return composed_matrix

if __name__ == '__main__':
    # Example usage:
    # Define some unitary matrices (example: Hadamard and Pauli-X)
    hadamard = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]])
    pauli_x = np.array([[0, 1], [1, 0]])

    # Create a list of unitary matrices
    unitary_list = [hadamard, pauli_x, hadamard]

    # Compose the unitary matrices
    composed_unitary = unitary_function_composer(unitary_list)

    # Print the composed unitary matrix
    if composed_unitary is not None:
        print("Composed Unitary Matrix:")
        print(composed_unitary)
    else:
        print("No unitary matrices to compose.")

    # Example with a single matrix
    single_matrix_list = [hadamard]
    composed_single = unitary_function_composer(single_matrix_list)
    print("\nComposed Single Matrix:")
    print(composed_single)

    # Example with an empty list
    empty_list = []
    composed_empty = unitary_function_composer(empty_list)
    print("\nComposed Empty List:")
    print(composed_empty)