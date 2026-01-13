import ast
import hashlib
import os

class CloningProhibitionEnforcer:
    """
    Enforces a prohibition on code cloning within a project.
    Detects and penalizes direct code duplication attempts.
    """

    def __init__(self, project_root, threshold=0.9, penalty_function=None):
        """
        Initializes the CloningProhibitionEnforcer.

        Args:
            project_root (str): The root directory of the project to analyze.
            threshold (float): The similarity threshold above which code is considered a clone (0.0-1.0).
            penalty_function (callable): A function to apply penalties for detected clones.
                                         Defaults to a simple warning message.
        """
        self.project_root = project_root
        self.threshold = threshold
        self.file_hashes = {}
        self.penalty_function = penalty_function or self._default_penalty_function

    def _default_penalty_function(self, file1, file2, similarity):
        """
        Default penalty function: prints a warning message.
        """
        print(f"WARNING: Potential code clone detected between {file1} and {file2} (Similarity: {similarity:.2f})")

    def calculate_hash(self, file_path):
        """
        Calculates a hash for the content of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The SHA-256 hash of the file content.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"Error reading or hashing file {file_path}: {e}")
            return None

    def calculate_ast_similarity(self, file1, file2):
        """
        Calculates the similarity between two files based on their Abstract Syntax Trees (ASTs).

        Args:
            file1 (str): The path to the first file.
            file2 (str): The path to the second file.

        Returns:
            float: The similarity score between the two files (0.0-1.0).
        """
        try:
            with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
                tree1 = ast.parse(f1.read())
                tree2 = ast.parse(f2.read())

            # Simple AST comparison: Count matching nodes
            nodes1 = list(ast.walk(tree1))
            nodes2 = list(ast.walk(tree2))

            common_nodes = 0
            for node1 in nodes1:
                for node2 in nodes2:
                    if type(node1) == type(node2):  # Compare node types
                        common_nodes += 1
                        break # Only count each node once

            total_nodes = max(len(nodes1), len(nodes2))
            if total_nodes == 0:
                return 0.0  # Avoid division by zero

            similarity = common_nodes / total_nodes
            return similarity

        except Exception as e:
            print(f"Error parsing or comparing ASTs for {file1} and {file2}: {e}")
            return 0.0

    def analyze_project(self):
        """
        Analyzes the project for potential code clones.
        """
        self.file_hashes = {}
        python_files = []

        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    self.file_hashes[file_path] = self.calculate_hash(file_path)

        # Compare all file pairs
        for i in range(len(python_files)):
            for j in range(i + 1, len(python_files)):
                file1 = python_files[i]
                file2 = python_files[j]

                if self.file_hashes[file1] is None or self.file_hashes[file2] is None:
                    continue # Skip files that couldn't be hashed

                # Quick hash check first
                if self.file_hashes[file1] == self.file_hashes[file2]:
                    similarity = 1.0  # Identical files
                else:
                    similarity = self.calculate_ast_similarity(file1, file2)

                if similarity >= self.threshold:
                    self.penalty_function(file1, file2, similarity)

    def set_penalty_function(self, penalty_function):
        """
        Sets a custom penalty function.

        Args:
            penalty_function (callable): The new penalty function to use.
        """
        self.penalty_function = penalty_function

if __name__ == '__main__':
    # Example usage:
    # Assuming your project root is in the current directory
    project_root = "."
    enforcer = CloningProhibitionEnforcer(project_root, threshold=0.8)

    # Example custom penalty function
    def custom_penalty(file1, file2, similarity):
        print(f"CRITICAL: Code duplication detected between {file1} and {file2} (Similarity: {similarity:.2f})")
        # Add more sophisticated actions here, like logging, raising exceptions, etc.

    #enforcer.set_penalty_function(custom_penalty) # Uncomment to use the custom penalty

    enforcer.analyze_project()