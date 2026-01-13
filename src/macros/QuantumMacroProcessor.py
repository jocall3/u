# src/macros/QuantumMacroProcessor.py

import random
import uuid
from typing import Dict, List, Any, Tuple, Optional

# ----------------------------------------------------------------------------
# Quantum State Representation (Metaphorical)
# ----------------------------------------------------------------------------
# In our system, a "Qubit" represents a macro's potential state.
# A macro can be in a superposition of multiple possible text expansions.
# "Measurement" collapses this superposition into a single, definite output.

class Qubit:
    """Represents the state of a macro before expansion (measurement)."""
    def __init__(self, basis_states: List[Any], amplitudes: Optional[List[float]] = None):
        """
        Initializes a qubit in a superposition of basis states.
        :param basis_states: A list of possible outcomes (e.g., text snippets, AST subtrees).
        :param amplitudes: Probabilities for each basis state. If None, assumes uniform distribution.
        """
        if not basis_states:
            raise ValueError("A qubit must have at least one basis state.")
        self.basis_states = basis_states
        
        if amplitudes:
            if len(amplitudes) != len(basis_states) or not abs(sum(p**2 for p in amplitudes) - 1.0) < 1e-9:
                # For simplicity, we'll use simple probabilities instead of complex amplitudes.
                # The check is for sum of probabilities being 1.
                if not abs(sum(amplitudes) - 1.0) < 1e-9:
                    raise ValueError("Probabilities must sum to 1.")
                self.probabilities = amplitudes
            else: # Assuming amplitudes are valid complex numbers for a quantum state
                self.probabilities = [abs(a)**2 for a in amplitudes]
        else:
            # Uniform superposition
            num_states = len(self.basis_states)
            self.probabilities = [1/num_states] * num_states

    def measure(self) -> Any:
        """
        Collapses the superposition to a single definite state based on probabilities.
        This is the core of the "randomness" and "quantum" metaphor.
        """
        return random.choices(self.basis_states, weights=self.probabilities, k=1)[0]

    def __repr__(self) -> str:
        return f"Qubit(states={len(self.basis_states)})"


# ----------------------------------------------------------------------------
# Abstract Syntax Tree (AST) and Macro Representation
# ----------------------------------------------------------------------------
# Instead of simple text replacement, we operate on an AST. This allows for
# more complex and context-aware transformations.

class ASTNode:
    """Base class for a node in our document's Abstract Syntax Tree."""
    def __init__(self, node_id: str = None):
        self.id = node_id or str(uuid.uuid4())
        self.parent = None
        self.children = []

    def add_child(self, node: 'ASTNode'):
        node.parent = self
        self.children.append(node)

    def render(self) -> str:
        """Renders the node and its children back into a string."""
        return "".join(child.render() for child in self.children)

class TextNode(ASTNode):
    """A node representing plain text."""
    def __init__(self, content: str):
        super().__init__()
        self.content = content

    def render(self) -> str:
        return self.content

class MacroNode(ASTNode):
    """A node representing a macro invocation, e.g., !MACRO_NAME(arg1, key=val)."""
    def __init__(self, name: str, args: List[str], kwargs: Dict[str, str], original_text: str):
        super().__init__()
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.original_text = original_text
        self.qubit: Optional[Qubit] = None
        self.is_measured = False
        self.measured_value: Optional[ASTNode] = None # The result after measurement

    def render(self) -> str:
        if not self.is_measured or self.measured_value is None:
            # This should not happen in a final render, but is a safeguard.
            return f"<!-- UNRESOLVED MACRO: {self.original_text} -->"
        return self.measured_value.render()

# ----------------------------------------------------------------------------
# Quantum Register and Entanglement Management
# ----------------------------------------------------------------------------

class QuantumRegister:
    """
    Manages the state of all macros (qubits) and their entanglements.
    Entanglement means that measuring one macro instantly affects the state
    of another, no matter where it is in the document set.
    """
    def __init__(self):
        self.macros: Dict[str, MacroNode] = {}
        self.entanglement_groups: Dict[str, List[str]] = {} # group_id -> [macro_id_1, macro_id_2, ...]

    def register_macro(self, macro_node: MacroNode):
        """Adds a macro to the register."""
        if macro_node.id in self.macros:
            raise ValueError(f"Duplicate macro ID detected: {macro_node.id}")
        self.macros[macro_node.id] = macro_node

    def create_entanglement(self, macro_ids: List[str], group_id: str = None):
        """
        Entangles a set of macros. When one is measured, the others in the
        group must collapse to a consistent state.
        """
        group_id = group_id or str(uuid.uuid4())
        if group_id not in self.entanglement_groups:
            self.entanglement_groups[group_id] = []
        
        for macro_id in macro_ids:
            if macro_id not in self.macros:
                print(f"Warning: Attempted to entangle non-existent macro ID: {macro_id}")
                continue
            self.entanglement_groups[group_id].append(macro_id)
            # In a real implementation, we'd also link the qubits' states here.
            # For this pseudocode, the logic is handled during measurement.

    def get_entangled_peers(self, macro_id: str) -> List[MacroNode]:
        """Finds all macros entangled with the given one."""
        peers = []
        for group in self.entanglement_groups.values():
            if macro_id in group:
                for peer_id in group:
                    if peer_id != macro_id and peer_id in self.macros:
                        peers.append(self.macros[peer_id])
        return peers

# ----------------------------------------------------------------------------
# The Main Processor
# ----------------------------------------------------------------------------

class QuantumMacroProcessor:
    """
    Orchestrates the parsing, processing, and rendering of documents
    containing quantum macros.
    """
    def __init__(self):
        self.register = QuantumRegister()
        self.macro_definitions = self._load_macro_definitions()

    def _load_macro_definitions(self) -> Dict[str, callable]:
        """
        Loads the functions that define macro behaviors.
        In a real system, this would be dynamic (plugins, etc.).
        """
        # Each function takes the processor and the macro node as arguments
        # and should return a Qubit representing the possible outcomes.
        return {
            "DEFINE_CONCEPT": self.macro_define_concept,
            "EXPLAIN_CONCEPT": self.macro_explain_concept,
            "ENTANGLE": self.macro_entangle,
            "RANDOM_QUOTE": self.macro_random_quote,
        }

    def parse_to_ast(self, text: str) -> ASTNode:
        """
        A simplified parser that converts source text into an AST.
        This uses a basic regex; a real implementation would use a robust
        parsing library like Lark or ANTLR.
        """
        # Simplified regex to find !MACRO(...)
        import re
        macro_pattern = re.compile(r'(![A-Z_]+)\((.*?)\)')
        root = ASTNode("root")
        last_index = 0

        for match in macro_pattern.finditer(text):
            # Add preceding text
            start, end = match.span()
            if start > last_index:
                root.add_child(TextNode(text[last_index:start]))
            
            # Parse macro
            macro_name = match.group(1).lstrip('!')
            args_str = match.group(2)
            # Rudimentary arg parsing
            args = []
            kwargs = {}
            # This is highly simplified and doesn't handle complex cases
            # like nested parentheses or quoted strings with commas.
            parts = [p.strip() for p in args_str.split(',') if p.strip()]
            for part in parts:
                if '=' in part:
                    key, val = part.split('=', 1)
                    kwargs[key.strip()] = val.strip().strip('"\'')
                else:
                    args.append(part.strip().strip('"\''))

            macro_node = MacroNode(macro_name, args, kwargs, match.group(0))
            root.add_child(macro_node)
            last_index = end

        # Add any remaining text
        if last_index < len(text):
            root.add_child(TextNode(text[last_index:]))
            
        return root

    def process_ast(self, root: ASTNode):
        """
        Traverses the AST, populates the quantum register, and resolves macros.
        """
        # 1. First pass: Discover all macros and register them
        self._discover_macros(root)

        # 2. Second pass: Initialize qubits and handle declarative macros like !ENTANGLE
        self._initialize_qubits(root)

        # 3. Third pass: Measure all unmeasured qubits and replace nodes
        self._measure_and_replace(root)

    def _discover_macros(self, node: ASTNode):
        """Recursively traverses AST to find and register MacroNodes."""
        if isinstance(node, MacroNode):
            self.register.register_macro(node)
        for child in node.children:
            self._discover_macros(child)

    def _initialize_qubits(self, node: ASTNode):
        """
        Initializes the quantum state (Qubit) for each macro and handles
        special macros that modify the system, like !ENTANGLE.
        """
        if isinstance(node, MacroNode):
            if node.name in self.macro_definitions:
                handler = self.macro_definitions[node.name]
                # The handler returns a Qubit or performs an action
                result = handler(self, node)
                if isinstance(result, Qubit):
                    node.qubit = result
            else:
                print(f"Warning: No definition found for macro '{node.name}'")
        
        for child in node.children:
            self._initialize_qubits(child)

    def _measure_and_replace(self, node: ASTNode):
        """
        Recursively measures all qubits. The core of the expansion logic.
        This ensures that entangled macros are resolved consistently.
        """
        if isinstance(node, MacroNode) and not node.is_measured:
            self.measure_macro(node)

        for child in node.children:
            self._measure_and_replace(child)

    def measure_macro(self, macro_node: MacroNode) -> ASTNode:
        """
        Measures a single macro, handling entanglement.
        This is the "collapse of the wave function".
        """
        if macro_node.is_measured:
            return macro_node.measured_value

        if macro_node.qubit is None:
            # This can happen for action macros like !ENTANGLE
            macro_node.measured_value = TextNode("") # Renders to nothing
            macro_node.is_measured = True
            return macro_node.measured_value

        # --- Entanglement Logic ---
        # Check if any entangled peers have already been measured.
        peers = self.register.get_entangled_peers(macro_node.id)
        measured_peer = next((p for p in peers if p.is_measured), None)

        if measured_peer:
            # State is determined by the already-measured peer.
            # This is a simplified model of entanglement. A real system would
            # have a shared state vector for the entangled group.
            # Here, we just copy the result, assuming a 1-to-1 mapping.
            # A more complex implementation would use the peer's result to
            # select a specific basis state from this macro's qubit.
            print(f"Collapsing {macro_node.id} based on entangled peer {measured_peer.id}")
            collapsed_value = measured_peer.measured_value
        else:
            # This is the first in its entanglement group to be measured (or it's not entangled).
            # Perform a standard measurement.
            print(f"Measuring {macro_node.id}...")
            collapsed_value = macro_node.qubit.measure()

        # The result of a measurement should be an ASTNode (or convertible to one)
        if isinstance(collapsed_value, str):
            # For simplicity, we re-parse the result. This allows macros to generate other macros.
            # A more efficient implementation would have handlers return AST subtrees directly.
            measured_ast = self.parse_to_ast(collapsed_value)
        elif isinstance(collapsed_value, ASTNode):
            measured_ast = collapsed_value
        else:
            measured_ast = TextNode(str(collapsed_value))

        macro_node.measured_value = measured_ast
        macro_node.is_measured = True

        # Now, trigger the measurement of all entangled peers to ensure consistency
        for peer in peers:
            if not peer.is_measured:
                self.measure_macro(peer) # This will trigger the "if measured_peer" block for them

        return measured_ast

    def process_text(self, text: str) -> str:
        """
        High-level method to process a string of text.
        """
        # Reset state for this run
        self.register = QuantumRegister()
        
        ast = self.parse_to_ast(text)
        self.process_ast(ast)
        return ast.render()

    # ------------------------------------------------------------------------
    # Example Macro Definitions
    # ------------------------------------------------------------------------

    def macro_define_concept(self, node: MacroNode) -> Qubit:
        """
        !DEFINE_CONCEPT("concept_id", "formal_name", "explanation_text")
        This macro defines a concept that can be referenced elsewhere.
        The macro itself expands to the explanation text.
        """
        concept_id = node.args[0]
        formal_name = node.args[1]
        explanation = node.args[2]
        
        # Store this data globally so other macros can find it.
        # This is a side-effect, a common pattern in macro systems.
        if not hasattr(self, 'concepts'):
            self.concepts = {}
        self.concepts[concept_id] = {'name': formal_name, 'text': explanation}
        
        # The macro's rendered output is the definition itself.
        output_text = f"### {formal_name}\n\n{explanation}"
        return Qubit([output_text])

    def macro_explain_concept(self, node: MacroNode) -> Qubit:
        """
        !EXPLAIN_CONCEPT("concept_id")
        This macro is entangled with a corresponding DEFINE_CONCEPT.
        It expands to the same text.
        """
        concept_id = node.args[0]
        # In a real system, we'd need to handle the case where the definition
        # hasn't been processed yet. Here we assume it exists.
        concept_data = getattr(self, 'concepts', {}).get(concept_id)
        if not concept_data:
            return Qubit([f"**Error: Concept '{concept_id}' not defined.**"])
        
        output_text = f"As previously established in the section on *{concept_data['name']}*, {concept_data['text']}"
        return Qubit([output_text])

    def macro_entangle(self, node: MacroNode) -> None:
        """
        !ENTANGLE("macro_id_1", "macro_id_2", ...)
        A declarative macro that establishes entanglement. It renders to nothing.
        We assume macros have a `uid` kwarg for this.
        """
        macro_uids = [uid for uid in node.args]
        self.register.create_entanglement(macro_uids)
        return None # This macro performs an action, it has no output

    def macro_random_quote(self, node: MacroNode) -> Qubit:
        """
        !RANDOM_QUOTE(topic="quantum")
        Expands to a random quote based on a topic. This is a perfect
        example of a macro in a superposition of states.
        """
        topic = node.kwargs.get("topic", "general")
        quotes = {
            "quantum": [
                "Anyone who is not shocked by quantum theory has not understood it. - Niels Bohr",
                "If you think you understand quantum mechanics, you don't understand quantum mechanics. - Richard Feynman",
                "The universe is not only stranger than we imagine, it is stranger than we can imagine. - Werner Heisenberg"
            ],
            "relativity": [
                "The distinction between past, present, and future is only a stubbornly persistent illusion. - Albert Einstein",
                "Spacetime tells matter how to move; matter tells spacetime how to curve. - John Archibald Wheeler"
            ]
        }
        
        possible_quotes = quotes.get(topic, ["There are no quotes for this topic."])
        return Qubit(possible_quotes)


# ----------------------------------------------------------------------------
# Example Usage
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    # This demonstrates the processor's capabilities.
    
    source_markdown = """
# Chapter 1: Core Concepts

Let's begin with a foundational idea. We will assign the unique ID "c1" to this definition.
!DEFINE_CONCEPT("HeisenbergUncertainty", "Heisenberg's Uncertainty Principle", "This principle states that there is a fundamental limit to the precision with which certain pairs of physical properties of a particle, such as position and momentum, can be known.", uid="c1")

A quote to ponder: !RANDOM_QUOTE(topic="quantum", uid="q1")

# Chapter 5: Advanced Topics

Later in the text, we need to refer back to our first concept. This explanation is linked to the original definition via the `uid`.
!ENTANGLE("c1", "c2")
Here is the entangled explanation: !EXPLAIN_CONCEPT("HeisenbergUncertainty", uid="c2")

And another quote, which should be different from the first:
!RANDOM_QUOTE(topic="quantum", uid="q2")

Finally, a quote on a different topic:
!RANDOM_QUOTE(topic="relativity", uid="q3")
"""

    print("--- SOURCE MARKDOWN ---")
    print(source_markdown)
    print("\n" + "="*80 + "\n")

    processor = QuantumMacroProcessor()
    
    # Process the text multiple times to see the random nature of measurement
    for i in range(2):
        print(f"--- PROCESSING RUN {i+1} ---")
        # Create a new processor each time to reset the state for a clean run
        processor = QuantumMacroProcessor()
        rendered_output = processor.process_text(source_markdown)
        print(rendered_output)
        print("\n" + "="*80 + "\n")