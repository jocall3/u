import unittest
import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

class TestHybridLayerMeasurement(unittest.TestCase):
    """Tests for hybrid quantum-classical layers with classical lines acting as measurement operators."""

    def setUp(self):
        """Set up test parameters and devices."""
        self.n_qubits = 2
        self.dev = qml.device("default.qubit", wires=self.n_qubits)
        self.rng = np.random.default_rng(42)  # Consistent random number generation

    def test_simple_hybrid_layer(self):
        """Test a simple hybrid layer with a classical line as a measurement."""

        def circuit(weights, x):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliX(1)), x[0] * x[1]  # Classical line as measurement

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7], requires_grad=True)
        x = pnp.array([0.2, 0.9], requires_grad=False)

        result = hybrid_qnode(weights, x)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result, tuple)

        expected_classical = x[0] * x[1]
        self.assertAlmostEqual(result[2], expected_classical)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x)
        self.assertEqual(len(grads), 2)
        self.assertIsInstance(grads, tuple)

    def test_more_complex_hybrid_layer(self):
        """Test a more complex hybrid layer with multiple classical lines and operations."""

        def circuit(weights, x):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            qml.RZ(weights[2], wires=0)
            return (
                qml.expval(qml.PauliZ(0)),
                qml.expval(qml.PauliX(1)),
                x[0] * x[1] + weights[3],  # Classical line with weight
                x[0] ** 2,  # Classical line
            )

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7, 0.2, 0.9], requires_grad=True)
        x = pnp.array([0.2, 0.9], requires_grad=False)

        result = hybrid_qnode(weights, x)
        self.assertEqual(len(result), 4)
        self.assertIsInstance(result, tuple)

        expected_classical1 = x[0] * x[1] + weights[3]
        expected_classical2 = x[0] ** 2
        self.assertAlmostEqual(result[2], expected_classical1)
        self.assertAlmostEqual(result[3], expected_classical2)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x)
        self.assertEqual(len(grads), 4)
        self.assertIsInstance(grads, tuple)

    def test_hybrid_layer_with_no_quantum_measurements(self):
        """Test a hybrid layer with only classical lines as measurements."""

        def circuit(weights, x):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            return (
                x[0] * x[1] + weights[2],  # Classical line with weight
                x[0] ** 2,  # Classical line
            )

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7, 0.9], requires_grad=True)
        x = pnp.array([0.2, 0.9], requires_grad=False)

        result = hybrid_qnode(weights, x)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, tuple)

        expected_classical1 = x[0] * x[1] + weights[2]
        expected_classical2 = x[0] ** 2
        self.assertAlmostEqual(result[0], expected_classical1)
        self.assertAlmostEqual(result[1], expected_classical2)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x)
        self.assertEqual(len(grads), 3)
        self.assertIsInstance(grads, tuple)

    def test_hybrid_layer_with_classical_processing(self):
        """Test a hybrid layer with classical processing of quantum measurements."""

        def circuit(weights, x):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            quantum_result = qml.expval(qml.PauliZ(0))
            return quantum_result * x[0] + weights[2], x[1] ** 2  # Classical processing

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7, 0.9], requires_grad=True)
        x = pnp.array([0.2, 0.9], requires_grad=False)

        result = hybrid_qnode(weights, x)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, tuple)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x)
        self.assertEqual(len(grads), 3)
        self.assertIsInstance(grads, tuple)

    def test_hybrid_layer_with_multiple_classical_inputs(self):
        """Test a hybrid layer with multiple classical inputs."""

        def circuit(weights, x, y):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            return (
                qml.expval(qml.PauliZ(0)),
                x * y + weights[2],  # Classical line with multiple inputs
            )

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7, 0.9], requires_grad=True)
        x = pnp.array(0.2, requires_grad=False)
        y = pnp.array(0.9, requires_grad=False)

        result = hybrid_qnode(weights, x, y)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, tuple)

        expected_classical = x * y + weights[2]
        self.assertAlmostEqual(result[1], expected_classical)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x, y)
        self.assertEqual(len(grads), 3)
        self.assertIsInstance(grads, tuple)

    def test_hybrid_layer_with_classical_array_input(self):
        """Test a hybrid layer with a classical array as input."""

        def circuit(weights, x):
            qml.Hadamard(wires=0)
            qml.RX(weights[0], wires=0)
            qml.CNOT(wires=[0, 1])
            qml.RY(weights[1], wires=1)
            return (
                qml.expval(qml.PauliZ(0)),
                pnp.sum(x) + weights[2],  # Classical line with array input
            )

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        weights = pnp.array([0.5, 0.7, 0.9], requires_grad=True)
        x = pnp.array([0.2, 0.9, 0.5], requires_grad=False)

        result = hybrid_qnode(weights, x)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, tuple)

        expected_classical = pnp.sum(x) + weights[2]
        self.assertAlmostEqual(result[1], expected_classical)

        # Test gradients
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(weights, x)
        self.assertEqual(len(grads), 3)
        self.assertIsInstance(grads, tuple)

    def test_hybrid_layer_with_no_weights(self):
        """Test a hybrid layer with no trainable weights."""

        def circuit(x):
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            return (
                qml.expval(qml.PauliZ(0)),
                x[0] * x[1],  # Classical line
            )

        hybrid_qnode = qml.QNode(circuit, self.dev, interface="autograd")

        x = pnp.array([0.2, 0.9], requires_grad=False)

        result = hybrid_qnode(x)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, tuple)

        expected_classical = x[0] * x[1]
        self.assertAlmostEqual(result[1], expected_classical)

        # Test gradients (should be empty)
        grad_fn = qml.grad(hybrid_qnode, argnum=0)
        grads = grad_fn(x)
        self.assertEqual(len(grads), 0)
        self.assertIsInstance(grads, tuple)

if __name__ == '__main__':
    unittest.main()