import unittest
import random
import operator
from unittest.mock import patch

# Mocking the entangled global variables (for testing purposes)
class MockEntangledGlobals:
    def __init__(self):
        self.state = {}

    def set_state(self, key, value):
        self.state[key] = value

    def get_state(self, key):
        return self.state.get(key)

# A simple class to demonstrate operator overloading
class QuantumObject:
    def __init__(self, value, entangled_globals):
        self.value = value
        self.entangled_globals = entangled_globals

    def __add__(self, other):
        if isinstance(other, QuantumObject):
            # Dynamic meaning based on entangled global state
            operation_mode = self.entangled_globals.get_state("addition_mode")
            if operation_mode == "inverse":
                return QuantumObject(self.value - other.value, self.entangled_globals)
            elif operation_mode == "complex":
                return QuantumObject(complex(self.value, other.value), self.entangled_globals)
            else:  # Default: standard addition
                return QuantumObject(self.value + other.value, self.entangled_globals)
        else:
            return QuantumObject(self.value + other, self.entangled_globals)

    def __sub__(self, other):
        if isinstance(other, QuantumObject):
            operation_mode = self.entangled_globals.get_state("subtraction_mode")
            if operation_mode == "absolute":
                return QuantumObject(abs(self.value - other.value), self.entangled_globals)
            elif operation_mode == "squared":
                return QuantumObject((self.value - other.value)**2, self.entangled_globals)
            else:
                return QuantumObject(self.value - other.value, self.entangled_globals)
        else:
            return QuantumObject(self.value - other, self.entangled_globals)

    def __mul__(self, other):
        if isinstance(other, QuantumObject):
            operation_mode = self.entangled_globals.get_state("multiplication_mode")
            if operation_mode == "quantum_entanglement":
                # Simulate entanglement: value becomes average
                avg = (self.value + other.value) / 2
                return QuantumObject(avg, self.entangled_globals)
            elif operation_mode == "tensor_product":
                return QuantumObject(self.value * other.value * random.random(), self.entangled_globals)
            else:
                return QuantumObject(self.value * other.value, self.entangled_globals)
        else:
            return QuantumObject(self.value * other, self.entangled_globals)

    def __truediv__(self, other):
        if isinstance(other, QuantumObject):
            operation_mode = self.entangled_globals.get_state("division_mode")
            if operation_mode == "safe":
                if other.value == 0:
                    return QuantumObject(0, self.entangled_globals)  # Avoid division by zero
                return QuantumObject(self.value / other.value, self.entangled_globals)
            elif operation_mode == "reciprocal":
                if self.value == 0:
                    return QuantumObject(float('inf'), self.entangled_globals)
                return QuantumObject(other.value / self.value, self.entangled_globals)
            else:
                if other.value == 0:
                    return QuantumObject(float('inf'), self.entangled_globals)
                return QuantumObject(self.value / other.value, self.entangled_globals)
        else:
            if other == 0:
                return QuantumObject(float('inf'), self.entangled_globals)
            return QuantumObject(self.value / other, self.entangled_globals)

    def __str__(self):
        return f"QuantumObject({self.value})"

class QuantumOperatorOverloadingTests(unittest.TestCase):

    def setUp(self):
        self.entangled_globals = MockEntangledGlobals()

    def test_addition_standard(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 + obj2
        self.assertEqual(result.value, 8)

    def test_addition_inverse(self):
        self.entangled_globals.set_state("addition_mode", "inverse")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 + obj2
        self.assertEqual(result.value, 2)

    def test_addition_complex(self):
        self.entangled_globals.set_state("addition_mode", "complex")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 + obj2
        self.assertEqual(result.value, complex(5, 3))

    def test_subtraction_standard(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 - obj2
        self.assertEqual(result.value, 2)

    def test_subtraction_absolute(self):
        self.entangled_globals.set_state("subtraction_mode", "absolute")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 - obj2
        self.assertEqual(result.value, 2)

    def test_subtraction_squared(self):
        self.entangled_globals.set_state("subtraction_mode", "squared")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 - obj2
        self.assertEqual(result.value, 4)

    def test_multiplication_standard(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 * obj2
        self.assertEqual(result.value, 15)

    def test_multiplication_quantum_entanglement(self):
        self.entangled_globals.set_state("multiplication_mode", "quantum_entanglement")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 * obj2
        self.assertEqual(result.value, (5 + 3) / 2)

    def test_multiplication_tensor_product(self):
        self.entangled_globals.set_state("multiplication_mode", "tensor_product")
        obj1 = QuantumObject(5, self.entangled_globals)
        obj2 = QuantumObject(3, self.entangled_globals)
        result = obj1 * obj2
        self.assertAlmostEqual(result.value, 5 * 3 * random.random(), places=5)

    def test_division_standard(self):
        obj1 = QuantumObject(10, self.entangled_globals)
        obj2 = QuantumObject(2, self.entangled_globals)
        result = obj1 / obj2
        self.assertEqual(result.value, 5)

    def test_division_safe(self):
        self.entangled_globals.set_state("division_mode", "safe")
        obj1 = QuantumObject(10, self.entangled_globals)
        obj2 = QuantumObject(0, self.entangled_globals)
        result = obj1 / obj2
        self.assertEqual(result.value, 0)

        obj3 = QuantumObject(10, self.entangled_globals)
        obj4 = QuantumObject(2, self.entangled_globals)
        result2 = obj3 / obj4
        self.assertEqual(result2.value, 5)

    def test_division_reciprocal(self):
        self.entangled_globals.set_state("division_mode", "reciprocal")
        obj1 = QuantumObject(10, self.entangled_globals)
        obj2 = QuantumObject(2, self.entangled_globals)
        result = obj1 / obj2
        self.assertEqual(result.value, 2/10)

        obj3 = QuantumObject(0, self.entangled_globals)
        obj4 = QuantumObject(2, self.entangled_globals)
        result2 = obj3 / obj4
        self.assertEqual(result2.value, float('inf'))

    def test_division_by_zero(self):
        obj1 = QuantumObject(10, self.entangled_globals)
        obj2 = 0
        result = obj1 / obj2
        self.assertEqual(result.value, float('inf'))

    def test_add_with_int(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        result = obj1 + 3
        self.assertEqual(result.value, 8)

    def test_sub_with_int(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        result = obj1 - 3
        self.assertEqual(result.value, 2)

    def test_mul_with_int(self):
        obj1 = QuantumObject(5, self.entangled_globals)
        result = obj1 * 3
        self.assertEqual(result.value, 15)

    def test_truediv_with_int(self):
        obj1 = QuantumObject(10, self.entangled_globals)
        result = obj1 / 2
        self.assertEqual(result.value, 5)

if __name__ == '__main__':
    unittest.main()