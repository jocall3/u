import unittest
import numpy as np
import cmath

# Assume the interpolator and its dependencies are in the q_alchemy library
# This is a common practice in unit testing, where we test one module in isolation.
# We will assume the following imports would work in the actual project structure.
from q_alchemy.interpolation import QuantumClassicalInterpolator, InterpolationMethod
from q_alchemy.errors import StateVectorError, InterpolationParameterError, IncompatibleStateError

class TestQuantumClassicalInterpolator(unittest.TestCase):
    """
    Unit tests for the QuantumClassicalInterpolator.

    These tests rigorously verify the behavior of the interpolation logic,
    ensuring smooth, norm-preserving transitions from a classical basis state
    to a target quantum superposition. The tests cover boundary conditions,
    intermediate states for different interpolation algorithms, error handling,
    and multi-qubit systems.
    """

    def setUp(self):
        """Set up common quantum states for use in multiple tests."""
        # Single-qubit basis states
        self.classical_state_0 = np.array([1, 0], dtype=np.complex128)
        self.classical_state_1 = np.array([0, 1], dtype=np.complex128)

        # Single-qubit superposition states
        self.hadamard_state = (1 / np.sqrt(2)) * np.array([1, 1], dtype=np.complex128)
        self.y_basis_state = (1 / np.sqrt(2)) * np.array([1, 1j], dtype=np.complex128)

        # Two-qubit states (4-dimensional Hilbert space)
        self.classical_state_00 = np.array([1, 0, 0, 0], dtype=np.complex128)
        self.bell_state_phi_plus = (1 / np.sqrt(2)) * np.array([1, 0, 0, 1], dtype=np.complex128)
        self.ghz_state_3_qubit = (1 / np.sqrt(2)) * np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=np.complex128)

    def assertStateVectorAlmostEqual(self, vec1, vec2, places=7, msg=None):
        """
        Custom assertion to compare two quantum state vectors.

        It verifies that both vectors are normalized and are equal up to a
        global phase factor by checking if the absolute value of their
        inner product is close to 1.
        """
        self.assertAlmostEqual(np.linalg.norm(vec1), 1.0, places=places, msg=f"Vector 1 is not normalized: {msg or ''}")
        self.assertAlmostEqual(np.linalg.norm(vec2), 1.0, places=places, msg=f"Vector 2 is not normalized: {msg or ''}")
        
        inner_product_mag = np.abs(np.vdot(vec1, vec2))
        self.assertAlmostEqual(inner_product_mag, 1.0, places=places,
                             msg=f"State vectors differ by more than a global phase. |<v1|v2>| = {inner_product_mag}. {msg or ''}")

    def test_successful_initialization(self):
        """Verify that the interpolator can be initialized with valid states."""
        try:
            interpolator = QuantumClassicalInterpolator(self.classical_state_0, self.hadamard_state)
            self.assertIsNotNone(interpolator)
            np.testing.assert_array_equal(interpolator.classical_state, self.classical_state_0)
            np.testing.assert_array_equal(interpolator.quantum_state, self.hadamard_state)
        except Exception as e:
            self.fail(f"Initialization failed with an unexpected exception: {e}")

    def test_initialization_fails_with_non_basis_classical_state(self):
        """Ensure initialization raises StateVectorError for a non-computational basis classical state."""
        with self.assertRaisesRegex(StateVectorError, "Classical state must be a valid computational basis state."):
            QuantumClassicalInterpolator(self.hadamard_state, self.y_basis_state)

    def test_initialization_fails_with_non_normalized_quantum_state(self):
        """Ensure initialization raises StateVectorError for a quantum state with norm != 1."""
        non_normalized_state = np.array([0.5, 0.5], dtype=np.complex128)
        with self.assertRaisesRegex(StateVectorError, "Quantum state vector must be normalized to 1."):
            QuantumClassicalInterpolator(self.classical_state_0, non_normalized_state)

    def test_initialization_fails_with_mismatched_dimensions(self):
        """Ensure initialization raises IncompatibleStateError for states from different Hilbert spaces."""
        with self.assertRaisesRegex(IncompatibleStateError, "State vectors must have the same dimensions."):
            QuantumClassicalInterpolator(self.classical_state_0, self.bell_state_phi_plus)

    def test_boundary_condition_lambda_zero(self):
        """Test that interpolate(0.0) returns the initial classical state."""
        interpolator = QuantumClassicalInterpolator(self.classical_state_1, self.y_basis_state)
        result_state = interpolator.interpolate(0.0)
        self.assertStateVectorAlmostEqual(result_state, self.classical_state_1)

    def test_boundary_condition_lambda_one(self):
        """Test that interpolate(1.0) returns the target quantum state."""
        interpolator = QuantumClassicalInterpolator(self.classical_state_00, self.bell_state_phi_plus)
        result_state = interpolator.interpolate(1.0)
        self.assertStateVectorAlmostEqual(result_state, self.bell_state_phi_plus)

    def test_midpoint_interpolation_with_slerp(self):
        """Verify the correctness of Spherical Linear Interpolation (SLERP) at lambda=0.5."""
        interpolator = QuantumClassicalInterpolator(
            self.classical_state_0, self.classical_state_1, method=InterpolationMethod.SLERP
        )
        result_state = interpolator.interpolate(0.5)
        # Interpolating between |0> and |1> (orthogonal, angle pi/2) should yield |+> at the midpoint.
        self.assertStateVectorAlmostEqual(result_state, self.hadamard_state)

    def test_midpoint_interpolation_with_nlerp(self):
        """Verify the correctness of Normalized Linear Interpolation (NLERP) at lambda=0.5."""
        interpolator = QuantumClassicalInterpolator(
            self.classical_state_0, self.hadamard_state, method=InterpolationMethod.NLERP
        )
        result_state = interpolator.interpolate(0.5)
        # NLERP: v_res = normalize((1-t)*v0 + t*v1)
        # t=0.5, v0=|0>, v1=|+>
        # unnormalized = 0.5*[1,0] + 0.5*[1/sqrt(2), 1/sqrt(2)] = [0.5 + 0.5/sqrt(2), 0.5/sqrt(2)]
        unnormalized_vec = np.array([0.5 + 0.5 / np.sqrt(2), 0.5 / np.sqrt(2)], dtype=np.complex128)
        expected_state = unnormalized_vec / np.linalg.norm(unnormalized_vec)
        self.assertStateVectorAlmostEqual(result_state, expected_state)

    def test_normalization_is_preserved_across_entire_path(self):
        """Check that the state vector norm remains 1.0 for all lambda in [0, 1]."""
        interpolator = QuantumClassicalInterpolator(self.classical_state_00, self.bell_state_phi_plus)
        for lam in np.linspace(0, 1, num=50, endpoint=True):
            with self.subTest(lambda_val=lam):
                interpolated_state = interpolator.interpolate(lam)
                norm = np.linalg.norm(interpolated_state)
                self.assertAlmostEqual(norm, 1.0, places=12,
                                     msg=f"Normalization failed at lambda={lam:.4f}. Norm was {norm}")

    def test_interpolation_parameter_out_of_bounds(self):
        """Ensure an InterpolationParameterError is raised for lambda outside [0, 1]."""
        interpolator = QuantumClassicalInterpolator(self.classical_state_0, self.hadamard_state)
        with self.assertRaises(InterpolationParameterError):
            interpolator.interpolate(-1e-9)
        with self.assertRaises(InterpolationParameterError):
            interpolator.interpolate(1.0 + 1e-9)

    def test_interpolation_with_complex_phases_slerp(self):
        """Test SLERP between a basis state and a state with non-trivial complex phases."""
        interpolator = QuantumClassicalInterpolator(self.classical_state_0, self.y_basis_state, method=InterpolationMethod.SLERP)
        
        # At lambda=0.5, the angle is halved. Angle between |0> and |Y+> is arccos(1/sqrt(2)) = pi/4.
        # Half angle is pi/8. The resulting state should be cos(pi/8)|0> + i*sin(pi/8)|1>.
        theta_half = np.pi / 8
        expected_state = np.array([np.cos(theta_half), 1j * np.sin(theta_half)], dtype=np.complex128)
        
        result_state = interpolator.interpolate(0.5)
        self.assertStateVectorAlmostEqual(result_state, expected_state)

    def test_continuity_of_interpolation(self):
        """
        Verify that the interpolation function is continuous by checking that
        small changes in lambda result in small changes in the state vector.
        """
        interpolator = QuantumClassicalInterpolator(self.classical_state_1, self.y_basis_state)
        lambda_val = 0.618  # An arbitrary point
        delta = 1e-7

        state1 = interpolator.interpolate(lambda_val)
        state2 = interpolator.interpolate(lambda_val + delta)

        # The distance between the two state vectors in Hilbert space should be small.
        distance = np.linalg.norm(state1 - state2)
        self.assertLess(distance, 1e-6, "State vector changed too abruptly for a small lambda step, suggesting discontinuity.")

    def test_interpolation_of_higher_dimensional_system(self):
        """Test interpolation for a 3-qubit system (8-dimensional space)."""
        classical_start = np.zeros(8, dtype=np.complex128)
        classical_start[0] = 1.0  # Corresponds to |000>

        interpolator = QuantumClassicalInterpolator(classical_start, self.ghz_state_3_qubit)

        # Check start and end points
        self.assertStateVectorAlmostEqual(interpolator.interpolate(0.0), classical_start)
        self.assertStateVectorAlmostEqual(interpolator.interpolate(1.0), self.ghz_state_3_qubit)

        # Check an intermediate point for normalization
        mid_state = interpolator.interpolate(0.5)
        self.assertAlmostEqual(np.linalg.norm(mid_state), 1.0)
        # Ensure it's not just one of the endpoints
        self.assertFalse(np.allclose(mid_state, classical_start))
        self.assertFalse(np.allclose(mid_state, self.ghz_state_3_qubit))

    def test_identical_start_and_end_states(self):
        """Test the edge case where the classical and quantum states are the same."""
        # Note: The "quantum" state here is also a basis state, which is a valid quantum state.
        interpolator = QuantumClassicalInterpolator(self.classical_state_0, self.classical_state_0)
        for lam in np.linspace(0, 1, 10):
            with self.subTest(lambda_val=lam):
                result_state = interpolator.interpolate(lam)
                self.assertStateVectorAlmostEqual(result_state, self.classical_state_0,
                                                msg=f"Interpolation with identical states failed at lambda={lam}")


if __name__ == '__main__':
    unittest.main(verbosity=2)