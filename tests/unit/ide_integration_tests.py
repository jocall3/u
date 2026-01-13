import unittest
import os
import sys
import random
import numpy as np

# Assuming the existence of a quantum IDE integration module
# and a quantum simulation module.  These are placeholders.
# In a real project, these would be imported from your project's modules.

# Placeholder for quantum IDE integration
class QuantumIDEIntegration:
    def __init__(self):
        pass

    def perform_tomography(self, code_snippet):
        """Simulates quantum tomography on a code snippet."""
        # Simulate tomography results (replace with actual implementation)
        return {"qubit_0": {"state": "0", "fidelity": 0.95}, "qubit_1": {"state": "1", "fidelity": 0.98}}

    def highlight_syntax(self, code_snippet, tomography_results):
        """Simulates dynamic syntax highlighting based on tomography."""
        # Simulate highlighting (replace with actual implementation)
        highlighted_code = f"// Highlighted: {code_snippet} - Tomography Results: {tomography_results}"
        return highlighted_code

# Placeholder for quantum simulation
class QuantumSimulator:
    def __init__(self):
        pass

    def simulate_circuit(self, circuit_description):
        """Simulates a quantum circuit."""
        # Simulate circuit execution (replace with actual implementation)
        return {"outcome": "00", "probability": 0.5}


class IDEIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.ide = QuantumIDEIntegration()
        self.simulator = QuantumSimulator()

    def test_real_time_tomography(self):
        """Tests real-time quantum tomography functionality."""
        code_snippet = "H q[0]; CNOT q[0], q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)
        self.assertTrue(all(key in tomography_results for key in ["qubit_0", "qubit_1"]))
        self.assertTrue(all(isinstance(val, dict) for val in tomography_results.values()))
        self.assertTrue(all(key in tomography_results[qubit] for qubit in tomography_results for key in ["state", "fidelity"]))
        self.assertTrue(all(isinstance(tomography_results[qubit]["fidelity"], float) for qubit in tomography_results))


    def test_dynamic_syntax_highlighting(self):
        """Tests dynamic syntax highlighting based on tomography results."""
        code_snippet = "X q[0]; Z q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_tomography_with_different_code(self):
        """Tests tomography with a different code snippet."""
        code_snippet = "Rz(pi/2) q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_different_results(self):
        """Tests highlighting with different tomography results."""
        code_snippet = "CNOT q[0], q[1];"
        tomography_results = {"qubit_0": {"state": "1", "fidelity": 0.8}, "qubit_1": {"state": "0", "fidelity": 0.7}}
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_circuit_simulation_integration(self):
        """Tests integration with a quantum simulator."""
        circuit_description = "H q[0]; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_fidelity_range(self):
        """Tests that fidelity values are within a valid range."""
        code_snippet = "H q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        for qubit_data in tomography_results.values():
            self.assertTrue(0 <= qubit_data["fidelity"] <= 1)


    def test_syntax_highlighting_with_empty_results(self):
        """Tests syntax highlighting with empty tomography results (edge case)."""
        code_snippet = "I q[0];"
        highlighted_code = self.ide.highlight_syntax(code_snippet, {})
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_tomography_with_long_code(self):
        """Tests tomography with a longer code snippet."""
        code_snippet = "H q[0]; CNOT q[0], q[1]; X q[1]; Measure q[0]; Measure q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_complex_code(self):
        """Tests highlighting with a more complex code snippet."""
        code_snippet = "Rx(pi/4) q[0]; Ry(pi/2) q[1]; CNOT q[0], q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_circuit_simulation_with_multiple_qubits(self):
        """Tests circuit simulation with multiple qubits."""
        circuit_description = "H q[0]; H q[1]; CNOT q[0], q[1]; Measure q[0]; Measure q[1];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_invalid_code(self):
        """Tests tomography with potentially invalid code (error handling)."""
        code_snippet = "INVALID_GATE q[0];"
        try:
            tomography_results = self.ide.perform_tomography(code_snippet)
            self.assertIsInstance(tomography_results, dict) # Expecting a valid result, even if it's an error report
        except Exception as e:
            self.fail(f"Tomography failed with invalid code: {e}")


    def test_highlighting_with_invalid_code(self):
        """Tests highlighting with potentially invalid code."""
        code_snippet = "INVALID_GATE q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_error_handling(self):
        """Tests simulation with potential error handling."""
        circuit_description = "INVALID_CIRCUIT;"
        try:
            simulation_result = self.simulator.simulate_circuit(circuit_description)
            self.assertIsInstance(simulation_result, dict) # Expecting a valid result, even if it's an error report
        except Exception as e:
            self.fail(f"Simulation failed with invalid circuit: {e}")


    def test_tomography_with_random_code(self):
        """Tests tomography with randomly generated code snippets."""
        gates = ["H", "X", "Z", "CNOT", "Rx(pi/2)", "Ry(pi/4)"]
        num_gates = random.randint(1, 5)
        code_snippet = "; ".join([f"{random.choice(gates)} q[{random.randint(0, 1)}]" for _ in range(num_gates)]) + ";"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_random_results(self):
        """Tests highlighting with randomly generated tomography results."""
        code_snippet = "H q[0]; CNOT q[0], q[1];"
        num_qubits = random.randint(1, 3)
        tomography_results = {f"qubit_{i}": {"state": str(random.randint(0, 1)), "fidelity": random.uniform(0.5, 1.0)} for i in range(num_qubits)}
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_random_circuits(self):
        """Tests simulation with randomly generated circuits."""
        gates = ["H", "X", "Z", "CNOT"]
        num_gates = random.randint(1, 5)
        circuit_description = "; ".join([f"{random.choice(gates)} q[{random.randint(0, 1)}]" for _ in range(num_gates)]) + "; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_large_code_snippet(self):
        """Tests tomography with a very long code snippet."""
        gates = ["H", "X", "Z", "CNOT", "Rx(pi/2)", "Ry(pi/4)"]
        num_gates = 20
        code_snippet = "; ".join([f"{random.choice(gates)} q[{random.randint(0, 1)}]" for _ in range(num_gates)]) + ";"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_large_results(self):
        """Tests highlighting with a large number of qubits in the results."""
        code_snippet = "H q[0]; CNOT q[0], q[1];"
        num_qubits = 5
        tomography_results = {f"qubit_{i}": {"state": str(random.randint(0, 1)), "fidelity": random.uniform(0.5, 1.0)} for i in range(num_qubits)}
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_complex_circuits(self):
        """Tests simulation with a more complex circuit description."""
        circuit_description = "H q[0]; CNOT q[0], q[1]; X q[1]; Measure q[0]; Measure q[1];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_parameterized_gates(self):
        """Tests tomography with parameterized gates."""
        code_snippet = "Rx(pi/3) q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_parameterized_gates(self):
        """Tests highlighting with parameterized gates."""
        code_snippet = "Ry(pi/6) q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_parameterized_gates(self):
        """Tests simulation with parameterized gates."""
        circuit_description = "Rz(pi/4) q[0]; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_multiple_lines(self):
        """Tests tomography with code spanning multiple lines."""
        code_snippet = "H q[0];\nCNOT q[0], q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_multiple_lines(self):
        """Tests highlighting with code spanning multiple lines."""
        code_snippet = "X q[0];\nZ q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_multiple_lines(self):
        """Tests simulation with a circuit description spanning multiple lines."""
        circuit_description = "H q[0];\nMeasure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_comments(self):
        """Tests tomography with comments in the code."""
        code_snippet = "H q[0]; // Apply Hadamard gate"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_comments(self):
        """Tests highlighting with comments in the code."""
        code_snippet = "X q[0]; // Apply Pauli-X gate"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_comments(self):
        """Tests simulation with comments in the circuit description."""
        circuit_description = "H q[0]; // Apply Hadamard gate\nMeasure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_whitespace(self):
        """Tests tomography with extra whitespace in the code."""
        code_snippet = "  H   q[0]  ;  "
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_whitespace(self):
        """Tests highlighting with extra whitespace in the code."""
        code_snippet = "  X   q[0]  ;  "
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_whitespace(self):
        """Tests simulation with extra whitespace in the circuit description."""
        circuit_description = "  H   q[0]  ;  Measure   q[0]  ;  "
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_nested_gates(self):
        """Tests tomography with nested gates (if supported)."""
        # Assuming a hypothetical nested gate structure
        code_snippet = "Controlled(H q[0], q[1]);"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_nested_gates(self):
        """Tests highlighting with nested gates."""
        code_snippet = "Controlled(X q[0], q[1]);"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_nested_gates(self):
        """Tests simulation with nested gates."""
        circuit_description = "Controlled(H q[0], q[1]); Measure q[0]; Measure q[1];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_conditional_gates(self):
        """Tests tomography with conditional gates (if supported)."""
        # Assuming a hypothetical conditional gate structure
        code_snippet = "If(q[0] == 1, X q[1]);"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_conditional_gates(self):
        """Tests highlighting with conditional gates."""
        code_snippet = "If(q[0] == 1, Z q[1]);"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_conditional_gates(self):
        """Tests simulation with conditional gates."""
        circuit_description = "If(q[0] == 1, H q[1]); Measure q[0]; Measure q[1];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_custom_gates(self):
        """Tests tomography with custom defined gates (if supported)."""
        # Assuming a hypothetical custom gate definition
        code_snippet = "CustomGate MyGate q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_custom_gates(self):
        """Tests highlighting with custom gates."""
        code_snippet = "CustomGate MyGate q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_custom_gates(self):
        """Tests simulation with custom gates."""
        circuit_description = "CustomGate MyGate q[0]; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_multiple_qubit_operations(self):
        """Tests tomography with operations affecting multiple qubits at once (if supported)."""
        code_snippet = "MultiQubitGate q[0], q[1], q[2];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_multiple_qubit_operations(self):
        """Tests highlighting with operations affecting multiple qubits."""
        code_snippet = "MultiQubitGate q[1], q[2], q[3];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_multiple_qubit_operations(self):
        """Tests simulation with operations affecting multiple qubits."""
        circuit_description = "MultiQubitGate q[0], q[1], q[2]; Measure q[0]; Measure q[1]; Measure q[2];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_complex_parameter_expressions(self):
        """Tests tomography with complex parameter expressions."""
        code_snippet = "Rx(pi/2 + theta) q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_complex_parameter_expressions(self):
        """Tests highlighting with complex parameter expressions."""
        code_snippet = "Ry(2*theta) q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_complex_parameter_expressions(self):
        """Tests simulation with complex parameter expressions."""
        circuit_description = "Rz(theta/2) q[0]; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_variable_declarations(self):
        """Tests tomography with variable declarations (if supported)."""
        code_snippet = "theta = pi/4; Rx(theta) q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_variable_declarations(self):
        """Tests highlighting with variable declarations."""
        code_snippet = "phi = pi/2; Ry(phi) q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_variable_declarations(self):
        """Tests simulation with variable declarations."""
        circuit_description = "alpha = pi/3; Rz(alpha) q[0]; Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_control_flow(self):
        """Tests tomography with control flow statements (if supported)."""
        code_snippet = "if (condition) { H q[0]; }"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_control_flow(self):
        """Tests highlighting with control flow statements."""
        code_snippet = "if (condition) { X q[1]; }"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_control_flow(self):
        """Tests simulation with control flow statements."""
        circuit_description = "if (condition) { H q[0]; } Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_loops(self):
        """Tests tomography with loop structures (if supported)."""
        code_snippet = "for i in range(2) { H q[0]; }"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_loops(self):
        """Tests highlighting with loop structures."""
        code_snippet = "for j in range(3) { X q[1]; }"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_loops(self):
        """Tests simulation with loop structures."""
        circuit_description = "for k in range(2) { H q[0]; } Measure q[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_quantum_registers(self):
        """Tests tomography with quantum registers (if supported)."""
        code_snippet = "qreg q[2]; H q[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_quantum_registers(self):
        """Tests highlighting with quantum registers."""
        code_snippet = "qreg q[3]; X q[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_quantum_registers(self):
        """Tests simulation with quantum registers."""
        circuit_description = "qreg q[2]; H q[0]; Measure q[0]; Measure q[1];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_classical_registers(self):
        """Tests tomography with classical registers (if supported)."""
        code_snippet = "creg c[1]; H q[0]; measure q[0] -> c[0];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        self.assertIsInstance(tomography_results, dict)


    def test_highlighting_with_classical_registers(self):
        """Tests highlighting with classical registers."""
        code_snippet = "creg c[2]; X q[1]; measure q[1] -> c[1];"
        tomography_results = self.ide.perform_tomography(code_snippet)
        highlighted_code = self.ide.highlight_syntax(code_snippet, tomography_results)
        self.assertIsInstance(highlighted_code, str)
        self.assertTrue("// Highlighted:" in highlighted_code)
        self.assertTrue("Tomography Results:" in highlighted_code)


    def test_simulation_with_classical_registers(self):
        """Tests simulation with classical registers."""
        circuit_description = "creg c[1]; H q[0]; measure q[0] -> c[0];"
        simulation_result = self.simulator.simulate_circuit(circuit_description)
        self.assertIsInstance(simulation_result, dict)
        self.assertTrue("outcome" in simulation_result)
        self.assertTrue("probability" in simulation_result)


    def test_tomography_with_multiple_registers(self):
        """Tests tomography