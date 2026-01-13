import unittest
import numpy as np
from scipy.linalg import expm

class TestNonHermitianOperator(unittest.TestCase):

    def setUp(self):
        # Define a simple non-Hermitian matrix
        self.non_hermitian_matrix = np.array([[1, 1j], [-1j, 2]])

        # Define a Hermitian matrix for comparison
        self.hermitian_matrix = np.array([[1, 1j], [-1j, 1]])

        # Define an initial state vector
        self.initial_state = np.array([1, 0], dtype=complex)

        # Define a small time step
        self.time_step = 0.01

    def test_non_hermiticity(self):
        """
        Test that the matrix is indeed non-Hermitian.
        """
        self.assertFalse(np.allclose(self.non_hermitian_matrix, self.non_hermitian_matrix.conj().T),
                         "The matrix should be non-Hermitian.")

    def test_amplitude_decay_gain(self):
        """
        Test that the amplitude changes over time due to non-Hermiticity.
        """
        # Evolve the state using the non-Hermitian matrix
        evolution_operator = expm(-1j * self.non_hermitian_matrix * self.time_step)
        final_state = evolution_operator @ self.initial_state

        # Check if the norm of the state vector changes (amplitude decay/gain)
        initial_norm = np.linalg.norm(self.initial_state)
        final_norm = np.linalg.norm(final_state)

        self.assertNotAlmostEqual(initial_norm, final_norm,
                                  msg="The norm of the state vector should change due to non-Hermiticity.")

    def test_probability_change(self):
        """
        Test that the probabilities change over time due to non-Hermiticity.
        """
        # Evolve the state using the non-Hermitian matrix
        evolution_operator = expm(-1j * self.non_hermitian_matrix * self.time_step)
        final_state = evolution_operator @ self.initial_state

        # Calculate initial and final probabilities
        initial_probability = np.abs(self.initial_state)**2
        final_probability = np.abs(final_state)**2

        # Check if the probabilities have changed
        self.assertFalse(np.allclose(initial_probability, final_probability),
                         "The probabilities should change due to non-Hermiticity.")

    def test_hermitian_amplitude_conservation(self):
        """
        Test that the amplitude is conserved for a Hermitian matrix.
        """
        # Evolve the state using the Hermitian matrix
        evolution_operator = expm(-1j * self.hermitian_matrix * self.time_step)
        final_state = evolution_operator @ self.initial_state

        # Check if the norm of the state vector remains constant
        initial_norm = np.linalg.norm(self.initial_state)
        final_norm = np.linalg.norm(final_state)

        self.assertAlmostEqual(initial_norm, final_norm,
                               msg="The norm of the state vector should be conserved for a Hermitian matrix.")

    def test_hermitian_probability_conservation(self):
        """
        Test that the probabilities are conserved for a Hermitian matrix.
        """
        # Evolve the state using the Hermitian matrix
        evolution_operator = expm(-1j * self.hermitian_matrix * self.time_step)
        final_state = evolution_operator @ self.initial_state

        # Calculate initial and final probabilities
        initial_probability = np.abs(self.initial_state)**2
        final_probability = np.abs(final_state)**2

        # Check if the probabilities remain constant
        self.assertTrue(np.allclose(np.sum(initial_probability), np.sum(final_probability)),
                        "The probabilities should be conserved for a Hermitian matrix.")

if __name__ == '__main__':
    unittest.main()