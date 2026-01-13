import ast
import random
import numpy as np

class AdaptiveQASTMutator:
    """
    A class for adaptively mutating Quantum Abstract Syntax Trees (QASTs) using phase-shift gates.
    This mutator dynamically evolves the AST based on probabilistic application of mutation operators,
    guided by a feedback mechanism (not implemented here) that could incorporate metrics like code coverage,
    performance, or security vulnerabilities.
    """

    def __init__(self, mutation_probability=0.1, phase_shift_range=(-np.pi, np.pi)):
        """
        Initializes the AdaptiveQASTMutator.

        Args:
            mutation_probability (float): The base probability of applying a mutation.
            phase_shift_range (tuple): The range of phase shifts to apply (in radians).
        """
        self.mutation_probability = mutation_probability
        self.phase_shift_range = phase_shift_range
        self.mutation_operators = {
            "insert_node": self.insert_node,
            "delete_node": self.delete_node,
            "replace_node": self.replace_node,
            "modify_constant": self.modify_constant,
            "swap_nodes": self.swap_nodes,
            "add_phase_shift": self.add_phase_shift,
        }
        self.operator_weights = {op_name: 1.0 for op_name in self.mutation_operators}  # Initial weights

    def mutate(self, tree):
        """
        Mutates the given AST.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        if random.random() < self.mutation_probability:
            # Choose a mutation operator based on weights
            operators = list(self.mutation_operators.keys())
            weights = list(self.operator_weights.values())
            chosen_operator_name = random.choices(operators, weights=weights, k=1)[0]
            chosen_operator = self.mutation_operators[chosen_operator_name]

            try:
                mutated_tree = chosen_operator(tree)
                return mutated_tree
            except Exception as e:
                print(f"Mutation failed: {e}")
                return tree  # Return original tree if mutation fails
        else:
            return tree

    def insert_node(self, tree):
        """
        Inserts a new node into the AST.  This is a placeholder and needs more sophisticated logic.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        # Placeholder: Insert a simple Pass node at a random location.
        nodes = list(ast.walk(tree))
        if not nodes:
            return tree

        insertion_point = random.choice(nodes)

        # Find the parent of the insertion point
        for parent in ast.walk(tree):
            for field, value in ast.iter_fields(parent):
                if isinstance(value, list):
                    if insertion_point in value:
                        index = value.index(insertion_point)
                        value.insert(index + 1, ast.Pass())  # Insert after the node
                        return tree
                elif value == insertion_point:
                    # Replace the node with a sequence of nodes (original + Pass)
                    setattr(parent, field, [insertion_point, ast.Pass()]) # This might not always work
                    return tree

        return tree # If no suitable insertion point is found, return the original tree

    def delete_node(self, tree):
        """
        Deletes a node from the AST.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        nodes = list(ast.walk(tree))
        if len(nodes) <= 1:  # Don't delete the root or leave an empty tree
            return tree

        node_to_delete = random.choice(nodes[1:])  # Avoid deleting the root

        for parent in ast.walk(tree):
            for field, value in ast.iter_fields(parent):
                if isinstance(value, list):
                    if node_to_delete in value:
                        value.remove(node_to_delete)
                        return tree
                elif value == node_to_delete:
                    # Replace the node with None (or a default value like ast.Pass())
                    setattr(parent, field, ast.Pass())
                    return tree

        return tree

    def replace_node(self, tree):
        """
        Replaces a node in the AST with another node.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        nodes = list(ast.walk(tree))
        if not nodes:
            return tree

        node_to_replace = random.choice(nodes)
        replacement_node = ast.Constant(value=random.randint(0, 100))  # Simple replacement

        for parent in ast.walk(tree):
            for field, value in ast.iter_fields(parent):
                if isinstance(value, list):
                    try:
                        index = value.index(node_to_replace)
                        value[index] = replacement_node
                        return tree
                    except ValueError:
                        pass # Node not found in this list
                elif value == node_to_replace:
                    setattr(parent, field, replacement_node)
                    return tree

        return tree

    def modify_constant(self, tree):
        """
        Modifies a constant value in the AST.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        constant_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Constant)]
        if not constant_nodes:
            return tree

        node_to_modify = random.choice(constant_nodes)
        if isinstance(node_to_modify.value, (int, float)):
            # Apply a small random change
            change = random.uniform(-0.1, 0.1) * node_to_modify.value
            node_to_modify.value += change
        elif isinstance(node_to_modify.value, str):
            # Modify the string (e.g., add a character)
            if node_to_modify.value:
                index = random.randint(0, len(node_to_modify.value) - 1)
                node_to_modify.value = node_to_modify.value[:index] + random.choice("abcdefg") + node_to_modify.value[index:]
            else:
                node_to_modify.value = "a"
        return tree

    def swap_nodes(self, tree):
        """
        Swaps two nodes in the AST.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        nodes = list(ast.walk(tree))
        if len(nodes) < 2:
            return tree

        node1, node2 = random.sample(nodes, 2)

        # Find parents and fields
        parent1, field1 = None, None
        parent2, field2 = None, None

        for parent in ast.walk(tree):
            for field, value in ast.iter_fields(parent):
                if isinstance(value, list):
                    if node1 in value:
                        parent1, field1 = parent, (field, value.index(node1))
                    if node2 in value:
                        parent2, field2 = parent, (field, value.index(node2))
                elif value == node1:
                    parent1, field1 = parent, field
                elif value == node2:
                    parent2, field2 = parent, field

        if parent1 and parent2 and field1 and field2:
            if isinstance(field1, tuple) and isinstance(field2, tuple): # Both are in lists
                list1 = getattr(parent1, field1[0])
                list2 = getattr(parent2, field2[0])
                list1[field1[1]], list2[field2[1]] = list2[field2[1]], list1[field1[1]]
            elif isinstance(field1, tuple): # Only node1 is in a list
                list1 = getattr(parent1, field1[0])
                temp = getattr(parent2, field2)
                list1[field1[1]], setattr(parent2, field2, list1[field1[1]])
                list1[field1[1]] = temp
            elif isinstance(field2, tuple): # Only node2 is in a list
                list2 = getattr(parent2, field2[0])
                temp = getattr(parent1, field1)
                list2[field2[1]], setattr(parent1, field1, list2[field2[1]])
                list2[field2[1]] = temp
            else: # Neither is in a list
                temp = getattr(parent1, field1)
                setattr(parent1, field1, getattr(parent2, field2))
                setattr(parent2, field2, temp)
            return tree

        return tree

    def add_phase_shift(self, tree):
        """
        Adds a phase shift to a numerical constant in the AST.  This is a placeholder.
        In a real quantum context, this would modify the phase of a quantum state represented by the constant.

        Args:
            tree (ast.AST): The AST to mutate.

        Returns:
            ast.AST: The mutated AST.
        """
        constant_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, (int, float))]
        if not constant_nodes:
            return tree

        node_to_modify = random.choice(constant_nodes)
        phase_shift = random.uniform(self.phase_shift_range[0], self.phase_shift_range[1])
        # In a real quantum context, this would be a complex number operation.
        # For this example, we'll just add the phase shift to the value.
        node_to_modify.value += phase_shift
        return tree

    def update_operator_weights(self, operator_name, reward):
        """
        Updates the weights of the mutation operators based on a reward signal.
        This allows the mutator to adapt to the specific characteristics of the code being mutated.

        Args:
            operator_name (str): The name of the operator that was used.
            reward (float): A reward signal indicating the effectiveness of the operator.
        """
        self.operator_weights[operator_name] += reward
        # Ensure weights remain non-negative
        for op_name in self.operator_weights:
            self.operator_weights[op_name] = max(0.1, self.operator_weights[op_name])  # Minimum weight

if __name__ == '__main__':
    # Example usage
    source_code = """
    def my_function(x):
        y = x + 1
        z = y * 2
        return z
    """
    tree = ast.parse(source_code)

    mutator = AdaptiveQASTMutator(mutation_probability=0.5)

    mutated_tree = mutator.mutate(tree)

    try:
        mutated_code = ast.unparse(mutated_tree)
        print("Original Code:\n", source_code)
        print("\nMutated Code:\n", mutated_code)
    except AttributeError as e:
        print(f"Error unparsing the mutated tree: {e}")
        print("Mutated tree structure (for debugging):\n", ast.dump(mutated_tree, indent=4))

    # Example of updating operator weights (simulating feedback)
    # mutator.update_operator_weights("insert_node", 0.5)  # Reward for insert_node
    # mutator.update_operator_weights("delete_node", -0.2) # Penalty for delete_node