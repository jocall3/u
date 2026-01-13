import random
import ast
import unittest

class QASTRobustnessChecker:
    """
    A class to check the robustness of a QAST (Quantum Abstract Syntax Tree)
    after mutation. It verifies program stability and correctness.
    """

    def __init__(self, original_source_code: str, mutated_source_code: str, test_cases: list):
        """
        Initializes the QASTRobustnessChecker with the original and mutated source code,
        and a list of test cases.

        Args:
            original_source_code: The original source code as a string.
            mutated_source_code: The mutated source code as a string.
            test_cases: A list of test cases to run against both versions.
        """
        self.original_source_code = original_source_code
        self.mutated_source_code = mutated_source_code
        self.test_cases = test_cases

    def parse_code(self, source_code: str) -> ast.AST:
        """
        Parses the given source code into an AST.

        Args:
            source_code: The source code to parse.

        Returns:
            The AST representation of the source code.

        Raises:
            SyntaxError: If the source code contains syntax errors.
        """
        try:
            return ast.parse(source_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in code: {e}")

    def execute_code(self, source_code: str, test_case: dict) -> any:
        """
        Executes the given source code with the provided test case.

        Args:
            source_code: The source code to execute.
            test_case: A dictionary containing input values for the code.

        Returns:
            The output of the code execution.  Returns None if execution fails.
        """
        try:
            # Create a local namespace for execution
            local_namespace = {}
            # Execute the code in the local namespace
            exec(source_code, local_namespace)

            # Find the main function (assuming it's named 'main')
            main_function = local_namespace.get("main")

            if main_function is None:
                # If no main function, try to execute the code directly
                # This is a simplified approach and might not work for all cases
                return eval(source_code, local_namespace)

            # Call the main function with the test case inputs
            input_values = test_case.get("input", {})
            if isinstance(input_values, dict):
                return main_function(**input_values)
            elif isinstance(input_values, tuple) or isinstance(input_values, list):
                return main_function(*input_values)
            else:
                return main_function(input_values)

        except Exception as e:
            print(f"Execution error: {e}")
            return None

    def check_robustness(self) -> bool:
        """
        Checks the robustness of the mutated code by comparing its output to the
        original code's output for each test case.

        Returns:
            True if the mutated code produces the same output as the original code
            for all test cases, False otherwise.
        """
        original_results = []
        mutated_results = []

        for test_case in self.test_cases:
            original_result = self.execute_code(self.original_source_code, test_case)
            mutated_result = self.execute_code(self.mutated_source_code, test_case)

            original_results.append(original_result)
            mutated_results.append(mutated_result)

        # Compare the results
        return original_results == mutated_results

    def run_tests(self) -> dict:
        """
        Runs a series of tests to evaluate the robustness of the mutated code.

        Returns:
            A dictionary containing the test results.
        """
        results = {}
        for i, test_case in enumerate(self.test_cases):
            test_name = f"Test Case {i+1}"
            try:
                original_result = self.execute_code(self.original_source_code, test_case)
                mutated_result = self.execute_code(self.mutated_source_code, test_case)

                results[test_name] = {
                    "original_result": original_result,
                    "mutated_result": mutated_result,
                    "passed": original_result == mutated_result
                }
            except Exception as e:
                results[test_name] = {
                    "error": str(e),
                    "passed": False
                }
        return results

class TestQASTRobustnessChecker(unittest.TestCase):
    def test_robustness_checker(self):
        original_code = """
def main(x):
    return x + 1
"""
        mutated_code = """
def main(x):
    return x + 2
"""
        test_cases = [
            {"input": {"x": 1}},
            {"input": {"x": 2}},
            {"input": {"x": 3}}
        ]

        checker = QASTRobustnessChecker(original_code, mutated_code, test_cases)
        results = checker.run_tests()

        for test_name, result in results.items():
            self.assertIn("original_result", result)
            self.assertIn("mutated_result", result)
            self.assertIn("passed", result)
            print(f"{test_name}: {result}")

        self.assertFalse(checker.check_robustness())

if __name__ == '__main__':
    unittest.main()