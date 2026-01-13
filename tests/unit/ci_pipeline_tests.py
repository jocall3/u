import unittest
from unittest.mock import Mock, patch, call
import numpy as np

# Assume the following classes exist in a library, e.g., 'quantum_ci_lib'
# We will be testing these classes. For the purpose of this file,
# we can imagine their implementations are more complex.

# --- Start: Hypothetical library code being tested ---
# This would normally be in separate files like 'quantum_ci_lib/simulator.py'

class QuantumSimulator:
    """A placeholder for a complex quantum circuit simulator."""
    def run(self, circuit_definition: str, num_qubits: int):
        """
        Executes a quantum circuit and returns the final state vector.
        A real implementation would use a library like Qiskit, Cirq, or a custom engine.
        """
        if num_qubits == 1 and circuit_definition == "H(q0)":
            # Hadamard on |0> -> |+>
            return {"state_vector": np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)}
        if num_qubits == 1 and circuit_definition == "H(q0);H(q0)":
            # H -> H on |0> -> |0> (Interference)
            return {"state_vector": np.array([1, 0], dtype=complex)}
        if num_qubits == 2 and circuit_definition == "H(q0);CNOT(q0,q1)":
            # Bell State |Φ+>
            return {"state_vector": np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)}
        raise ValueError(f"Unsupported circuit definition: {circuit_definition}")

class DestructiveInterferenceDetector:
    """A placeholder for an advanced quantum state analysis engine."""
    def analyze(self, initial_state: np.ndarray, final_state: np.ndarray, tolerance=1e-9):
        """
        Analyzes if destructive interference likely occurred to return to a basis state.
        This is a simplified heuristic.
        """
        # Check if final state is a computational basis state (e.g., |0>, |1>, |00>, etc.)
        is_final_basis = np.sum(np.isclose(np.abs(final_state)**2, 1.0, atol=tolerance)) == 1
        
        # Check if initial state was NOT a basis state (i.e., was in superposition)
        is_initial_superposition = np.sum(np.isclose(np.abs(initial_state)**2, 1.0, atol=tolerance)) != 1

        if is_final_basis and is_initial_superposition:
            return {"interference_detected": True, "confidence": 0.99}
        
        return {"interference_detected": False, "confidence": 0.1}

class QuantumCIPipeline:
    """Orchestrates quantum simulation and analysis stages."""
    def __init__(self, simulator: QuantumSimulator, analyzer: DestructiveInterferenceDetector):
        self.simulator = simulator
        self.analyzer = analyzer
        self.log = []

    def run_check(self, name: str, circuit: str, num_qubits: int):
        """
        Runs a full check, including simulation and interference analysis.
        """
        self.log.append(f"START: Running check '{name}'")
        try:
            # Define initial state |0...0>
            initial_state = np.zeros(2**num_qubits, dtype=complex)
            initial_state[0] = 1.0

            # Stage 1: Simulation
            self.log.append(f"Executing quantum simulation for circuit: {circuit}")
            sim_result = self.simulator.run(circuit, num_qubits)
            final_state = sim_result.get("state_vector")
            if final_state is None:
                raise RuntimeError("Simulator did not return a state_vector.")

            # Stage 2: Analysis
            # For this example, we'll analyze against a hypothetical intermediate superposition state
            # A real pipeline might have more complex logic to determine the 'before' state.
            intermediate_state_for_analysis = np.full(2**num_qubits, 1/np.sqrt(2**num_qubits), dtype=complex)

            self.log.append("Analyzing final quantum state for destructive interference.")
            analysis_result = self.analyzer.analyze(intermediate_state_for_analysis, final_state)

            self.log.append(f"FINISH: Check '{name}' completed successfully.")
            return {
                "status": "SUCCESS",
                "check_name": name,
                "simulation_output": sim_result,
                "analysis_output": analysis_result
            }
        except Exception as e:
            self.log.append(f"ERROR: Check '{name}' failed: {e}")
            return {
                "status": "FAILURE",
                "check_name": name,
                "error_message": str(e)
            }

# --- End: Hypothetical library code being tested ---


class TestQuantumCIPipelineExecution(unittest.TestCase):
    """
    Unit tests for the QuantumCIPipeline, focusing on orchestration and error handling.
    Dependencies (Simulator, Analyzer) are mocked to isolate the pipeline logic.
    """

    def setUp(self):
        """Set up mock components for each test."""
        self.mock_simulator = Mock(spec=QuantumSimulator)
        self.mock_analyzer = Mock(spec=DestructiveInterferenceDetector)
        self.pipeline = QuantumCIPipeline(self.mock_simulator, self.mock_analyzer)

    def test_pipeline_orchestrates_simulation_and_analysis_successfully(self):
        """
        Verify the pipeline calls the simulator and then the analyzer in the correct sequence.
        """
        # Configure mocks to return predictable results
        test_circuit = "H(q0);CNOT(q0,q1)"
        num_qubits = 2
        simulated_state = {"state_vector": np.array([0.707, 0, 0, 0.707], dtype=complex)}
        analysis_report = {"interference_detected": False, "confidence": 0.15}

        self.mock_simulator.run.return_value = simulated_state
        self.mock_analyzer.analyze.return_value = analysis_report

        # Execute the pipeline
        result = self.pipeline.run_check("BellStateCheck", test_circuit, num_qubits)

        # Assertions
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["check_name"], "BellStateCheck")
        
        # Verify simulator was called correctly
        self.mock_simulator.run.assert_called_once_with(test_circuit, num_qubits)

        # Verify analyzer was called with the output of the simulator
        # The 'intermediate_state' is hardcoded in the pipeline for this example
        expected_intermediate_state = np.full(4, 1/np.sqrt(4), dtype=complex)
        
        # Use np.testing.assert_array_equal for numpy array comparison
        call_args, _ = self.mock_analyzer.analyze.call_args
        np.testing.assert_array_almost_equal(call_args[0], expected_intermediate_state)
        np.testing.assert_array_almost_equal(call_args[1], simulated_state["state_vector"])
        
        self.assertEqual(result["simulation_output"], simulated_state)
        self.assertEqual(result["analysis_output"], analysis_report)
        self.assertIn("FINISH: Check 'BellStateCheck' completed successfully.", self.pipeline.log)

    def test_pipeline_handles_simulation_failure_gracefully(self):
        """
        Ensure the pipeline returns a 'FAILURE' status if the simulator raises an exception.
        """
        # Configure the mock simulator to raise an error
        error_message = "Quantum singularity detected in sector 7G."
        self.mock_simulator.run.side_effect = ValueError(error_message)

        # Execute the pipeline
        result = self.pipeline.run_check("RiskyExperiment", "INVALID_GATE", 1)

        # Assertions
        self.assertEqual(result["status"], "FAILURE")
        self.assertEqual(result["error_message"], error_message)
        
        # Ensure the analyzer was never called
        self.mock_analyzer.analyze.assert_not_called()
        self.assertIn(f"ERROR: Check 'RiskyExperiment' failed: {error_message}", self.pipeline.log)

    def test_pipeline_handles_missing_state_vector_from_simulator(self):
        """
        Verify the pipeline fails if the simulator returns an invalid dictionary.
        """
        # Configure mock to return a malformed result
        self.mock_simulator.run.return_value = {"measurements": {"0": 1024}} # Missing 'state_vector'

        # Execute
        result = self.pipeline.run_check("MalformedOutputCheck", "H(q0)", 1)

        # Assertions
        self.assertEqual(result["status"], "FAILURE")
        self.assertIn("Simulator did not return a state_vector.", result["error_message"])
        self.mock_analyzer.analyze.assert_not_called()

    def test_pipeline_correctly_reports_detected_interference(self):
        """
        Test the end-to-end flow where the analyzer reports positive interference detection.
        """
        # Configure mocks
        simulated_state = {"state_vector": np.array([1, 0], dtype=complex)} # |0> state
        analysis_report = {"interference_detected": True, "confidence": 0.99}
        self.mock_simulator.run.return_value = simulated_state
        self.mock_analyzer.analyze.return_value = analysis_report

        # Execute
        result = self.pipeline.run_check("InterferenceTest", "H(q0);H(q0)", 1)

        # Assertions
        self.assertEqual(result["status"], "SUCCESS")
        self.assertTrue(result["analysis_output"]["interference_detected"])
        self.assertGreater(result["analysis_output"]["confidence"], 0.9)


class TestQuantumComponentIntegration(unittest.TestCase):
    """
    Integration-style tests for the quantum components, using their actual implementations.
    This verifies the components work together as expected without mocking.
    """

    def setUp(self):
        """Instantiate real components for integration testing."""
        self.simulator = QuantumSimulator()
        self.analyzer = DestructiveInterferenceDetector()
        self.pipeline = QuantumCIPipeline(self.simulator, self.analyzer)

    def test_hadamard_gate_creates_correct_superposition(self):
        """
        Verify the simulator produces the correct state vector for a single Hadamard gate.
        """
        result = self.simulator.run("H(q0)", num_qubits=1)
        state_vector = result["state_vector"]
        expected_vector = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        np.testing.assert_array_almost_equal(state_vector, expected_vector)

    def test_bell_state_circuit_creates_entanglement(self):
        """
        Verify the simulator produces the correct entangled Bell state.
        """
        result = self.simulator.run("H(q0);CNOT(q0,q1)", num_qubits=2)
        state_vector = result["state_vector"]
        expected_vector = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        np.testing.assert_array_almost_equal(state_vector, expected_vector)

    def test_analyzer_identifies_destructive_interference(self):
        """
        Verify the analyzer correctly detects interference when a superposition collapses to a basis state.
        """
        # State before interference (e.g., after one H gate)
        initial_superposition = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        # State after interference (e.g., after a second H gate)
        final_basis_state = np.array([1, 0], dtype=complex)

        result = self.analyzer.analyze(initial_superposition, final_basis_state)
        self.assertTrue(result["interference_detected"])
        self.assertGreater(result["confidence"], 0.9)

    def test_analyzer_ignores_superposition_to_superposition(self):
        """
        Verify the analyzer does not flag interference for transitions between superpositions.
        """
        initial_superposition = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        # A different superposition state (e.g., after a phase shift)
        final_superposition = np.array([1/np.sqrt(2), -1/np.sqrt(2)], dtype=complex)

        result = self.analyzer.analyze(initial_superposition, final_superposition)
        self.assertFalse(result["interference_detected"])

    def test_full_pipeline_run_detects_interference_in_h_h_circuit(self):
        """
        An end-to-end test verifying the pipeline correctly processes a circuit
        that is known to exhibit destructive interference.
        """
        # The H-H circuit on |0> returns the state to |0>.
        # The analyzer should detect this return to a basis state.
        result = self.pipeline.run_check("DoubleHadamardInterference", "H(q0);H(q0)", 1)

        self.assertEqual(result["status"], "SUCCESS")
        
        # Check simulation output
        final_state = result["simulation_output"]["state_vector"]
        expected_state = np.array([1, 0], dtype=complex)
        np.testing.assert_array_almost_equal(final_state, expected_state)

        # Check analysis output
        analysis = result["analysis_output"]
        self.assertTrue(analysis["interference_detected"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)