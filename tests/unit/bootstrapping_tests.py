import unittest
import random
import math
from typing import Dict, Any, Tuple, List

# --- Conceptual Mock Classes for Quantum Bootstrapping System ---

class QuantumState:
    """
    Represents a conceptual quantum state with probabilistic outcomes.
    In this simulation, it holds a dictionary of possibilities with their
    relative weights, which are normalized to probabilities upon initialization.
    """
    def __init__(self, possibilities: Dict[str, float]):
        """
        Initializes a QuantumState.
        :param possibilities: A dictionary where keys are state names (str)
                              and values are non-negative weights (float).
        :raises ValueError: If possibilities are empty or contain negative weights.
        """
        if not possibilities:
            raise ValueError("QuantumState must have at least one possibility.")
        if not all(isinstance(p, (int, float)) and p >= 0 for p in possibilities.values()):
            raise ValueError("Probabilities (weights) must be non-negative numbers.")

        self._possibilities = possibilities
        self._normalize_probabilities()

    def _normalize_probabilities(self):
        """Normalizes the internal weights to sum to 1.0."""
        total_weight = sum(self._possibilities.values())
        if total_weight == 0:
            # If all weights are zero, assign equal probability to all
            num_possibilities = len(self._possibilities)
            if num_possibilities > 0:
                for key in self._possibilities:
                    self._possibilities[key] = 1.0 / num_possibilities
            # If num_possibilities is 0, it's caught by the constructor.
        else:
            for key in self._possibilities:
                self._possibilities[key] /= total_weight

    def observe(self) -> str:
        """
        Simulates observation, collapsing the state to one outcome based on probabilities.
        :return: The observed state name.
        """
        outcomes = list(self._possibilities.keys())
        weights = list(self._possibilities.values())
        if not outcomes:
            return None  # Should not happen due to constructor validation
        return random.choices(outcomes, weights=weights, k=1)[0]

    def get_probabilities(self) -> Dict[str, float]:
        """Returns the normalized probabilities of the state."""
        return self._possibilities

    def __eq__(self, other: Any) -> bool:
        """
        Compares two QuantumState objects for equality, accounting for
        floating-point inaccuracies and order of possibilities.
        """
        if not isinstance(other, QuantumState):
            return NotImplemented
        
        # Combine all keys from both states to ensure comparison handles missing keys (implicitly 0.0)
        all_keys = set(self._possibilities.keys()) | set(other._possibilities.keys())
        
        for key in all_keys:
            prob_self = self._possibilities.get(key, 0.0)
            prob_other = other._possibilities.get(key, 0.0)
            if not math.isclose(prob_self, prob_other, rel_tol=1e-9, abs_tol=1e-12):
                return False
        return True

    def __repr__(self) -> str:
        return f"QuantumState({self._possibilities})"

class EntangledPair:
    """
    Simulates a conceptual entangled pair of 'knowledge units' or 'concepts'.
    Observation of one conceptually influences the other, reflecting a shared
    underlying state.
    """
    def __init__(self, concept_a_state: QuantumState, concept_b_state: QuantumState):
        """
        Initializes an EntangledPair.
        :param concept_a_state: The QuantumState of the first concept.
        :param concept_b_state: The QuantumState of the second concept.
        """
        self._concept_a_state = concept_a_state
        self._concept_b_state = concept_b_state
        # Simulate a shared, hidden 'quantum' value that dictates correlation
        self._entangled_value = random.choice(["correlation_type_X", "correlation_type_Y", "correlation_type_Z"])

    def get_concept_a_state(self) -> QuantumState:
        return self._concept_a_state

    def get_concept_b_state(self) -> QuantumState:
        return self._concept_b_state

    def observe_a(self) -> str:
        """
        Simulates observing concept A, yielding an outcome correlated with the
        underlying entangled value.
        """
        if self._entangled_value == "correlation_type_X":
            return "outcome_A_alpha"
        elif self._entangled_value == "correlation_type_Y":
            return "outcome_A_beta"
        else: # correlation_type_Z
            return "outcome_A_gamma"

    def observe_b(self) -> str:
        """
        Simulates observing concept B, yielding an outcome correlated with the
        underlying entangled value (and thus with A's observation).
        """
        if self._entangled_value == "correlation_type_X":
            return "outcome_B_alpha"
        elif self._entangled_value == "correlation_type_Y":
            return "outcome_B_beta"
        else: # correlation_type_Z
            return "outcome_B_gamma"

    def get_correlation_value(self) -> str:
        """
        Returns the underlying correlated value for testing purposes.
        In a true quantum system, this would not be directly accessible.
        """
        return self._entangled_value

class LanguageCompiler:
    """
    A conceptual compiler that can process and 'self-compile' its own grammar
    or set of operational rules, simulating language self-reference.
    """
    def __init__(self, grammar_rules: Dict[str, str]):
        """
        Initializes the LanguageCompiler with a set of grammar rules.
        :param grammar_rules: A dictionary representing the language's rules.
        """
        self._grammar_rules = grammar_rules
        self._compiled_self_representation: Optional[Dict[str, Any]] = None

    def compile_self(self) -> Dict[str, Any]:
        """
        Simulates the language processing its own grammar rules to create
        a self-representation. This is a placeholder for a complex parsing
        and semantic analysis process.
        :return: A dictionary representing the self-compiled state.
        """
        # In a real system, this would involve parsing, semantic analysis,
        # and potentially code generation based on the grammar rules themselves.
        # Here, we simulate the outcome of such a process.
        self._compiled_self_representation = {
            "compiler_version": "1.0.quantum_alpha",
            "rules_processed_count": len(self._grammar_rules),
            "self_awareness_level": "syntactic_understanding_phase",
            "generated_meta_code_snippet": f"// Self-generated directive based on {len(self._grammar_rules)} foundational rules."
        }
        return self._compiled_self_representation

    def get_grammar_rules(self) -> Dict[str, str]:
        return self._grammar_rules

    def get_compiled_self_representation(self) -> Optional[Dict[str, Any]]:
        return self._compiled_self_representation

class QuantumBootstrapper:
    """
    The core conceptual engine for self-referential quantum bootstrapping.
    It manages knowledge expansion, language self-compilation, and entanglement
    of concepts, progressing towards a state where the 'learner becomes the teacher'.
    """
    def __init__(self, initial_seed_concept: str):
        """
        Initializes the QuantumBootstrapper with a foundational concept.
        :param initial_seed_concept: The starting point for knowledge generation.
        """
        self._seed = initial_seed_concept
        # Knowledge base stores concepts mapped to their current QuantumState
        self._knowledge_base: Dict[str, QuantumState] = {
            initial_seed_concept: QuantumState({"initial_form_A": 0.7, "initial_form_B": 0.3})
        }
        self._language_compiler = LanguageCompiler({
            "rule_001_concept_definition": "concept -> [attribute]+",
            "rule_002_entanglement_syntax": "entangle(concept_A, concept_B) -> correlated_state",
            "rule_003_bootstrapping_directive": "iterate -> expand_knowledge, self_compile, entangle_new"
        })
        self._bootstrapping_iterations = 0
        # Stores EntangledPair objects, keyed by a sorted tuple of concept names
        self._entangled_concepts: Dict[Tuple[str, str], EntangledPair] = {}

    def get_seed(self) -> str:
        return self._seed

    def get_knowledge_base(self) -> Dict[str, QuantumState]:
        return self._knowledge_base

    def get_language_compiler(self) -> LanguageCompiler:
        return self._language_compiler

    def bootstrap_iteration(self) -> int:
        """
        Executes a single step of the self-referential quantum bootstrapping process.
        This involves expanding knowledge, self-compiling the language, and
        potentially creating new entanglements.
        :return: The current number of concepts in the knowledge base.
        """
        # 1. Expand knowledge based on existing states (probabilistic generation)
        new_concepts: Dict[str, QuantumState] = {}
        for concept_name, q_state in list(self._knowledge_base.items()): # Iterate over a copy
            observed_form = q_state.observe()
            # Simulate generating new knowledge based on the observed form
            if "initial_form" in observed_form:
                new_concepts[f"derived_{concept_name}_state_alpha"] = QuantumState({"potential_state_1": 0.6, "potential_state_2": 0.4})
                new_concepts[f"derived_{concept_name}_state_beta"] = QuantumState({"potential_state_3": 0.8, "potential_state_4": 0.2})
            elif "potential_state_1" in observed_form:
                new_concepts[f"refined_{concept_name}_substate_gamma"] = QuantumState({"refined_form_X": 0.9, "refined_form_Y": 0.1})
            # Add some randomness to concept generation
            if random.random() < 0.3:
                new_concepts[f"random_discovery_{self._bootstrapping_iterations}_{len(new_concepts)}"] = QuantumState({"unforeseen_aspect": 1.0})

        self._knowledge_base.update(new_concepts)

        # 2. Attempt self-compilation of language
        self._language_compiler.compile_self()

        # 3. Potentially create new entanglements between newly generated concepts
        if self._bootstrapping_iterations == 0 and len(self._knowledge_base) > 1:
            # Entangle the seed with one of the first derived concepts
            first_derived_concept = next(iter(new_concepts.keys()), self._seed)
            self.entangle_concepts(self._seed, first_derived_concept)
        elif self._bootstrapping_iterations > 0 and len(new_concepts) >= 2:
            # Entangle two random new concepts
            new_concept_names = list(new_concepts.keys())
            if len(new_concept_names) >= 2:
                concept1, concept2 = random.sample(new_concept_names, 2)
                self.entangle_concepts(concept1, concept2)

        self._bootstrapping_iterations += 1
        return len(self._knowledge_base)

    def entangle_concepts(self, concept_name_a: str, concept_name_b: str) -> EntangledPair:
        """
        Creates a conceptual entanglement between two knowledge units.
        :param concept_name_a: The name of the first concept.
        :param concept_name_b: The name of the second concept.
        :return: The created EntangledPair object.
        :raises ValueError: If either concept does not exist in the knowledge base.
        """
        if concept_name_a not in self._knowledge_base or concept_name_b not in self._knowledge_base:
            raise ValueError("Both concepts must exist in the knowledge base to be entangled.")

        # Use a sorted tuple as key to ensure uniqueness regardless of order (A,B) vs (B,A)
        pair_key = tuple(sorted((concept_name_a, concept_name_b)))
        if pair_key not in self._entangled_concepts:
            self._entangled_concepts[pair_key] = EntangledPair(
                self._knowledge_base[concept_name_a],
                self._knowledge_base[concept_name_b]
            )
        return self._entangled_concepts[pair_key]

    def get_entangled_pairs(self) -> Dict[Tuple[str, str], EntangledPair]:
        return self._entangled_concepts

    def get_bootstrapping_iterations(self) -> int:
        return self._bootstrapping_iterations

    def simulate_learner_becomes_teacher(self) -> str:
        """
        Simulates the system generating new directives or 'teaching material'
        based on its bootstrapped and entangled knowledge, embodying the
        "learner becomes the teacher" phase.
        :return: A generated directive string.
        """
        if self._bootstrapping_iterations < 3: # Requires some iterations to 'learn'
            return "System still in foundational learning phase, cannot generate advanced directives yet."

        known_concepts = list(self._knowledge_base.keys())
        if not known_concepts:
            return "No concepts learned yet to generate directives."

        # Select two random concepts for the directive
        concept_1 = random.choice(known_concepts)
        concept_2 = random.choice(known_concepts) if len(known_concepts) > 1 else concept_1

        # Randomly choose a directive template
        directive_templates = [
            "Directive: Explore the quantum entanglement implications between '{concept_1}' and '{concept_2}'.",
            "Instruction: Formulate a new self-compilation rule based on the observed states of '{concept_1}'.",
            "Task: Design a conceptual experiment to observe the superposition of '{concept_2}' within the knowledge graph.",
            "Guidance: Synthesize a novel conceptual space by integrating '{concept_1}' and its derived forms with '{concept_2}'.",
            "Mandate: Analyze the self-referential loops in the language compiler concerning '{concept_1}' and '{concept_2}'."
        ]
        directive_template = random.choice(directive_templates)

        return directive_template.format(concept_1=concept_1, concept_2=concept_2)


# --- Unit Tests for Quantum Bootstrapping ---

class TestQuantumBootstrapping(unittest.TestCase):
    """
    Unit tests for the self-referential quantum bootstrapping system,
    verifying language self-compilation and entanglement.
    """

    def setUp(self):
        """Set up a fresh QuantumBootstrapper instance for each test."""
        self.bootstrapper = QuantumBootstrapper("GenesisConcept")

    def test_initial_state_and_seed(self):
        """Verify the bootstrapper's initial configuration and seed concept."""
        self.assertIsNotNone(self.bootstrapper.get_seed())
        self.assertEqual(self.bootstrapper.get_seed(), "GenesisConcept")

        knowledge_base = self.bootstrapper.get_knowledge_base()
        self.assertIn("GenesisConcept", knowledge_base)
        self.assertIsInstance(knowledge_base["GenesisConcept"], QuantumState)
        # Check initial probabilities (allowing for float comparison)
        expected_initial_state = QuantumState({"initial_form_A": 0.7, "initial_form_B": 0.3})
        self.assertEqual(knowledge_base["GenesisConcept"], expected_initial_state)
        self.assertEqual(self.bootstrapper.get_bootstrapping_iterations(), 0)

    def test_language_compiler_initialization(self):
        """Ensure the language compiler is correctly initialized with rules."""
        compiler = self.bootstrapper.get_language_compiler()
        self.assertIsInstance(compiler, LanguageCompiler)
        self.assertGreater(len(compiler.get_grammar_rules()), 0)
        self.assertIsNone(compiler.get_compiled_self_representation()) # Should not be compiled initially

    def test_single_bootstrapping_iteration(self):
        """Test the effects of a single bootstrapping step: knowledge expansion, self-compilation, entanglement."""
        initial_knowledge_count = len(self.bootstrapper.get_knowledge_base())
        self.bootstrapper.bootstrap_iteration()

        self.assertEqual(self.bootstrapper.get_bootstrapping_iterations(), 1)
        # Knowledge base should have expanded with derived concepts
        self.assertGreater(len(self.bootstrapper.get_knowledge_base()), initial_knowledge_count)
        self.assertTrue(any("derived_GenesisConcept" in k for k in self.bootstrapper.get_knowledge_base()))

        # Language compiler should have performed self-compilation
        compiler = self.bootstrapper.get_language_compiler()
        self.assertIsNotNone(compiler.get_compiled_self_representation())
        self.assertIn("self_awareness_level", compiler.get_compiled_self_representation())
        self.assertEqual(compiler.get_compiled_self_representation()["rules_processed_count"], len(compiler.get_grammar_rules()))

        # Entanglement should have been initiated between the seed and a derived concept
        entangled_pairs = self.bootstrapper.get_entangled_pairs()
        self.assertGreater(len(entangled_pairs), 0)
        first_pair_key = list(entangled_pairs.keys())[0]
        self.assertIn("GenesisConcept", first_pair_key)
        self.assertIsInstance(entangled_pairs[first_pair_key], EntangledPair)

    def test_multiple_bootstrapping_iterations_refinement(self):
        """Verify that multiple iterations lead to a more complex knowledge base and sustained self-compilation."""
        initial_knowledge_count = len(self.bootstrapper.get_knowledge_base())
        
        # Perform several iterations
        num_iterations = 5
        for i in range(num_iterations):
            self.bootstrapper.bootstrap_iteration()
            self.assertEqual(self.bootstrapper.get_bootstrapping_iterations(), i + 1)

        # Knowledge base should be significantly larger
        self.assertGreater(len(self.bootstrapper.get_knowledge_base()), initial_knowledge_count + num_iterations * 2) # Expect at least 2 new concepts per iteration

        # Compiler should have been re-compiled (or state updated) in each iteration
        final_compiler_state = self.bootstrapper.get_language_compiler().get_compiled_self_representation()
        self.assertIsNotNone(final_compiler_state)
        self.assertIn("generated_meta_code_snippet", final_compiler_state)

        # Entanglement should persist and potentially grow
        self.assertGreater(len(self.bootstrapper.get_entangled_pairs()), 0)
        # Check if new entanglements were created beyond the first iteration
        if num_iterations > 1:
            self.assertGreater(len(self.bootstrapper.get_entangled_pairs()), 1)

    def test_quantum_state_observation_probabilistic_nature(self):
        """Test the probabilistic outcome of QuantumState observation."""
        test_state = QuantumState({"StateA": 0.5, "StateB": 0.5})
        observations = [test_state.observe() for _ in range(2000)] # Increased observations for better statistical accuracy
        count_A = observations.count("StateA")
        count_B = observations.count("StateB")

        # With 2000 observations, expect roughly 50/50, allowing for statistical variance
        self.assertAlmostEqual(count_A, 1000, delta=100) # Allow +/- 5%
        self.assertAlmostEqual(count_B, 1000, delta=100)

        # Test a state with unequal probabilities
        test_state_unequal = QuantumState({"StateX": 0.8, "StateY": 0.2})
        observations_unequal = [test_state_unequal.observe() for _ in range(2000)]
        count_X = observations_unequal.count("StateX")
        count_Y = observations_unequal.count("StateY")
        self.assertAlmostEqual(count_X, 1600, delta=100) # Allow +/- 5%
        self.assertAlmostEqual(count_Y, 400, delta=100)

    def test_entanglement_correlation_consistency(self):
        """Test the conceptual correlation consistency within entangled pairs."""
        self.bootstrapper.bootstrap_iteration() # Ensure entanglement is created
        entangled_pairs = self.bootstrapper.get_entangled_pairs()
        self.assertGreater(len(entangled_pairs), 0)

        # Pick an arbitrary entangled pair
        pair_key = list(entangled_pairs.keys())[0]
        entangled_pair = entangled_pairs[pair_key]

        # The underlying correlation_value should dictate both observation outcomes
        correlation_value = entangled_pair.get_correlation_value()

        if correlation_value == "correlation_type_X":
            self.assertEqual(entangled_pair.observe_a(), "outcome_A_alpha")
            self.assertEqual(entangled_pair.observe_b(), "outcome_B_alpha")
        elif correlation_value == "correlation_type_Y":
            self.assertEqual(entangled_pair.observe_a(), "outcome_A_beta")
            self.assertEqual(entangled_pair.observe_b(), "outcome_B_beta")
        else: # correlation_type_Z
            self.assertEqual(entangled_pair.observe_a(), "outcome_A_gamma")
            self.assertEqual(entangled_pair.observe_b(), "outcome_B_gamma")

        # Test that trying to entangle non-existent concepts raises an error
        with self.assertRaises(ValueError):
            self.bootstrapper.entangle_concepts("NonExistentConcept1", "NonExistentConcept2")

    def test_language_self_compilation_process(self):
        """Verify the language compiler's ability to process its own rules and generate a self-representation."""
        compiler = self.bootstrapper.get_language_compiler()
        self.assertIsNone(compiler.get_compiled_self_representation())

        compiled_output = compiler.compile_self()
        self.assertIsNotNone(compiled_output)
        self.assertIn("compiler_version", compiled_output)
        self.assertIn("rules_processed_count", compiled_output)
        self.assertEqual(compiled_output["rules_processed_count"], len(compiler.get_grammar_rules()))
        self.assertIn("self_awareness_level", compiled_output)
        self.assertIn("generated_meta_code_snippet", compiled_output)

        # Ensure subsequent calls return the same (or updated, if logic allowed) representation
        # In this mock, it's idempotent after the first call.
        self.assertEqual(compiler.get_compiled_self_representation(), compiled_output)

    def test_learner_becomes_teacher_phase_progression(self):
        """Test the system's ability to generate new directives after sufficient bootstrapping."""
        # Initially, it should indicate it's not ready to teach
        initial_directive = self.bootstrapper.simulate_learner_becomes_teacher()
        self.assertIn("learning phase", initial_directive)

        # Bootstrap enough iterations to reach the 'teaching' phase (threshold is 3)
        for _ in range(3):
            self.bootstrapper.bootstrap_iteration()

        teaching_directive = self.bootstrapper.simulate_learner_becomes_teacher()
        self.assertNotIn("learning phase", teaching_directive)
        self.assertIsInstance(teaching_directive, str)
        self.assertGreater(len(teaching_directive), 50) # Ensure it's a meaningful, generated string

        # Ensure the directive incorporates known concepts
        knowledge_keys = list(self.bootstrapper.get_knowledge_base().keys())
        # This is a probabilistic check, as random.choice is used.
        # We assert that at least one known concept is likely to be in the directive.
        self.assertTrue(any(k in teaching_directive for k in knowledge_keys),
                        f"Directive '{teaching_directive}' does not contain any known concepts.")

    def test_quantum_state_normalization_logic(self):
        """Test that QuantumState probabilities are correctly normalized under various conditions."""
        state1 = QuantumState({"A": 1, "B": 1, "C": 1})
        self.assertEqual(state1.get_probabilities(), {"A": 1/3, "B": 1/3, "C": 1/3})

        state2 = QuantumState({"X": 10, "Y": 30})
        self.assertEqual(state2.get_probabilities(), {"X": 0.25, "Y": 0.75})

        state3 = QuantumState({"Z": 0.0}) # Should normalize to 1.0 if it's the only one
        self.assertEqual(state3.get_probabilities(), {"Z": 1.0})

        state4 = QuantumState({"P": 0.5, "Q": 0.5})
        self.assertEqual(state4.get_probabilities(), {"P": 0.5, "Q": 0.5})

        # Test with zero total weight (should distribute equally)
        state5 = QuantumState({"R": 0, "S": 0, "T": 0})
        self.assertEqual(state5.get_probabilities(), {"R": 1/3, "S": 1/3, "T": 1/3})

        # Test with invalid input (empty possibilities)
        with self.assertRaises(ValueError):
            QuantumState({})
        # Test with invalid input (negative weight)
        with self.assertRaises(ValueError):
            QuantumState({"A": -1})
        # Test with invalid input (non-numeric weight)
        with self.assertRaises(ValueError):
            QuantumState({"A": "invalid_weight"})

    def test_quantum_state_equality_comparison(self):
        """Test the custom equality comparison for QuantumState objects."""
        s1 = QuantumState({"Alpha": 0.5, "Beta": 0.5})
        s2 = QuantumState({"Alpha": 0.5, "Beta": 0.5})
        s3 = QuantumState({"Alpha": 0.6, "Beta": 0.4})
        s4 = QuantumState({"Beta": 0.5, "Alpha": 0.5}) # Order of keys shouldn't matter

        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertEqual(s1, s4)

        # Test with floating point precision differences
        s5 = QuantumState({"Gamma": 1/3, "Delta": 2/3})
        s6 = QuantumState({"Gamma": 0.3333333333333333, "Delta": 0.6666666666666666})
        self.assertEqual(s5, s6)

        # Test with effectively zero probabilities for missing keys
        s7 = QuantumState({"Epsilon": 1.0})
        s8 = QuantumState({"Epsilon": 1.0, "Zeta": 0.0})
        self.assertEqual(s7, s8)
        self.assertEqual(s8, s7)

        s9 = QuantumState({"Eta": 0.5, "Theta": 0.5})
        s10 = QuantumState({"Eta": 0.5}) # Not equal, 'Theta' is missing and not implicitly zero
        self.assertNotEqual(s9, s10)
        self.assertNotEqual(s10, s9)


if __name__ == '__main__':
    unittest.main()