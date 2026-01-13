class TypeError(Exception):
    """Custom exception for type errors during operator application."""
    pass

class OperatorTypeChecker:
    """
    Pseudocode for the type system component responsible for enforcing
    non-commutative operator algebra during type checking.

    This class defines rules for operators, including their commutativity,
    and checks if an operator application is valid given the operand types.
    It specifically handles non-commutative operators by requiring an exact
    match for the ordered pair of operand types, reflecting the principle
    that in certain algebraic structures (like those found in quantum mechanics),
    the order of operations fundamentally alters the outcome and thus the type.
    """

    def __init__(self):
        """
        Initializes the OperatorTypeChecker with an empty set of operator rules.
        Rules are stored as:
        {
            'operator_symbol': {
                'is_commutative': bool,
                'valid_operand_type_pairs': [
                    (left_type_str, right_type_str, result_type_str),
                    ...
                ]
            }
        }
        The type strings (e.g., "Int", "Matrix[N,M]") are simplified representations
        for this pseudocode; in a full system, these would be rich Type objects.
        """
        self._operator_rules: dict[str, dict] = {}

    def register_operator_rule(self,
                               operator_symbol: str,
                               is_commutative: bool,
                               operand_type_pairs: list[tuple[str, str, str]]):
        """
        Registers or updates a rule for a specific operator.

        Args:
            operator_symbol: The string representation of the operator (e.g., '+', '*', '@', '⊗').
            is_commutative: True if the operator is commutative (A op B == B op A), False otherwise.
                            For non-commutative operators, the order of operands is critical.
            operand_type_pairs: A list of valid (left_type, right_type, result_type) tuples.
                                Each tuple specifies a valid combination of operand types
                                and the type of the result. For non-commutative operators,
                                the order within these tuples is strictly enforced.
        
        Raises:
            ValueError: If input arguments are invalid.
        """
        if not isinstance(operator_symbol, str) or not operator_symbol:
            raise ValueError("Operator symbol must be a non-empty string.")
        if not isinstance(is_commutative, bool):
            raise ValueError("is_commutative must be a boolean.")
        if not isinstance(operand_type_pairs, list):
            raise ValueError("operand_type_pairs must be a list.")
        for pair in operand_type_pairs:
            if not (isinstance(pair, tuple) and len(pair) == 3 and
                    all(isinstance(t, str) for t in pair)):
                raise ValueError("Each operand_type_pair must be a tuple of three strings "
                                 "(left_type, right_type, result_type).")

        self._operator_rules[operator_symbol] = {
            'is_commutative': is_commutative,
            'valid_operand_type_pairs': operand_type_pairs
        }
        # In a more advanced system, for commutative operators, one might
        # automatically generate and store reversed pairs to optimize lookup.
        # For this pseudocode, we handle commutativity dynamically during checking.

    def _get_operator_rule(self, operator_symbol: str) -> dict:
        """
        Retrieves the rule for a given operator symbol.

        Args:
            operator_symbol: The symbol of the operator to look up.

        Returns:
            The dictionary containing the operator's rules.

        Raises:
            TypeError: If the operator is not registered in the type system.
        """
        rule = self._operator_rules.get(operator_symbol)
        if rule is None:
            raise TypeError(f"Operator '{operator_symbol}' is not defined in the type system. "
                            "Quantum laws demand defined operations.")
        return rule

    def check_operator_application(self,
                                   operator_symbol: str,
                                   left_operand_type: str,
                                   right_operand_type: str) -> str:
        """
        Checks if an operator application is type-valid and returns the resulting type.
        This method rigorously enforces non-commutative algebra rules, where the order
        of operands is paramount, akin to how quantum operators do not always commute.

        Args:
            operator_symbol: The operator being applied (e.g., '+', '@', '⊗').
            left_operand_type: The type string of the left-hand operand.
            right_operand_type: The type string of the right-hand operand.

        Returns:
            The resulting type string if the operation is valid.

        Raises:
            TypeError: If the operator is not defined, or the operand types are
                       incompatible for the given operator and its commutativity rules.
        """
        rule = self._get_operator_rule(operator_symbol)
        is_commutative = rule['is_commutative']
        valid_pairs = rule['valid_operand_type_pairs']

        # First, attempt to find a direct match for the (left, right) operand types.
        # In a real type system, `_is_assignable` would perform subtyping checks.
        # For this pseudocode, we assume exact string match for simplicity.
        for l_rule_type, r_rule_type, result_type in valid_pairs:
            if self._is_assignable(left_operand_type, l_rule_type) and \
               self._is_assignable(right_operand_type, r_rule_type):
                return result_type

        # If no direct match, and the operator is commutative, check the reversed pair.
        # This allows registering (A, B) and implicitly supporting (B, A).
        if is_commutative:
            for l_rule_type, r_rule_type, result_type in valid_pairs:
                # Check if the *reversed* actual operands match a *registered* pair
                # (right_operand_type, left_operand_type) against (l_rule_type, r_rule_type)
                if self._is_assignable(right_operand_type, l_rule_type) and \
                   self._is_assignable(left_operand_type, r_rule_type):
                    return result_type

        # If no valid pair found after all checks, raise a type error.
        error_message = (
            f"Type mismatch for operator '{operator_symbol}': "
            f"Cannot apply '{operator_symbol}' to operands of type "
            f"'{left_operand_type}' and '{right_operand_type}'. "
        )
        if not is_commutative:
            error_message += "This operator is non-commutative; the order of operands is critical and cannot be reversed."
        else:
            error_message += "No compatible type combination found."

        raise TypeError(error_message)

    # --- Placeholder for more advanced type system features ---

    def _is_assignable(self, source_type: str, target_type: str) -> bool:
        """
        Pseudocode for checking if a `source_type` can be assigned to a `target_type`.
        In a full type system, this would involve complex logic for subtyping,
        interface conformance, structural compatibility, etc.
        For this simplified pseudocode, we assume exact type string equality.
        """
        # Example: "Int" is assignable to "Number", but "Number" is not to "Int".
        # For now, a direct match is sufficient for demonstration.
        return source_type == target_type

    def _resolve_type_hierarchy(self, type_name: str) -> 'TypeObject':
        """
        Pseudocode for resolving a type name string to a more complex TypeObject.
        This TypeObject would contain detailed information about its supertypes,
        members, generic parameters, etc., enabling sophisticated type checks.
        In a real system, this would query a global type registry or AST.
        For this pseudocode, we simply return the string itself, implying it's a basic type.
        """
        # This method would be crucial for `_is_assignable` to work with subtyping.
        return type_name # Placeholder: returns the string as its "resolved" form.