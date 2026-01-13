import cmath
import random
from typing import List, Dict, Tuple, Any, Optional

# --- Quantum-inspired Data Structures ---

class QuantumToken:
    """
    Represents a token in a superposition of possible interpretations.
    Each interpretation has a complex amplitude.
    The sum of the squared magnitudes of amplitudes should ideally be 1 (normalized).
    """
    def __init__(self, interpretations: Dict[Tuple[str, str], complex]):
        """
        Initializes a QuantumToken.
        :param interpretations: A dictionary where keys are (value, type) tuples
                                and values are complex amplitudes.
                                Example: {("var", "IDENTIFIER"): 0.707j, ("let", "KEYWORD"): 0.707}
        """
        if not interpretations:
            raise ValueError("QuantumToken must have at least one interpretation.")
        self.interpretations = interpretations
        self._normalize_amplitudes()

    def _normalize_amplitudes(self):
        """Normalizes the amplitudes such that the sum of squared magnitudes is 1."""
        total_magnitude_sq = sum(abs(amp)**2 for amp in self.interpretations.values())
        if total_magnitude_sq == 0:
            # This state is effectively a null state, handle as an error or specific case
            # For now, we'll just ensure it doesn't cause division by zero.
            # In a real quantum system, this would imply an invalid state.
            return
        
        norm_factor = cmath.sqrt(total_magnitude_sq)
        self.interpretations = {
            (val, typ): amp / norm_factor
            for (val, typ), amp in self.interpretations.items()
        }

    def __repr__(self):
        return f"QToken({self.interpretations})"

class QuantumParseNode:
    """
    Represents a node in a quantum parse tree.
    For simplicity in this pseudocode, a node itself is not in superposition,
    but rather the entire parse tree fragment it belongs to is part of a superposition.
    """
    def __init__(self, node_type: str, children: List[Any] = None, value: Optional[str] = None):
        self.node_type = node_type
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        if self.value:
            return f"QNode({self.node_type}, '{self.value}')"
        return f"QNode({self.node_type}, children={len(self.children)})"

class QuantumParseTreeFragment:
    """
    A partial or complete parse tree, representing one possible outcome
    in a superposition of parse states.
    """
    def __init__(self, nodes: List[QuantumParseNode]):
        self.nodes = nodes

    def __repr__(self):
        return f"QTreeFragment({[str(n) for n in self.nodes]})"

class QuantumParseState:
    """
    Represents the overall state of the parser, a superposition of
    multiple possible parse tree fragments, each with a complex amplitude.
    """
    def __init__(self, states: List[Tuple[QuantumParseTreeFragment, complex]]):
        if not states:
            raise ValueError("QuantumParseState must have at least one state.")
        self.states = states
        self._normalize_amplitudes()

    def _normalize_amplitudes(self):
        """Normalizes the amplitudes such that the sum of squared magnitudes is 1."""
        total_magnitude_sq = sum(abs(amp)**2 for _, amp in self.states)
        if total_magnitude_sq == 0:
            # This state is effectively a null state, handle as an error or specific case
            return
        norm_factor = cmath.sqrt(total_magnitude_sq)
        self.states = [
            (fragment, amp / norm_factor)
            for fragment, amp in self.states
        ]

    def __repr__(self):
        return f"QParseState(num_states={len(self.states)})"

# --- Unitary Transformation (Grammar Rule Application) ---

class QuantumGrammarRule:
    """
    Represents a grammar rule that can be applied as a unitary transformation.
    For pseudocode, this is simplified. A real rule would involve more complex
    pattern matching and amplitude transformations.
    """
    def __init__(self, name: str, pattern_types: List[str], result_node_type: str):
        self.name = name
        self.pattern_types = pattern_types # e.g., ["IDENTIFIER", "OPERATOR", "IDENTIFIER"]
        self.result_node_type = result_node_type # e.g., "EXPRESSION"

    def apply_to_fragment(self, fragment: QuantumParseTreeFragment,
                          fragment_amplitude: complex) -> List[Tuple[QuantumParseTreeFragment, complex]]:
        """
        Applies the rule to a specific parse tree fragment.
        This is a highly simplified unitary transformation. In a real system,
        it would involve more complex amplitude calculations and entanglement.

        For pseudocode, we simulate:
        1. Checking if the rule's pattern matches the end of the fragment.
        2. If it matches, it creates a new node, replaces the matched elements,
           and potentially combines amplitudes.
        3. If it doesn't match, the rule doesn't create a new path from this fragment.
        """
        new_fragments_with_amplitudes = []

        # Try to match the rule's pattern with the last N nodes of the fragment
        if len(fragment.nodes) >= len(self.pattern_types):
            match_slice = fragment.nodes[-len(self.pattern_types):]
            
            # Check if types match
            types_in_slice = [n.node_type for n in match_slice]
            
            if types_in_slice == self.pattern_types:
                # Rule matches! Create a new node and a new fragment.
                # The amplitude of this new state is derived from the original fragment's amplitude.
                # This is where "unitary" aspect comes in: amplitudes are combined/transformed.
                
                new_node_children = match_slice
                new_node_value = None
                
                # A very simple example of combining values for the new node
                if all(hasattr(c, 'value') and c.value is not None for c in new_node_children):
                    new_node_value = " ".join(c.value for c in new_node_children)

                new_node = QuantumParseNode(self.result_node_type, children=new_node_children, value=new_node_value)
                
                # Create a new fragment by replacing the matched nodes with the new node
                new_nodes = fragment.nodes[:-len(self.pattern_types)] + [new_node]
                new_fragment = QuantumParseTreeFragment(new_nodes)
                
                # The amplitude transformation is the core "unitary" part.
                # For pseudocode, we'll simulate a simple phase shift or amplitude modification.
                # This is *not* a real quantum calculation, but illustrates the concept
                # of evolving amplitudes.
                
                # Example: A rule might have an intrinsic "strength" or "likelihood"
                # represented by a complex number.
                rule_transformation_factor = cmath.exp(1j * cmath.pi / 8) # Example phase shift
                
                # The amplitude of the new state is the original amplitude * rule's transformation factor.
                # This is a simplification; in reality, interference and entanglement would make it more complex.
                combined_amplitude = fragment_amplitude * rule_transformation_factor
                new_fragments_with_amplitudes.append((new_fragment, combined_amplitude))
        
        return new_fragments_with_amplitudes


# --- Core Quantum Parser Engine ---

class QuantumParserCore:
    """
    The core quantum parser engine.
    It maintains a superposition of parse states and applies unitary transformations
    (grammar rules) to evolve this superposition.
    Finally, it performs a "measurement" to collapse the superposition into a
    single, concrete parse tree.
    """
    def __init__(self, grammar_rules: List[QuantumGrammarRule]):
        self.grammar_rules = grammar_rules

    def _apply_all_unitary_transformations(self, current_state: QuantumParseState) -> QuantumParseState:
        """
        Applies all relevant grammar rules (unitary transformations) to the
        current superposition of parse states.
        This evolves the entire quantum state of the parser.
        """
        new_states_with_amplitudes: List[Tuple[QuantumParseTreeFragment, complex]] = []
        
        # Each existing fragment in the superposition can evolve in multiple ways
        # based on the grammar rules.
        for fragment, fragment_amplitude in current_state.states:
            # The original fragment might persist if no rule applies, or if rules
            # create parallel paths without consuming the original.
            # For simplicity, we add the original fragment back, and rules add new ones.
            # In a more rigorous model, amplitudes would be distributed.
            new_states_with_amplitudes.append((fragment, fragment_amplitude))

            for rule in self.grammar_rules:
                # Apply the rule to this specific fragment and its amplitude
                evolved_fragments = rule.apply_to_fragment(fragment, fragment_amplitude)
                new_states_with_amplitudes.extend(evolved_fragments)
        
        # Filter out states with negligible amplitudes to manage complexity
        # and re-normalize the entire superposition.
        filtered_states = [(f, a) for f, a in new_states_with_amplitudes if abs(a)**2 > 1e-9]
        
        if not filtered_states:
            # If all paths vanished, it's a parsing error or dead end.
            raise RuntimeError("All parse paths collapsed to zero amplitude.")

        return QuantumParseState(filtered_states)

    def _measure_state(self, final_state: QuantumParseState) -> QuantumParseTreeFragment:
        """
        Performs a 'measurement' operation on the final superposition of parse states.
        This collapses the quantum state into a single, concrete parse tree
        based on the probabilities derived from the amplitudes.
        """
        probabilities = []
        fragments = []
        
        for fragment, amplitude in final_state.states:
            prob = abs(amplitude)**2
            probabilities.append(prob)
            fragments.append(fragment)
        
        # Normalize probabilities (they should already be normalized if QuantumParseState is)
        total_prob = sum(probabilities)
        if total_prob == 0:
            raise RuntimeError("Cannot measure a state with zero total probability.")
        
        normalized_probabilities = [p / total_prob for p in probabilities]
        
        # Randomly select a parse tree based on the probabilities
        chosen_fragment = random.choices(fragments, weights=normalized_probabilities, k=1)[0]
        
        print(f"Measurement collapsed to: {chosen_fragment} with probability {normalized_probabilities[fragments.index(chosen_fragment)]:.4f}")
        return chosen_fragment

    def parse(self, quantum_token_stream: List[QuantumToken]) -> QuantumParseTreeFragment:
        """
        Parses a stream of QuantumTokens, evolving the parser's quantum state
        and finally collapsing it to a concrete parse tree.
        """
        # Initial state: a superposition of empty parse trees, each with some amplitude.
        # For simplicity, let's start with a single empty fragment with amplitude 1.
        initial_fragment = QuantumParseTreeFragment([])
        current_quantum_state = QuantumParseState([(initial_fragment, 1.0 + 0j)])

        print("--- Quantum Parsing Initiated ---")
        print(f"Initial state: {current_quantum_state}")

        for i, q_token in enumerate(quantum_token_stream):
            print(f"\nProcessing Quantum Token {i}: {q_token}")
            
            # Integrate the current quantum token into the parser's state.
            # Each interpretation of the token expands the current superposition.
            expanded_states_from_token: List[Tuple[QuantumParseTreeFragment, complex]] = []
            
            for (token_value, token_type), token_amplitude in q_token.interpretations.items():
                # For each existing fragment in the current superposition
                for existing_fragment, existing_amplitude in current_quantum_state.states:
                    # Create a new node for this token interpretation
                    token_node = QuantumParseNode(token_type, value=token_value)
                    
                    # Append it to the existing fragment
                    new_fragment_nodes = existing_fragment.nodes + [token_node]
                    new_fragment = QuantumParseTreeFragment(new_fragment_nodes)
                    
                    # Combine amplitudes: original fragment's amplitude * token's interpretation amplitude
                    # This represents the probability amplitude of reaching this specific path.
                    combined_amplitude = existing_amplitude * token_amplitude
                    expanded_states_from_token.append((new_fragment, combined_amplitude))
            
            # Now, `current_quantum_state` is the superposition of all possible
            # ways the token could have been interpreted and appended to existing paths.
            current_quantum_state = QuantumParseState(expanded_states_from_token)
            print(f"State after token {i} integration: {current_quantum_state}")

            # Apply unitary transformations (grammar rules) to evolve the state
            current_quantum_state = self._apply_all_unitary_transformations(current_quantum_state)
            print(f"State after unitary transformations for token {i}: {num_unique_fragments(current_quantum_state)} unique fragments in superposition.")

        print("\n--- Quantum Parsing Complete. Performing Measurement ---")
        final_parse_tree = self._measure_state(current_quantum_state)
        return final_parse_tree

# Helper for debugging output
def num_unique_fragments(state: QuantumParseState) -> int:
    """Counts unique fragment structures in a QuantumParseState."""
    unique_reprs = set()
    for fragment, _ in state.states:
        unique_reprs.add(str(fragment))
    return len(unique_reprs)

# --- Example Usage ---
if __name__ == "__main__":
    # Define some simplified grammar rules
    # Rule 1: IDENTIFIER -> VARIABLE_DECLARATION
    rule1 = QuantumGrammarRule("VarDecl", ["IDENTIFIER"], "VARIABLE_DECLARATION")
    
    # Rule 2: NUMBER -> LITERAL
    rule2 = QuantumGrammarRule("Literal", ["NUMBER"], "LITERAL")

    # Rule 3: VARIABLE_DECLARATION ASSIGN_OP LITERAL -> ASSIGNMENT_STATEMENT
    rule3 = QuantumGrammarRule("Assignment", ["VARIABLE_DECLARATION", "ASSIGN_OP", "LITERAL"], "ASSIGNMENT_STATEMENT")
    
    # Rule 4: LITERAL PLUS_OP LITERAL -> EXPRESSION
    rule4 = QuantumGrammarRule("Addition", ["LITERAL", "PLUS_OP", "LITERAL"], "EXPRESSION")

    # Rule 5: IDENTIFIER -> EXPRESSION (an identifier can be an expression)
    rule5 = QuantumGrammarRule("IdentifierAsExpression", ["IDENTIFIER"], "EXPRESSION")

    # Rule 6: EXPRESSION PLUS_OP EXPRESSION -> EXPRESSION
    rule6 = QuantumGrammarRule("ComplexAddition", ["EXPRESSION", "PLUS_OP", "EXPRESSION"], "EXPRESSION")

    grammar = [rule1, rule2, rule3, rule4, rule5, rule6]
    parser = QuantumParserCore(grammar)

    # Create a stream of quantum tokens
    # Token 1: Could be 'x' (IDENTIFIER) or '10' (NUMBER) - highly ambiguous!
    # Let's make it slightly biased towards 'x'
    q_token1 = QuantumToken({
        ("x", "IDENTIFIER"): cmath.sqrt(0.6) + 0j,
        ("10", "NUMBER"): cmath.sqrt(0.4) + 0j
    })

    # Token 2: Definitely an assignment operator
    q_token2 = QuantumToken({
        ("=", "ASSIGN_OP"): 1.0 + 0j
    })

    # Token 3: Could be 'y' (IDENTIFIER) or '20' (NUMBER)
    q_token3 = QuantumToken({
        ("y", "IDENTIFIER"): cmath.sqrt(0.5) + 0j,
        ("20", "NUMBER"): cmath.sqrt(0.5) + 0j
    })
    
    # Token 4: Could be '+' (PLUS_OP) or '-' (MINUS_OP)
    q_token4 = QuantumToken({
        ("+", "PLUS_OP"): cmath.sqrt(0.8) + 0j,
        ("-", "MINUS_OP"): cmath.sqrt(0.2) + 0j
    })

    # Token 5: Definitely a number
    q_token5 = QuantumToken({
        ("5", "NUMBER"): 1.0 + 0j
    })

    # Example 1: Simple assignment or expression
    print("\n--- Parsing Example 1: Ambiguous Assignment/Expression ---")
    token_stream_1 = [q_token1, q_token2, q_token3] # e.g., 'x' = 'y' or '10' = '20' (invalid) or 'x' = '20'
    try:
        final_tree_1 = parser.parse(token_stream_1)
        print(f"\nFinal Measured Parse Tree 1: {final_tree_1}")
    except RuntimeError as e:
        print(f"Parsing Error: {e}")

    # Example 2: More complex expression with operator ambiguity
    print("\n--- Parsing Example 2: Ambiguous Expression ---")
    token_stream_2 = [q_token1, q_token4, q_token5] # e.g., 'x' + '5' or '10' + '5'
    try:
        final_tree_2 = parser.parse(token_stream_2)
        print(f"\nFinal Measured Parse Tree 2: {final_tree_2}")
    except RuntimeError as e:
        print(f"Parsing Error: {e}")

    # Example 3: A sequence that might lead to a full assignment statement
    print("\n--- Parsing Example 3: Full Assignment Statement ---")
    token_stream_3 = [
        QuantumToken({("myVar", "IDENTIFIER"): 1.0 + 0j}),
        QuantumToken({("=", "ASSIGN_OP"): 1.0 + 0j}),
        QuantumToken({("100", "NUMBER"): 1.0 + 0j})
    ]
    try:
        final_tree_3 = parser.parse(token_stream_3)
        print(f"\nFinal Measured Parse Tree 3: {final_tree_3}")
    except RuntimeError as e:
        print(f"Parsing Error: {e}")

    # Example 4: A sequence that might lead to a complex expression
    print("\n--- Parsing Example 4: Complex Expression ---")
    token_stream_4 = [
        QuantumToken({("a", "IDENTIFIER"): 1.0 + 0j}),
        QuantumToken({("+", "PLUS_OP"): 1.0 + 0j}),
        QuantumToken({("b", "IDENTIFIER"): 1.0 + 0j})
    ]
    try:
        final_tree_4 = parser.parse(token_stream_4)
        print(f"\nFinal Measured Parse Tree 4: {final_tree_4}")
    except RuntimeError as e:
        print(f"Parsing Error: {e}")