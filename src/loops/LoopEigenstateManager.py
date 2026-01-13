import numpy as np
import scipy.linalg as la
import random

class LoopEigenstateManager:
    """
    Manages the eigenstates associated with loop operators during execution.
    This class provides methods for initializing, updating, and accessing
    the eigenstates, ensuring their consistency and orthogonality.
    """

    def __init__(self, num_loops, dimension):
        """
        Initializes the LoopEigenstateManager.

        Args:
            num_loops (int): The number of loop operators.
            dimension (int): The dimension of the Hilbert space.
        """
        self.num_loops = num_loops
        self.dimension = dimension
        self.eigenstates = {}  # Dictionary to store eigenstates for each loop
        self.eigenvalues = {} # Dictionary to store eigenvalues for each loop
        self.initialized = False

    def initialize_eigenstates(self, loop_operators):
        """
        Initializes the eigenstates for each loop operator.

        Args:
            loop_operators (list): A list of loop operator matrices (NumPy arrays).
        """
        if len(loop_operators) != self.num_loops:
            raise ValueError("Number of loop operators does not match the expected number.")

        for i, operator in enumerate(loop_operators):
            if operator.shape != (self.dimension, self.dimension):
                raise ValueError(f"Loop operator {i} has incorrect dimensions.")

            # Compute eigenvalues and eigenvectors
            eigenvalues, eigenvectors = la.eig(operator)

            # Store the eigenstates and eigenvalues
            self.eigenstates[i] = eigenvectors
            self.eigenvalues[i] = eigenvalues

        self.initialized = True

    def get_eigenstate(self, loop_index, state_index):
        """
        Returns the eigenstate for a given loop and state index.

        Args:
            loop_index (int): The index of the loop operator.
            state_index (int): The index of the eigenstate.

        Returns:
            numpy.ndarray: The eigenstate vector.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenstates:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        if state_index < 0 or state_index >= self.dimension:
            raise ValueError(f"State index {state_index} is invalid.")

        return self.eigenstates[loop_index][:, state_index]

    def get_eigenvalue(self, loop_index, state_index):
        """
        Returns the eigenvalue for a given loop and state index.

        Args:
            loop_index (int): The index of the loop operator.
            state_index (int): The index of the eigenvalue.

        Returns:
            complex: The eigenvalue.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenvalues:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        if state_index < 0 or state_index >= self.dimension:
            raise ValueError(f"State index {state_index} is invalid.")

        return self.eigenvalues[loop_index][state_index]

    def update_eigenstate(self, loop_index, state_index, new_eigenstate):
        """
        Updates an eigenstate for a given loop operator.

        Args:
            loop_index (int): The index of the loop operator.
            state_index (int): The index of the eigenstate to update.
            new_eigenstate (numpy.ndarray): The new eigenstate vector.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenstates:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        if state_index < 0 or state_index >= self.dimension:
            raise ValueError(f"State index {state_index} is invalid.")

        if new_eigenstate.shape != (self.dimension,):
            raise ValueError("New eigenstate has incorrect dimensions.")

        self.eigenstates[loop_index][:, state_index] = new_eigenstate

    def reorthogonalize_eigenstates(self, loop_index):
        """
        Reorthogonalizes the eigenstates for a given loop operator using Gram-Schmidt.

        Args:
            loop_index (int): The index of the loop operator.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenstates:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        eigenstates = self.eigenstates[loop_index]
        num_states = eigenstates.shape[1]

        for i in range(num_states):
            v = eigenstates[:, i]
            for j in range(i):
                u = eigenstates[:, j]
                v = v - np.dot(np.conjugate(u), v) * u
            v = v / la.norm(v)
            eigenstates[:, i] = v

        self.eigenstates[loop_index] = eigenstates

    def perturb_eigenstates(self, loop_index, perturbation_strength=0.01):
        """
        Perturbs the eigenstates for a given loop operator by adding random noise.

        Args:
            loop_index (int): The index of the loop operator.
            perturbation_strength (float): The strength of the perturbation.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenstates:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        eigenstates = self.eigenstates[loop_index]
        num_states = eigenstates.shape[1]

        for i in range(num_states):
            noise = np.random.normal(0, perturbation_strength, self.dimension) + 1j * np.random.normal(0, perturbation_strength, self.dimension)
            eigenstates[:, i] = eigenstates[:, i] + noise
            eigenstates[:, i] = eigenstates[:, i] / la.norm(eigenstates[:, i]) # Renormalize

        self.eigenstates[loop_index] = eigenstates

    def get_all_eigenstates(self, loop_index):
        """
        Returns all eigenstates for a given loop operator.

        Args:
            loop_index (int): The index of the loop operator.

        Returns:
            numpy.ndarray: A matrix where each column is an eigenstate.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenstates:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        return self.eigenstates[loop_index]

    def get_all_eigenvalues(self, loop_index):
        """
        Returns all eigenvalues for a given loop operator.

        Args:
            loop_index (int): The index of the loop operator.

        Returns:
            numpy.ndarray: An array of eigenvalues.
        """
        if not self.initialized:
            raise ValueError("Eigenstates have not been initialized.")

        if loop_index not in self.eigenvalues:
            raise ValueError(f"Loop index {loop_index} is invalid.")

        return self.eigenvalues[loop_index]

    def generate_random_loop_operators(self):
        """
        Generates random loop operators for testing purposes.

        Returns:
            list: A list of random loop operator matrices.
        """
        loop_operators = []
        for _ in range(self.num_loops):
            # Generate a random complex matrix
            random_matrix = np.random.rand(self.dimension, self.dimension) + 1j * np.random.rand(self.dimension, self.dimension)
            # Make it Hermitian (self-adjoint) to ensure real eigenvalues
            hermitian_matrix = (random_matrix + random_matrix.conj().T) / 2
            loop_operators.append(hermitian_matrix)
        return loop_operators

if __name__ == '__main__':
    # Example usage
    num_loops = 3
    dimension = 4

    # Create an instance of the LoopEigenstateManager
    eigenstate_manager = LoopEigenstateManager(num_loops, dimension)

    # Generate random loop operators (for demonstration)
    loop_operators = eigenstate_manager.generate_random_loop_operators()

    # Initialize the eigenstates
    eigenstate_manager.initialize_eigenstates(loop_operators)

    # Access and print some eigenstates and eigenvalues
    for i in range(num_loops):
        print(f"Loop {i}:")
        for j in range(dimension):
            eigenstate = eigenstate_manager.get_eigenstate(i, j)
            eigenvalue = eigenstate_manager.get_eigenvalue(i, j)
            print(f"  Eigenstate {j}: {eigenstate}")
            print(f"  Eigenvalue {j}: {eigenvalue}")

    # Perturb and reorthogonalize eigenstates for loop 0
    eigenstate_manager.perturb_eigenstates(0, perturbation_strength=0.05)
    eigenstate_manager.reorthogonalize_eigenstates(0)

    print("\nAfter perturbation and reorthogonalization (Loop 0):")
    for j in range(dimension):
        eigenstate = eigenstate_manager.get_eigenstate(0, j)
        print(f"  Eigenstate {j}: {eigenstate}")