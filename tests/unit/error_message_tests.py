import unittest
from superdense_coding import SuperdenseCoding

class ErrorMessageTests(unittest.TestCase):

    def setUp(self):
        self.superdense_coding = SuperdenseCoding()

    def test_invalid_alice_input_type(self):
        with self.assertRaises(TypeError) as context:
            self.superdense_coding.encode_message(123, "Bob")
        self.assertTrue("Alice's input must be a string" in str(context.exception))

    def test_invalid_bob_input_type(self):
        with self.assertRaises(TypeError) as context:
            self.superdense_coding.encode_message("Alice", 456)
        self.assertTrue("Bob's input must be a string" in str(context.exception))

    def test_invalid_alice_input_length(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.encode_message("TooLongAlice", "Bob")
        self.assertTrue("Alice's input must be a single character" in str(context.exception))

    def test_invalid_bob_input_length(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.encode_message("Alice", "TooLongBob")
        self.assertTrue("Bob's input must be a single character" in str(context.exception))

    def test_invalid_alice_input_value(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.encode_message("X", "Bob")
        self.assertTrue("Alice's input must be '0' or '1'" in str(context.exception))

    def test_invalid_bob_input_value(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.encode_message("Alice", "Y")
        self.assertTrue("Bob's input must be '0' or '1'" in str(context.exception))

    def test_decode_invalid_qubit_state_type(self):
        with self.assertRaises(TypeError) as context:
            self.superdense_coding.decode_message(123)
        self.assertTrue("Qubit state must be a string" in str(context.exception))

    def test_decode_invalid_qubit_state_length(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.decode_message("TooLongQubitState")
        self.assertTrue("Qubit state must be two characters long" in str(context.exception))

    def test_decode_invalid_qubit_state_value(self):
        with self.assertRaises(ValueError) as context:
            self.superdense_coding.decode_message("XY")
        self.assertTrue("Qubit state must be '00', '01', '10', or '11'" in str(context.exception))

if __name__ == '__main__':
    unittest.main()