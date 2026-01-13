import unittest
from quantum_lambda import QuantumLambdaExpression, QuantumVariable, QuantumAbstraction, QuantumApplication, QuantumState, QuantumOperator

class QuantumLambdaCalculusTests(unittest.TestCase):

    def test_quantum_variable_creation(self):
        x = QuantumVariable("x")
        self.assertEqual(x.name, "x")

    def test_quantum_abstraction_creation(self):
        x = QuantumVariable("x")
        body = QuantumVariable("y")
        abstraction = QuantumAbstraction(x, body)
        self.assertEqual(abstraction.variable.name, "x")
        self.assertEqual(abstraction.body.name, "y")

    def test_quantum_application_creation(self):
        func = QuantumVariable("f")
        arg = QuantumVariable("x")
        application = QuantumApplication(func, arg)
        self.assertEqual(application.func.name, "f")
        self.assertEqual(application.arg.name, "x")

    def test_quantum_state_creation(self):
        state = QuantumState({QuantumVariable("x"): 0.7, QuantumVariable("y"): 0.3})
        self.assertAlmostEqual(state.probabilities[QuantumVariable("x")], 0.7)
        self.assertAlmostEqual(state.probabilities[QuantumVariable("y")], 0.3)

    def test_quantum_operator_creation(self):
        operator = QuantumOperator({QuantumVariable("x"): QuantumVariable("y"), QuantumVariable("y"): QuantumVariable("x")})
        self.assertEqual(operator.mapping[QuantumVariable("x")], QuantumVariable("y"))
        self.assertEqual(operator.mapping[QuantumVariable("y")], QuantumVariable("x"))

    def test_quantum_variable_representation(self):
        x = QuantumVariable("x")
        self.assertEqual(str(x), "x")

    def test_quantum_abstraction_representation(self):
        x = QuantumVariable("x")
        body = QuantumVariable("y")
        abstraction = QuantumAbstraction(x, body)
        self.assertEqual(str(abstraction), "(λx.y)")

    def test_quantum_application_representation(self):
        func = QuantumVariable("f")
        arg = QuantumVariable("x")
        application = QuantumApplication(func, arg)
        self.assertEqual(str(application), "(f x)")

    def test_quantum_state_representation(self):
        state = QuantumState({QuantumVariable("x"): 0.7, QuantumVariable("y"): 0.3})
        self.assertTrue("{x: 0.7, y: 0.3}" in str(state)) # Order might vary

    def test_quantum_operator_representation(self):
        operator = QuantumOperator({QuantumVariable("x"): QuantumVariable("y"), QuantumVariable("y"): QuantumVariable("x")})
        self.assertTrue("{x: y, y: x}" in str(operator)) # Order might vary

    def test_quantum_application_evaluation_simple(self):
        # (λx.x) y  -> y
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        identity = QuantumAbstraction(x, x)
        application = QuantumApplication(identity, y)
        result = application.evaluate()
        self.assertEqual(result, y)

    def test_quantum_application_evaluation_complex(self):
        # (λx.(λy.x)) z -> (λy.z)
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        z = QuantumVariable("z")
        inner_abstraction = QuantumAbstraction(y, x)
        outer_abstraction = QuantumAbstraction(x, inner_abstraction)
        application = QuantumApplication(outer_abstraction, z)
        result = application.evaluate()
        self.assertEqual(str(result), "(λy.z)")

    def test_quantum_state_application(self):
        # Apply a simple operator to a state
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        state = QuantumState({x: 0.6, y: 0.4})
        operator = QuantumOperator({x: y, y: x})
        new_state = state.apply_operator(operator)
        self.assertAlmostEqual(new_state.probabilities[x], 0.4)
        self.assertAlmostEqual(new_state.probabilities[y], 0.6)

    def test_quantum_state_normalization(self):
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        state = QuantumState({x: 0.3, y: 0.2})
        normalized_state = state.normalize()
        total_probability = sum(normalized_state.probabilities.values())
        self.assertAlmostEqual(total_probability, 1.0)
        self.assertAlmostEqual(normalized_state.probabilities[x], 0.6)
        self.assertAlmostEqual(normalized_state.probabilities[y], 0.4)

    def test_quantum_application_with_state(self):
        # (λx.x) applied to a superposition of x and y
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        identity = QuantumAbstraction(x, x)
        initial_state = QuantumState({x: 0.8, y: 0.2})
        application = QuantumApplication(identity, initial_state)
        result = application.evaluate()
        self.assertIsInstance(result, QuantumState)
        self.assertAlmostEqual(result.probabilities[x], 0.8)
        self.assertAlmostEqual(result.probabilities[y], 0.2)

    def test_quantum_application_with_operator(self):
        # (λx.x) applied to an operator that swaps x and y
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        identity = QuantumAbstraction(x, x)
        swap_operator = QuantumOperator({x: y, y: x})
        application = QuantumApplication(identity, swap_operator)
        result = application.evaluate()
        self.assertIsInstance(result, QuantumOperator)
        self.assertEqual(result.mapping[x], y)
        self.assertEqual(result.mapping[y], x)

    def test_quantum_application_complex_state_manipulation(self):
        # (λf.(f x)) (λy.y) applied to a state where x is in superposition
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        f = QuantumVariable("f")
        identity = QuantumAbstraction(y, y)
        application = QuantumApplication(f, x)
        outer_abstraction = QuantumAbstraction(f, application)
        initial_state = QuantumState({x: 0.7, y: 0.3})
        full_application = QuantumApplication(outer_abstraction, identity)
        result = full_application.evaluate()
        self.assertEqual(str(result), "x") # Should return x, but x is in a state

    def test_quantum_beta_reduction(self):
        # (λx.x) y -> y
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        identity = QuantumAbstraction(x, x)
        result = identity.beta_reduce(y)
        self.assertEqual(result, y)

    def test_quantum_beta_reduction_complex(self):
        # (λx.(λy.x)) z -> (λy.z)
        x = QuantumVariable("x")
        y = QuantumVariable("y")
        z = QuantumVariable("z")
        inner_abstraction = QuantumAbstraction(y, x)
        outer_abstraction = QuantumAbstraction(x, inner_abstraction)
        result = outer_abstraction.beta_reduce(z)
        self.assertEqual(str(result), "(λy.z)")

if __name__ == '__main__':
    unittest.main()