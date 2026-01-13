import ast
import hashlib
import random
import typing
from typing import List, Tuple, Dict, Any

class QuantumCohomologyAnalyzer:
    """
    Analyzes Python code to identify topological invariants and potential quantum cohomology relationships.
    This is a highly experimental and theoretical approach.
    """

    def __init__(self, code: str):
        """
        Initializes the analyzer with the Python code.

        Args:
            code: The Python code to analyze as a string.
        """
        self.code = code
        self.tree = ast.parse(code)
        self.node_hashes: Dict[ast.AST, str] = {}
        self.graph: Dict[str, List[str]] = {}  # Adjacency list representation
        self.invariants: Dict[str, Any] = {}

    def calculate_node_hashes(self) -> None:
        """
        Calculates a hash for each node in the AST based on its type and attributes.
        """
        for node in ast.walk(self.tree):
            node_str = f"{type(node).__name__}:{node.__dict__}"
            self.node_hashes[node] = hashlib.sha256(node_str.encode()).hexdigest()

    def build_dependency_graph(self) -> None:
        """
        Builds a dependency graph based on the AST.  Nodes are AST node hashes,
        and edges represent parent-child relationships.
        """
        self.graph = {}
        for node in ast.walk(self.tree):
            node_hash = self.node_hashes[node]
            self.graph.setdefault(node_hash, [])
            for child in ast.iter_child_nodes(node):
                child_hash = self.node_hashes[child]
                self.graph[node_hash].append(child_hash)

    def calculate_graph_invariants(self) -> None:
        """
        Calculates basic graph invariants such as node degree distribution,
        connected components, and cycle detection (rudimentary).
        """
        degrees = {}
        for node, neighbors in self.graph.items():
            degree = len(neighbors)
            degrees.setdefault(degree, 0)
            degrees[degree] += 1
        self.invariants['degree_distribution'] = degrees

        # Simple connected components (very basic)
        visited = set()
        components = 0
        for node in self.graph:
            if node not in visited:
                components += 1
                self._dfs(node, visited)
        self.invariants['connected_components'] = components

        # Simple cycle detection (very basic and limited)
        self.invariants['has_cycle'] = self._detect_cycle()

    def _dfs(self, node: str, visited: set) -> None:
        """
        Depth-first search helper function for connected components.
        """
        visited.add(node)
        for neighbor in self.graph.get(node, []):
            if neighbor not in visited:
                self._dfs(neighbor, visited)

    def _detect_cycle(self) -> bool:
        """
        Rudimentary cycle detection.  Not robust.
        """
        visited = set()
        recursion_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)

            for neighbor in self.graph.get(node, []):
                if neighbor in recursion_stack:
                    return True
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True

            recursion_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def analyze_code_complexity(self) -> None:
        """
        Estimates code complexity based on AST depth and number of nodes.
        """
        max_depth = 0
        num_nodes = 0

        def calculate_depth(node, depth):
            nonlocal max_depth, num_nodes
            max_depth = max(max_depth, depth)
            num_nodes += 1
            for child in ast.iter_child_nodes(node):
                calculate_depth(child, depth + 1)

        calculate_depth(self.tree, 0)
        self.invariants['ast_depth'] = max_depth
        self.invariants['num_ast_nodes'] = num_nodes

    def identify_potential_invariants(self) -> None:
        """
        Identifies potential topological invariants based on code structure.
        This is a heuristic and experimental approach.
        """
        # Example: Number of function definitions might be a topological invariant
        num_functions = len([node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)])
        self.invariants['num_functions'] = num_functions

        # Example: Number of loops might be another invariant
        num_loops = len([node for node in ast.walk(self.tree) if isinstance(node, (ast.For, ast.While))])
        self.invariants['num_loops'] = num_loops

        # Example: Number of conditional statements
        num_conditionals = len([node for node in ast.walk(self.tree) if isinstance(node, ast.If)])
        self.invariants['num_conditionals'] = num_conditionals

        # Example: Average line length
        lines = self.code.splitlines()
        if lines:
            avg_line_length = sum(len(line) for line in lines) / len(lines)
            self.invariants['avg_line_length'] = avg_line_length
        else:
            self.invariants['avg_line_length'] = 0

    def run_analysis(self) -> Dict[str, Any]:
        """
        Runs the complete analysis pipeline.

        Returns:
            A dictionary containing the calculated invariants.
        """
        self.calculate_node_hashes()
        self.build_dependency_graph()
        self.calculate_graph_invariants()
        self.analyze_code_complexity()
        self.identify_potential_invariants()
        return self.invariants

    def generate_random_perturbation(self, perturbation_level: float = 0.1) -> str:
        """
        Generates a slightly perturbed version of the code.
        Perturbation level controls the amount of change.

        Args:
            perturbation_level: A float between 0 and 1 representing the
                percentage of code to perturb.

        Returns:
            The perturbed code as a string.
        """
        lines = self.code.splitlines()
        num_lines = len(lines)
        num_lines_to_perturb = int(num_lines * perturbation_level)

        indices_to_perturb = random.sample(range(num_lines), num_lines_to_perturb)

        for i in indices_to_perturb:
            # Simple perturbation: add a comment or change a variable name
            if random.random() < 0.5:
                lines[i] = "# " + lines[i]  # Add comment
            else:
                # Try to change a variable name (very basic)
                words = lines[i].split()
                if words:
                    index_to_change = random.randint(0, len(words) - 1)
                    if words[index_to_change].isidentifier():
                        words[index_to_change] = "perturbed_" + words[index_to_change]
                        lines[i] = " ".join(words)

        return "\n".join(lines)

if __name__ == '__main__':
    test_code = """
def my_function(x, y):
    if x > 0:
        result = x + y
    else:
        result = x - y
    for i in range(10):
        print(i)
    return result

def another_function(z):
    return z * 2
"""

    analyzer = QuantumCohomologyAnalyzer(test_code)
    invariants = analyzer.run_analysis()
    print("Invariants:", invariants)

    perturbed_code = analyzer.generate_random_perturbation(perturbation_level=0.2)
    print("\nPerturbed Code:\n", perturbed_code)

    analyzer2 = QuantumCohomologyAnalyzer(perturbed_code)
    invariants2 = analyzer2.run_analysis()
    print("\nInvariants of Perturbed Code:", invariants2)