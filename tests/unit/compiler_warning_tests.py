import unittest
from unittest.mock import patch

# Placeholder for the actual zero-knowledge compiler.  Replace with real implementation.
class MockZeroKnowledgeCompiler:
    def __init__(self):
        self.warnings = []

    def compile(self, code):
        # Simulate some warnings based on the code.
        if "print(" in code:
            self.warnings.append("Warning: Classical output detected. May compromise zero-knowledge.")
        if "measure(" in code and "discard(" not in code:
            self.warnings.append("Warning: Measurement without immediate discard. Information leakage possible.")
        return "Compiled code", self.warnings

class CompilerWarningTests(unittest.TestCase):

    def setUp(self):
        self.compiler = MockZeroKnowledgeCompiler()

    def test_no_warnings(self):
        code = """
        # Some zero-knowledge code
        a = secret_input()
        b = secret_input()
        c = a + b
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 0)

    def test_classical_output_warning(self):
        code = """
        a = secret_input()
        print(a) # Classical output
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertIn("Classical output detected", warnings[0])

    def test_measurement_without_discard_warning(self):
        code = """
        q = qubit()
        measure(q) # Measurement without discard
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertIn("Measurement without immediate discard", warnings[0])

    def test_measurement_with_discard_no_warning(self):
        code = """
        q = qubit()
        result = measure(q)
        discard(q)
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 0)

    def test_multiple_warnings(self):
        code = """
        a = secret_input()
        print(a)
        q = qubit()
        measure(q)
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 2)
        self.assertIn("Classical output detected", warnings)
        self.assertIn("Measurement without immediate discard", warnings)

    def test_empty_code(self):
        code = ""
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 0)

    def test_comment_with_print(self):
        code = """
        # This is a comment with print(something)
        a = secret_input()
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 0)

    def test_comment_with_measure(self):
        code = """
        # This is a comment with measure(something)
        q = qubit()
        """
        compiled_code, warnings = self.compiler.compile(code)
        self.assertEqual(len(warnings), 0)

if __name__ == '__main__':
    unittest.main()