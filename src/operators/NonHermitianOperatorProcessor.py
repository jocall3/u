import numpy as np
from scipy.linalg import expm

class NonHermitianOperatorProcessor:
    """
    Processes the dynamics of a quantum system under the influence of a non-Hermitian operator.
    This class handles the time evolution of a quantum state, accounting for gain and loss
    processes described by the non-Hermitian Hamiltonian.
    """

    def __init__(self, hamiltonian, initial_state, dt):
        """
        Initializes the NonHermitianOperatorProcessor.

        Args:
            hamiltonian (numpy.ndarray): The non-Hermitian Hamiltonian matrix.
            initial_state (numpy.ndarray): The initial quantum state vector.
            dt (float): The time step for the time evolution.
        """
        self.hamiltonian = hamiltonian
        self.state = initial_state
        self.dt = dt
        self.time = 0.0

    def evolve_state(self):
        """
        Evolves the quantum state by one time step using the non-Hermitian Hamiltonian.
        Uses the matrix exponential method for time evolution.
        """
        # Calculate the time evolution operator
        evolution_operator = expm(-1j * self.hamiltonian * self.dt)

        # Evolve the state
        self.state = evolution_operator @ self.state

        # Normalize the state (optional, but often necessary for non-Hermitian systems)
        norm = np.linalg.norm(self.state)
        if norm > 0:  # Avoid division by zero
            self.state = self.state / norm
        else:
            print("Warning: State norm is zero.  State may be collapsing to zero.")

        self.time += self.dt

    def get_current_state(self):
        """
        Returns the current quantum state.

        Returns:
            numpy.ndarray: The current quantum state vector.
        """
        return self.state

    def get_time(self):
        """
        Returns the current time.

        Returns:
            float: The current time.
        """
        return self.time

    def set_hamiltonian(self, new_hamiltonian):
        """
        Sets a new Hamiltonian for the system.

        Args:
            new_hamiltonian (numpy.ndarray): The new non-Hermitian Hamiltonian matrix.
        """
        self.hamiltonian = new_hamiltonian

    def set_time_step(self, new_dt):
        """
        Sets a new time step for the evolution.

        Args:
            new_dt (float): The new time step.
        """
        self.dt = new_dt

    def measure_observable(self, observable):
        """
        Calculates the expectation value of an observable.

        Args:
            observable (numpy.ndarray): The observable matrix.

        Returns:
            complex: The expectation value of the observable.
        """
        return np.conjugate(self.state) @ observable @ self.state

    def simulate_time_evolution(self, total_time):
        """
        Simulates the time evolution of the system for a specified total time.

        Args:
            total_time (float): The total time to simulate.

        Returns:
            tuple: A tuple containing lists of times and corresponding state vectors.
        """
        times = []
        states = []
        while self.time < total_time:
            times.append(self.time)
            states.append(self.state.copy())  # Store a copy to avoid modification
            self.evolve_state()
        times.append(self.time)
        states.append(self.state.copy())
        return times, states

    def reset_state(self, new_initial_state):
        """
        Resets the state to a new initial state and resets the time to 0.

        Args:
            new_initial_state (numpy.ndarray): The new initial state vector.
        """
        self.state = new_initial_state
        self.time = 0.0