import random
import numpy as np

class ConfigStateGenerator:
    """
    Generates quantum states from configuration parameters.
    This class provides methods to create various quantum states based on input configurations,
    incorporating randomness and ensuring uniqueness in the generated states.
    """

    def __init__(self, seed=None):
        """
        Initializes the ConfigStateGenerator with an optional seed for reproducibility.

        Args:
            seed (int, optional): Seed for the random number generator. Defaults to None.
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)  # Seed NumPy as well

        self.generated_states = set()  # Track generated states to avoid duplicates

    def generate_random_state(self, dimension):
        """
        Generates a random quantum state vector of a given dimension.

        Args:
            dimension (int): The dimension of the quantum state vector.

        Returns:
            numpy.ndarray: A normalized complex-valued numpy array representing the quantum state.
        """
        while True:
            real_parts = np.random.rand(dimension)
            imag_parts = np.random.rand(dimension)
            complex_vector = real_parts + 1j * imag_parts
            norm = np.linalg.norm(complex_vector)
            if norm > 0:  # Avoid division by zero
                state = complex_vector / norm
                state_tuple = tuple(state.tolist())  # Convert to tuple for hashing
                if state_tuple not in self.generated_states:
                    self.generated_states.add(state_tuple)
                    return state
            # If norm is zero or state is duplicate, regenerate

    def generate_bell_state(self, bell_state_type="phi_plus"):
        """
        Generates one of the four Bell states.

        Args:
            bell_state_type (str, optional): The type of Bell state to generate.
                Options are "phi_plus", "phi_minus", "psi_plus", "psi_minus".
                Defaults to "phi_plus".

        Returns:
            numpy.ndarray: A numpy array representing the Bell state.

        Raises:
            ValueError: If an invalid bell_state_type is provided.
        """
        if bell_state_type == "phi_plus":
            state = np.array([1, 0, 0, 1]) / np.sqrt(2)
        elif bell_state_type == "phi_minus":
            state = np.array([1, 0, 0, -1]) / np.sqrt(2)
        elif bell_state_type == "psi_plus":
            state = np.array([0, 1, 1, 0]) / np.sqrt(2)
        elif bell_state_type == "psi_minus":
            state = np.array([0, 1, -1, 0]) / np.sqrt(2)
        else:
            raise ValueError("Invalid bell_state_type. Choose from 'phi_plus', 'phi_minus', 'psi_plus', 'psi_minus'.")

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state

    def generate_ghz_state(self, num_qubits):
        """
        Generates a GHZ state for a given number of qubits.

        Args:
            num_qubits (int): The number of qubits in the GHZ state.

        Returns:
            numpy.ndarray: A numpy array representing the GHZ state.
        """
        dimension = 2**num_qubits
        state = np.zeros(dimension)
        state[0] = 1 / np.sqrt(2)
        state[-1] = 1 / np.sqrt(2)

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state

    def generate_w_state(self, num_qubits):
        """
        Generates a W state for a given number of qubits.

        Args:
            num_qubits (int): The number of qubits in the W state.

        Returns:
            numpy.ndarray: A numpy array representing the W state.
        """
        dimension = 2**num_qubits
        state = np.zeros(dimension)
        for i in range(num_qubits):
            state[2**i] = 1 / np.sqrt(num_qubits)

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state

    def generate_custom_state(self, amplitudes):
        """
        Generates a custom quantum state from a list of complex amplitudes.

        Args:
            amplitudes (list): A list of complex numbers representing the amplitudes of the state.

        Returns:
            numpy.ndarray: A normalized numpy array representing the custom quantum state.
        """
        amplitudes = np.array(amplitudes, dtype=np.complex128)
        norm = np.linalg.norm(amplitudes)
        if norm == 0:
            raise ValueError("Amplitudes cannot all be zero.")
        state = amplitudes / norm

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape) + 1j * np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state

    def generate_superposition_state(self, basis_states, probabilities):
        """
        Generates a superposition state from a list of basis states and their probabilities.

        Args:
            basis_states (list): A list of numpy arrays representing the basis states.
            probabilities (list): A list of probabilities corresponding to each basis state.
                                  The probabilities must sum to 1.

        Returns:
            numpy.ndarray: A numpy array representing the superposition state.
        """
        if not np.isclose(sum(probabilities), 1.0):
            raise ValueError("Probabilities must sum to 1.")

        state = np.zeros_like(basis_states[0], dtype=np.complex128)
        for i, basis_state in enumerate(basis_states):
            state += np.sqrt(probabilities[i]) * basis_state

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape) + 1j * np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state

    def generate_entangled_state(self, state1, state2):
        """
        Generates an entangled state by taking the tensor product of two states.

        Args:
            state1 (numpy.ndarray): The first quantum state.
            state2 (numpy.ndarray): The second quantum state.

        Returns:
            numpy.ndarray: A numpy array representing the entangled state.
        """
        state = np.kron(state1, state2)

        state_tuple = tuple(state.tolist())
        if state_tuple not in self.generated_states:
            self.generated_states.add(state_tuple)
            return state
        else:
            # If duplicate, generate a slightly perturbed version
            perturbed_state = state + np.random.normal(0, 0.001, size=state.shape) + 1j * np.random.normal(0, 0.001, size=state.shape)
            perturbed_state /= np.linalg.norm(perturbed_state)
            return perturbed_state