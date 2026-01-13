import random
import numpy as np

class DecoherenceInjector:
    """
    A class to inject controlled decoherence into quantum states or simulations.
    This allows for testing the robustness of quantum algorithms and hardware
    against noise.

    The injector can simulate various decoherence channels, such as:
        - Amplitude damping
        - Phase damping (dephasing)
        - Depolarizing channel
        - Custom noise models

    The strength of the decoherence can be controlled by parameters like:
        - Error probability
        - Time duration
        - Temperature (for thermal noise models)
    """

    def __init__(self, seed=None):
        """
        Initializes the DecoherenceInjector with a random seed for reproducibility.

        Args:
            seed (int, optional): Random seed. Defaults to None.
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)  # Seed NumPy as well

        self.noise_models = {
            "amplitude_damping": self._amplitude_damping,
            "phase_damping": self._phase_damping,
            "depolarizing": self._depolarizing,
            "custom": self._custom_noise
        }

    def inject_decoherence(self, quantum_state, noise_model="amplitude_damping", **kwargs):
        """
        Injects decoherence into a quantum state according to the specified noise model.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.  Can be a state vector or density matrix.
            noise_model (str): The name of the noise model to use.  Must be one of the keys in self.noise_models.
            **kwargs: Keyword arguments specific to the chosen noise model.

        Returns:
            numpy.ndarray: The decohered quantum state.

        Raises:
            ValueError: If the noise model is not recognized.
        """
        if noise_model not in self.noise_models:
            raise ValueError(f"Unknown noise model: {noise_model}.  Valid models are: {list(self.noise_models.keys())}")

        return self.noise_models[noise_model](quantum_state, **kwargs)

    def _amplitude_damping(self, quantum_state, gamma=0.1):
        """
        Simulates amplitude damping decoherence.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            gamma (float): The probability of energy loss (0 <= gamma <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        # Kraus operators for amplitude damping
        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = np.array([[0, np.sqrt(gamma)], [0, 0]])

        if len(quantum_state.shape) == 1:  # State vector
            rho = np.outer(quantum_state, np.conjugate(quantum_state))
        else: # Density matrix
            rho = quantum_state

        rho_new = K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T

        return rho_new

    def _phase_damping(self, quantum_state, lambda_val=0.1):
        """
        Simulates phase damping (dephasing) decoherence.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            lambda_val (float): The dephasing probability (0 <= lambda_val <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        # Kraus operators for phase damping
        K0 = np.array([[1, 0], [0, np.sqrt(1 - lambda_val)]])
        K1 = np.array([[0, 0], [0, np.sqrt(lambda_val)]])

        if len(quantum_state.shape) == 1:  # State vector
            rho = np.outer(quantum_state, np.conjugate(quantum_state))
        else: # Density matrix
            rho = quantum_state

        rho_new = K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T

        return rho_new

    def _depolarizing(self, quantum_state, p=0.1):
        """
        Simulates the depolarizing channel.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            p (float): The probability of depolarization (0 <= p <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        I = np.eye(2)
        X = np.array([[0, 1], [1, 0]])
        Y = np.array([[0, -1j], [1j, 0]])
        Z = np.array([[1, 0], [0, -1]])

        if len(quantum_state.shape) == 1:  # State vector
            rho = np.outer(quantum_state, np.conjugate(quantum_state))
        else: # Density matrix
            rho = quantum_state

        rho_new = (1 - p) * rho + (p / 3) * (X @ rho @ X + Y @ rho @ Y + Z @ rho @ Z)

        return rho_new

    def _custom_noise(self, quantum_state, kraus_operators):
        """
        Applies custom noise defined by a set of Kraus operators.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            kraus_operators (list of numpy.ndarray): A list of Kraus operators.

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        if len(quantum_state.shape) == 1:  # State vector
            rho = np.outer(quantum_state, np.conjugate(quantum_state))
        else: # Density matrix
            rho = quantum_state

        rho_new = np.zeros_like(rho, dtype=complex)
        for K in kraus_operators:
            rho_new += K @ rho @ K.conj().T

        return rho_new

    def apply_bit_flip(self, quantum_state, probability):
        """
        Applies a bit flip error to a qubit with a given probability.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            probability (float): The probability of a bit flip (0 <= probability <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        if random.random() < probability:
            X = np.array([[0, 1], [1, 0]])
            if len(quantum_state.shape) == 1:  # State vector
                return X @ quantum_state
            else: # Density matrix
                return X @ quantum_state @ X
        else:
            return quantum_state

    def apply_phase_flip(self, quantum_state, probability):
        """
        Applies a phase flip error to a qubit with a given probability.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            probability (float): The probability of a phase flip (0 <= probability <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        if random.random() < probability:
            Z = np.array([[1, 0], [0, -1]])
            if len(quantum_state.shape) == 1:  # State vector
                return Z @ quantum_state
            else: # Density matrix
                return Z @ quantum_state @ Z
        else:
            return quantum_state

    def apply_bit_phase_flip(self, quantum_state, probability):
        """
        Applies a bit-phase flip error to a qubit with a given probability.

        Args:
            quantum_state (numpy.ndarray): The quantum state to be decohered.
            probability (float): The probability of a bit-phase flip (0 <= probability <= 1).

        Returns:
            numpy.ndarray: The decohered quantum state.
        """
        if random.random() < probability:
            Y = np.array([[0, -1j], [1j, 0]])
            if len(quantum_state.shape) == 1:  # State vector
                return Y @ quantum_state
            else: # Density matrix
                return Y @ quantum_state @ Y
        else:
            return quantum_state