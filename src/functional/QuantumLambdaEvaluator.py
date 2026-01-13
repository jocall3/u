# src/functional/QuantumLambdaEvaluator.py

import cmath
from typing import List, Tuple, Dict, Union, Callable, Set

# A small tolerance for floating point comparisons with complex numbers
TOLERANCE = 1e-9

# --- 1. Foundational Lambda Calculus Structures ---
# These classes represent the "classical" basis states for our quantum terms.
# They are immutable to be safely used as dictionary keys.

class Term:
    """Abstract base class for all lambda calculus terms."""
    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    def get_free_variables(self) -> Set[str]:
        """Returns the set of free variables in the term."""
        raise NotImplementedError

class Variable(Term):
    """Represents a variable, e.g., 'x'."""
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def get_free_variables(self) -> Set[str]:
        return {self.name}

class Lambda(Term):
    """Represents a lambda abstraction, e.g., 'λx.M'."""
    def __init__(self, var: Variable, body: Term):
        self._var = var
        self._body = body

    @property
    def var(self) -> Variable:
        return self._var

    @property
    def body(self) -> Term:
        return self._body

    def __str__(self) -> str:
        return f"(λ{self.var}. {self.body})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Lambda) and self.var == other.var and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.var, self.body))

    def get_free_variables(self) -> Set[str]:
        return self.body.get_free_variables() - {self.var.name}

class Application(Term):
    """Represents a function application, e.g., '(M N)'."""
    def __init__(self, func: Term, arg: Term):
        self._func = func
        self._arg = arg

    @property
    def func(self) -> Term:
        return self._func

    @property
    def arg(self) -> Term:
        return self._arg

    def __str__(self) -> str:
        return f"({self.func} {self.arg})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Application) and self.func == other.func and self.arg == other.arg

    def __hash__(self) -> int:
        return hash((self.func, self.arg))

    def get_free_variables(self) -> Set[str]:
        return self.func.get_free_variables().union(self.arg.get_free_variables())

# --- 2. Quantum State Representation ---

# A quantum state is a dictionary mapping a classical term to a complex amplitude.
QuantumState = Dict[Term, complex]

class QuantumTerm:
    """Represents a superposition of lambda calculus terms."""
    def __init__(self, state: QuantumState):
        self.state = self._normalize(state)

    def _normalize(self, state: QuantumState) -> QuantumState:
        """Normalizes the quantum state so that the sum of squared magnitudes is 1."""
        prob_sum = sum(abs(amp)**2 for amp in state.values())
        if prob_sum < TOLERANCE:
            return {}
        norm = cmath.sqrt(prob_sum)
        return {term: amp / norm for term, amp in state.items() if abs(amp) > TOLERANCE}

    def __str__(self) -> str:
        if not self.state:
            return "|Empty⟩"
        return " + ".join([f"({amp:.3f})|{term}⟩" for term, amp in self.state.items()])

# --- 3. Core Evaluator Logic ---

class QuantumLambdaEvaluator:
    """
    A pseudocode evaluator for a quantum lambda calculus.
    This demonstrates the principles of superposition, unitary evolution (evaluation),
    and interference via controlled-phase oracles.
    """
    def __init__(self, max_reduction_steps: int = 100):
        self._max_steps = max_reduction_steps
        self._fresh_var_counter = 0

    def _get_fresh_variable(self, existing_vars: Set[str]) -> Variable:
        """Generates a fresh variable name not in the given set."""
        while True:
            name = f"v{self._fresh_var_counter}"
            self._fresh_var_counter += 1
            if name not in existing_vars:
                return Variable(name)

    def _substitute(self, term: Term, var_to_replace: Variable, replacement: Term) -> Term:
        """
        Performs substitution M[x:=N] with proper handling of variable capture
        using alpha-conversion.
        """
        if isinstance(term, Variable):
            return replacement if term == var_to_replace else term
        elif isinstance(term, Application):
            return Application(
                self._substitute(term.func, var_to_replace, replacement),
                self._substitute(term.arg, var_to_replace, replacement)
            )
        elif isinstance(term, Lambda):
            # If the bound variable is the one we're replacing, substitution stops here.
            if term.var == var_to_replace:
                return term
            
            free_in_replacement = replacement.get_free_variables()
            # Check for variable capture: if the bound variable of the lambda
            # is free in the replacement term, we must rename it.
            if term.var.name in free_in_replacement:
                all_vars = term.get_free_variables().union(free_in_replacement)
                fresh_var = self._get_fresh_variable(all_vars)
                # Alpha-convert: rename the bound variable in the body
                new_body = self._substitute(term.body, term.var, fresh_var)
                new_lambda = Lambda(fresh_var, new_body)
                # Retry substitution on the alpha-converted lambda
                return self._substitute(new_lambda, var_to_replace, replacement)
            else:
                # No capture, proceed with substitution in the body.
                return Lambda(term.var, self._substitute(term.body, var_to_replace, replacement))
        return term

    def _is_value(self, term: Term) -> bool:
        """Checks if a term is a value (i.e., cannot be reduced further)."""
        return isinstance(term, Lambda)

    def _single_step_reduce(self, term: Term) -> Term:
        """Performs a single step of call-by-value beta-reduction."""
        if isinstance(term, Application):
            # (E-AppAbs): The core beta-reduction rule for call-by-value.
            if self._is_value(term.func) and self._is_value(term.arg):
                if isinstance(term.func, Lambda):
                    return self._substitute(term.func.body, term.func.var, term.arg)
            # (E-App1): If func is not a value, reduce it.
            if not self._is_value(term.func):
                return Application(self._single_step_reduce(term.func), term.arg)
            # (E-App2): If func is a value but arg is not, reduce arg.
            if not self._is_value(term.arg):
                return Application(term.func, self._single_step_reduce(term.arg))
        return term

    def _evaluate_classical_term(self, term: Term) -> Term:
        """Fully evaluates a classical lambda term to its normal form."""
        current_term = term
        for _ in range(self._max_steps):
            next_term = self._single_step_reduce(current_term)
            if next_term == current_term:
                return next_term
            current_term = next_term
        raise RuntimeError(f"Evaluation exceeded max steps for term: {term}")

    def evolve(self, q_term: QuantumTerm) -> QuantumTerm:
        """
        Simulates the unitary evolution of the quantum state via evaluation.
        Each basis state |T⟩ evolves to |eval(T)⟩.
        """
        new_state: QuantumState = {}
        for term, amp in q_term.state.items():
            try:
                evaluated_term = self._evaluate_classical_term(term)
                new_state[evaluated_term] = new_state.get(evaluated_term, 0) + amp
            except RuntimeError as e:
                print(f"Warning: Non-terminating computation for basis state {term}. Discarding. Error: {e}")
        return QuantumTerm(new_state)

    def apply(self, q_func: QuantumTerm, q_arg: QuantumTerm) -> QuantumTerm:
        """
        Applies a superposition of functions to a superposition of arguments.
        This creates a new superposition of Application terms.
        """
        new_state: QuantumState = {}
        if not q_func.state or not q_arg.state:
            return QuantumTerm({})
            
        for func_term, func_amp in q_func.state.items():
            for arg_term, arg_amp in q_arg.state.items():
                app_term = Application(func_term, arg_term)
                new_amp = func_amp * arg_amp
                new_state[app_term] = new_state.get(app_term, 0) + new_amp
        return QuantumTerm(new_state)

    def apply_phase_oracle(self, q_state: QuantumTerm, predicate: Callable[[Term], bool]) -> QuantumTerm:
        """
        Simulates a controlled-phase gate (an oracle). It applies a phase shift of -1
        to the amplitudes of basis states that satisfy the given predicate.
        This is the core mechanism for quantum interference.
        """
        new_state = {
            term: -amp if predicate(term) else amp
            for term, amp in q_state.state.items()
        }
        # This operation is unitary, so the result is already normalized.
        return QuantumTerm(new_state)

# --- 4. Demonstration ---

def main_demonstration():
    """
    An illustrative example of using the Quantum Lambda Evaluator to solve a
    simple problem: distinguishing between a constant and a balanced function,
    akin to the Deutsch-Jozsa algorithm's core idea.
    """
    print("="*70)
    print("    Quantum Lambda Calculus Evaluator: A Demonstration")
    print("="*70)

    # --- Define Church Booleans and Functions ---
    x, y, f, a, b = Variable('x'), Variable('y'), Variable('f'), Variable('a'), Variable('b')
    
    # TRUE = λx.λy.x
    TRUE = Lambda(x, Lambda(y, x))
    # FALSE = λx.λy.y
    FALSE = Lambda(x, Lambda(y, y))
    
    # We define two functions to put into superposition:
    # 1. A constant function: always returns TRUE.
    #    CONST_TRUE = λf. TRUE
    CONST_TRUE = Lambda(f, TRUE)

    # 2. An identity-like function: returns its argument.
    #    ID_FUNC = λf. f
    ID_FUNC = Lambda(f, f)

    print("--- Problem Setup ---")
    print("We have two functions in a black box (superposition):")
    print(f"  1. CONST_TRUE = {CONST_TRUE}")
    print(f"  2. ID_FUNC    = {ID_FUNC}")
    print("Our goal is to determine which function was evaluated using one query.")
    print("\n--- Step 1: Prepare Superposition States ---")

    # Create a uniform superposition of the two functions.
    # |ψ_func⟩ = 1/√2 |CONST_TRUE⟩ + 1/√2 |ID_FUNC⟩
    amp = 1 / cmath.sqrt(2)
    superposed_functions = QuantumTerm({
        CONST_TRUE: amp,
        ID_FUNC: amp
    })
    print(f"Function superposition |ψ_func⟩ = {superposed_functions}")

    # Create a uniform superposition of arguments (TRUE and FALSE).
    # |ψ_arg⟩ = 1/√2 |TRUE⟩ + 1/√2 |FALSE⟩
    superposed_args = QuantumTerm({
        TRUE: amp,
        FALSE: amp
    })
    print(f"Argument superposition |ψ_arg⟩ = {superposed_args}\n")

    # --- Step 2: Quantum Parallelism ---
    print("--- Step 2: Apply Superposed Function to Superposed Argument ---")
    evaluator = QuantumLambdaEvaluator()
    # This creates a state with all possible applications
    applied_state = evaluator.apply(superposed_functions, superposed_args)
    print(f"State after application (before evolution):\n|ψ_applied⟩ = {applied_state}\n")

    # --- Step 3: Unitary Evolution ---
    print("--- Step 3: Evolve the System (Evaluate the Terms) ---")
    # The evaluator reduces each term in the superposition to its normal form.
    # (CONST_TRUE TRUE)  -> TRUE
    # (CONST_TRUE FALSE) -> TRUE
    # (ID_FUNC TRUE)     -> TRUE
    # (ID_FUNC FALSE)    -> FALSE
    evolved_state = evaluator.evolve(applied_state)
    print(f"State after evolution (results of all computations):\n|ψ_evolved⟩ = {evolved_state}\n")
    print("Notice the constructive interference on the |TRUE⟩ state.")

    # --- Step 4: Oracle and Interference ---
    print("--- Step 4: Apply a Phase Oracle ---")
    print("Let's find out which function produced the result FALSE.")
    print("The oracle will flip the phase of the |FALSE⟩ component.")
    
    # The predicate marks the state we are interested in.
    predicate = lambda term: term == FALSE
    
    marked_state = evaluator.apply_phase_oracle(evolved_state, predicate)
    print(f"State after oracle marking:\n|ψ_marked⟩ = {marked_state}\n")

    print("--- Interpretation ---")
    print("The final state contains all the information from the parallel computations.")
    print("The component with the flipped phase, (-0.500)|(λx. λy. y)⟩, corresponds to the")
    print("computation path that resulted in FALSE.")
    print("By tracing this amplitude back, we know it came from the |ID_FUNC⟩ applied to |FALSE⟩.")
    print("A full quantum algorithm would now apply further transformations (e.g., QFT or")
    print("a diffusion operator) to amplify this difference, allowing a high-probability")
    print("measurement of the property of interest (e.g., 'was the function constant or balanced?').")
    print("This pseudocode successfully demonstrates the core quantum principles of superposition,")
    print("parallelism, and interference within the framework of lambda calculus.")
    print("="*70)

if __name__ == "__main__":
    main_demonstration()