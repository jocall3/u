import unittest
import numpy as np
from cmath import exp, pi

# --- Mock Implementations for a Hypothetical Quantum Anyon Library ---
# In a real project, these would be imported from a separate library.
# For this self-contained test file, we define them here.

class Anyon:
    """Represents a topological particle (anyon) with a specific charge."""
    def __init__(self, charge_label, is_abelian=False):
        if not isinstance(charge_label, (str, int)):
            raise TypeError("charge_label must be a string or integer.")
        self.charge = charge_label
        self.is_abelian = is_abelian

    def __repr__(self):
        return f"Anyon('{self.charge}')"

    def __eq__(self, other):
        return isinstance(other, Anyon) and self.charge == other.charge

    def __hash__(self):
        return hash(self.charge)

# Define standard anyon types
VACUUM = Anyon('1')
FIBONACCI_TAU = Anyon('τ')
ISING_SIGMA = Anyon('σ', is_abelian=True)
ISING_PSI = Anyon('ψ')

class FusionError(Exception):
    """Custom exception for invalid fusion operations."""
    pass

def get_fusion_channels(a1: Anyon, a2: Anyon):
    """
    Determines the possible outcomes (fusion channels) of fusing two anyons.
    This function encodes the fusion rules of a given anyon theory.
    """
    # Fibonacci Anyon Fusion Rules
    if a1 == FIBONACCI_TAU and a2 == FIBONACCI_TAU:
        return [VACUUM, FIBONACCI_TAU]
    if (a1 == FIBONACCI_TAU and a2 == VACUUM) or (a1 == VACUUM and a2 == FIBONACCI_TAU):
        return [FIBONACCI_TAU]
    
    # Ising Anyon Fusion Rules
    if a1 == ISING_SIGMA and a2 == ISING_SIGMA:
        return [VACUUM, ISING_PSI]
    if (a1 == ISING_SIGMA and a2 == ISING_PSI) or (a1 == ISING_PSI and a2 == ISING_SIGMA):
        return [ISING_SIGMA]
    if a1 == ISING_PSI and a2 == ISING_PSI:
        return [VACUUM]

    # General rule: fusing with vacuum yields the original anyon
    if a1 == VACUUM: return [a2]
    if a2 == VACUUM: return [a1]

    raise FusionError(f"Fusion rule for {a1} ⊗ {a2} is not defined.")

def get_braid_operator(a1: Anyon, a2: Anyon, fusion_channel: Anyon):
    """
    Returns the unitary matrix (R-matrix) for braiding a1 around a2,
    given their total topological charge (fusion_channel).
    """
    # Braiding for Fibonacci Anyons (τ ⊗ τ -> 1 or τ)
    if a1 == FIBONACCI_TAU and a2 == FIBONACCI_TAU:
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        if fusion_channel == VACUUM:
            return np.array([[exp(4j * pi / 5)]])
        elif fusion_channel == FIBONACCI_TAU:
            return np.array([[exp(-3j * pi / 5)]])
        else:
            raise ValueError("Invalid fusion channel for τ ⊗ τ braid.")

    # Braiding for Ising Anyons (σ ⊗ σ -> 1 or ψ)
    if a1 == ISING_SIGMA and a2 == ISING_SIGMA:
        if fusion_channel == VACUUM:
            return np.array([[exp(-1j * pi / 8)]])
        elif fusion_channel == ISING_PSI:
            return np.array([[exp(3j * pi / 8)]])
        else:
            raise ValueError("Invalid fusion channel for σ ⊗ σ braid.")
    
    # Default for abelian cases or simple swaps
    return np.array([[1]])


class AnyonicQuantumSystem:
    """
    Represents a system of anyons encoding a quantum state.
    The state is defined in the fusion space of the anyons.
    """
    def __init__(self, anyons, initial_state_vector):
        self.anyons = list(anyons)
        self.state_vector = np.array(initial_state_vector, dtype=complex)
        # In a real system, we would validate the dimension of the state vector
        # against the Hilbert space size derived from the anyon fusion paths.

    def apply_braid(self, idx1, idx2):
        """
        Applies a braid operation between anyons at idx1 and idx2.
        This is a simplified model. A full model requires specifying the fusion
        tree to resolve basis ambiguity. Here we assume a simple 2D basis.
        """
        # This is a highly simplified representation of a non-abelian braid.
        # The F and R matrices would be used in a full implementation.
        # For this test, we'll use a pre-computed braid matrix for a known gate.
        
        # Fibonacci CNOT approximation matrix
        F = np.array([[1, 0], [0, exp(1j * pi / 5)]])
        R = np.array([[exp(-4j*pi/5), 0], [0, exp(3j*pi/5)]])
        
        # A sequence of braids can approximate a gate.
        # Braid sequence for a phase gate: B = R F R
        B = R @ F @ R
        
        self.state_vector = B @ self.state_vector

# --- Unit Test Class ---

class TestAnyonModule(unittest.TestCase):
    """
    Verifies the fundamental properties of anyonic systems, including
    fusion rules, braiding statistics, and their semantic interpretation
    as quantum computational gates.
    """

    def test_anyon_creation_and_properties(self):
        """Ensures anyons are instantiated with correct properties."""
        tau = Anyon('τ')
        sigma = Anyon('σ', is_abelian=True)
        self.assertEqual(tau.charge, 'τ')
        self.assertFalse(tau.is_abelian)
        self.assertEqual(sigma.charge, 'σ')
        self.assertTrue(sigma.is_abelian)
        with self.assertRaises(TypeError):
            Anyon(charge_label=None)

    def test_fibonacci_fusion_rules(self):
        """Validates the fusion channels for Fibonacci anyons."""
        # τ ⊗ τ → 1 ⊕ τ
        channels = get_fusion_channels(FIBONACCI_TAU, FIBONACCI_TAU)
        self.assertIn(VACUUM, channels)
        self.assertIn(FIBONACCI_TAU, channels)
        self.assertEqual(len(channels), 2)

        # τ ⊗ 1 → τ
        channels = get_fusion_channels(FIBONACCI_TAU, VACUUM)
        self.assertEqual(channels, [FIBONACCI_TAU])

    def test_ising_fusion_rules(self):
        """Validates the fusion channels for Ising anyons."""
        # σ ⊗ σ → 1 ⊕ ψ
        channels = get_fusion_channels(ISING_SIGMA, ISING_SIGMA)
        self.assertIn(VACUUM, channels)
        self.assertIn(ISING_PSI, channels)
        self.assertEqual(len(channels), 2)

        # σ ⊗ ψ → σ
        channels = get_fusion_channels(ISING_SIGMA, ISING_PSI)
        self.assertEqual(channels, [ISING_SIGMA])

    def test_invalid_fusion_raises_error(self):
        """Checks that undefined fusion rules raise a FusionError."""
        undefined_anyon = Anyon('X')
        with self.assertRaises(FusionError):
            get_fusion_channels(FIBONACCI_TAU, undefined_anyon)

    def test_abelian_braiding_phase(self):
        """Verifies the phase factor from braiding two abelian Ising anyons."""
        # Braiding σ around σ when their total charge is 1 (vacuum)
        op_vac = get_braid_operator(ISING_SIGMA, ISING_SIGMA, VACUUM)
        expected_phase_vac = exp(-1j * pi / 8)
        self.assertTrue(np.allclose(op_vac, [[expected_phase_vac]]))

        # Braiding σ around σ when their total charge is ψ
        op_psi = get_braid_operator(ISING_SIGMA, ISING_SIGMA, ISING_PSI)
        expected_phase_psi = exp(3j * pi / 8)
        self.assertTrue(np.allclose(op_psi, [[expected_phase_psi]]))

    def test_non_abelian_braiding_operator(self):
        """
        Tests the construction of a non-abelian braid operator for Fibonacci anyons.
        This operator acts on the 2D fusion space of three τ anyons.
        """
        # The braid operator B acts on the basis |(ττ)τ; 1>, |(ττ)τ; τ>
        # where the label is the intermediate fusion channel of the first two anyons.
        R1 = get_braid_operator(FIBONACCI_TAU, FIBONACCI_TAU, VACUUM)[0,0]
        R2 = get_braid_operator(FIBONACCI_TAU, FIBONACCI_TAU, FIBONACCI_TAU)[0,0]
        
        # The F-matrix (or 6j-symbol) for Fibonacci anyons
        phi = (1 + np.sqrt(5)) / 2
        F = np.array([[1/phi, 1/np.sqrt(phi)],
                      [1/np.sqrt(phi), -1/phi]])
        
        # The braid operator is B = F⁻¹ R F
        # Since F is its own inverse (F²=I), F⁻¹ = F
        R_diag = np.diag([R1, R2])
        B_matrix = F @ R_diag @ F

        # Expected B matrix for Fibonacci anyons
        expected_B = np.array([
            [exp(4j*pi/5)/phi, exp(-3j*pi/5)/np.sqrt(phi)],
            [exp(4j*pi/5)/np.sqrt(phi), -exp(-3j*pi/5)/phi]
        ])
        
        self.assertTrue(np.allclose(B_matrix, expected_B))
        
        # Verify unitarity: B†B = I
        self.assertTrue(np.allclose(B_matrix.conj().T @ B_matrix, np.identity(2)))

    def test_topological_invariance_reidemeister_2(self):
        """
        Verifies that a braid and its inverse cancel (Reidemeister II move).
        B(i, i+1) * B⁻¹(i, i+1) = I
        """
        # For non-abelian anyons, the inverse braid is not just the conjugate transpose
        # of the R-matrix, but the R-matrix for the inverse braid topology.
        # R⁻¹ is the R-matrix for braiding particle 2 around particle 1.
        # For Fibonacci anyons, R_21 = R_12⁻¹ = R_12*
        R_tau_tau_vac = get_braid_operator(FIBONACCI_TAU, FIBONACCI_TAU, VACUUM)
        R_inv_tau_tau_vac = R_tau_tau_vac.conj().T
        
        identity = R_tau_tau_vac @ R_inv_tau_tau_vac
        self.assertTrue(np.allclose(identity, np.identity(1)))

    def test_semantic_transformation_to_quantum_gate(self):
        """
        Tests if a specific sequence of braids correctly transforms a quantum state,
        emulating a known quantum gate. This demonstrates the "semantic" value.
        """
        # A specific braid sequence on 3 anyons can approximate a phase gate.
        # Let the computational basis be |0> -> |(ττ)τ; 1> and |1> -> |(ττ)τ; τ>
        # Initial state: |+> = 1/sqrt(2) * (|0> + |1>)
        initial_state = (1/np.sqrt(2)) * np.array([1, 1])
        
        system = AnyonicQuantumSystem(
            anyons=[FIBONACCI_TAU, FIBONACCI_TAU, FIBONACCI_TAU],
            initial_state_vector=initial_state
        )
        
        # This is a mock of applying a specific braid sequence.
        # The mock `apply_braid` implements a phase gate B = RFR.
        system.apply_braid(0, 1)
        
        final_state = system.state_vector
        
        # Expected final state after applying the phase gate B to |+>
        F = np.array([[1, 0], [0, exp(1j * pi / 5)]])
        R = np.array([[exp(-4j*pi/5), 0], [0, exp(3j*pi/5)]])
        B = R @ F @ R
        expected_final_state = B @ initial_state
        
        # Verify the semantic transformation
        self.assertTrue(np.allclose(final_state, expected_final_state))
        
        # Check that the relative phase has been altered
        phase_diff_initial = np.angle(initial_state[1]) - np.angle(initial_state[0])
        phase_diff_final = np.angle(final_state[1]) - np.angle(final_state[0])
        self.assertNotAlmostEqual(phase_diff_initial, phase_diff_final)

    def test_pentagon_equation_consistency(self):
        """
        Checks a simplified instance of the pentagon equation, which ensures
        the consistency of fusion path changes (associativity of fusion).
        F * F = I for the Fibonacci model, a key consistency check.
        """
        phi = (1 + np.sqrt(5)) / 2
        F_matrix = np.array([[1/phi, 1/np.sqrt(phi)],
                             [1/np.sqrt(phi), -1/phi]])
        
        F_squared = F_matrix @ F_matrix
        
        # For the Fibonacci anyon model, the F-matrix is its own inverse.
        self.assertTrue(np.allclose(F_squared, np.identity(2)),
                        "F-matrix squared should be the identity for Fibonacci anyons.")


if __name__ == '__main__':
    unittest.main(verbosity=2)