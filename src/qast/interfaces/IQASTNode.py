import abc
from typing import Any, List, Optional, Dict, Union

# Forward declaration for type hinting.
# In a full project, IQASTOperation would be defined in its own interface file
# (e.g., 'src/qast/interfaces/IQASTOperation.py') and imported.
# For this interface definition, we use a string literal for forward referencing.
# from .IQASTOperation import IQASTOperation

class IQASTNode(abc.ABC):
    """
    Core interface for a generic Quantum Abstract Syntax Tree (QAST) node.

    This abstract base class defines the fundamental contract for any element
    within a QAST, encompassing its identity, state representation, operational
    capabilities, structural relationships, and interaction within a layered
    quantum computation model. It serves as a blueprint for all concrete QAST
    node implementations, ensuring a consistent API across diverse node types
    like qubits, gates, measurements, and classical registers.
    """

    @property
    @abc.abstractmethod
    def node_id(self) -> str:
        """
        A globally unique identifier for this specific QAST node instance.
        This ID should be immutable after node creation.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def node_type(self) -> str:
        """
        The conceptual type of this QAST node, categorizing its role within the
        quantum computation. Examples include 'qubit', 'gate', 'measurement',
        'classical_register', 'circuit_block', 'initialization', 'barrier', etc.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_state_representation(self) -> Any:
        """
        Returns a representation of the quantum state, classical state, or
        symbolic expression associated with this node. The specific return type
        is context-dependent and could be a state vector (e.g., numpy array),
        a density matrix, a classical bit value, a symbolic tensor, or a
        reference to a global quantum state object.

        This method is crucial for understanding the node's contribution to
        the overall quantum computation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def apply_operation(self, operation: 'IQASTOperation') -> None:
        """
        Applies a quantum or classical operation to this node.
        The operation might modify the node's internal state, its properties,
        or its relationships with child nodes. This method is central to
        building and transforming the QAST.

        Args:
            operation: An instance of IQASTOperation representing the action
                       to be applied.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_children(self) -> List['IQASTNode']:
        """
        Returns a list of child nodes directly connected to this node in the QAST's
        hierarchical or graph structure. For leaf nodes, this list will be empty.
        The order of children might be significant depending on the node type.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_child(self, child_node: 'IQASTNode') -> None:
        """
        Adds a specified child node to this node's list of children.
        Implementations should handle potential duplicate additions or
        structural constraints.

        Args:
            child_node: The IQASTNode instance to add as a child.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_child(self, child_node: 'IQASTNode') -> None:
        """
        Removes a specified child node from this node's list of children.
        Implementations should ensure proper disconnection and potentially
        handle orphaned nodes or structural integrity.

        Args:
            child_node: The IQASTNode instance to remove.

        Raises:
            ValueError: If the `child_node` is not found among the current children.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_parent(self) -> Optional['IQASTNode']:
        """
        Returns the parent node of this node in the QAST.
        Returns `None` if this node is a root node (i.e., has no parent).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_parent(self, parent_node: Optional['IQASTNode']) -> None:
        """
        Sets the parent node for this node. This method is typically used
        during tree construction or restructuring.

        Args:
            parent_node: The IQASTNode instance to set as parent, or `None`
                         if this node is becoming a root.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_layer_index(self) -> int:
        """
        Returns the conceptual layer index of this node within the QAST's
        layered structure. This index often corresponds to a time step or
        sequential execution order in a quantum circuit. It is crucial for
        dependency tracking, scheduling, and visualization.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_layer_index(self, index: int) -> None:
        """
        Sets the conceptual layer index for this node. This method allows
        for dynamic reordering or optimization of the QAST's layered structure.

        Args:
            index: The integer index representing the layer.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def propagate_quantum_effect(self, context: Dict[str, Any]) -> Any:
        """
        Simulates or calculates the quantum effect of this node, propagating
        its influence to subsequent nodes or layers within a given quantum context.
        This method embodies the "quantum becomes the law" principle, handling
        complex interactions such as entanglement, superposition, interference,
        and decoherence.

        The `context` dictionary provides necessary global information, such as
        the current global quantum state, qubit mapping, noise model parameters,
        or classical measurement outcomes.

        Args:
            context: A dictionary containing relevant simulation/propagation
                     parameters and the current global state.

        Returns:
            An updated quantum state, a set of classical outcomes, or a symbolic
            representation of the propagated effect, depending on the node type
            and the simulation backend.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_qasm(self) -> str:
        """
        Generates a QASM (Quantum Assembly Language) string representation
        of the operations or state associated with this node. This is vital
        for interoperability with quantum hardware and simulators.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_latex(self) -> str:
        """
        Generates a LaTeX string representation (e.g., for circuit diagrams
        using `qcircuit`, mathematical expressions, or state vectors) of this node.
        This facilitates high-quality documentation and visualization.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self) -> bool:
        """
        Performs internal consistency checks and validates the node's state,
        properties, and connections according to QAST rules and quantum mechanics
        principles. This method helps ensure the integrity and correctness of
        the quantum program represented by the QAST.

        Returns:
            True if the node is valid, False otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns a dictionary of arbitrary, user-defined metadata associated
        with this node. This allows for flexible extension of node properties
        without modifying the core interface.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Sets a specific metadata key-value pair for this node.

        Args:
            key: The string key for the metadata entry.
            value: The value to associate with the key.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def traverse(self, visitor: Any) -> None:
        """
        Allows for the implementation of the Visitor design pattern, enabling
        external algorithms to traverse the QAST starting from this node.
        The visitor object typically defines methods like `visit_node(node)`
        that are called for each visited node.

        Args:
            visitor: An object conforming to a visitor interface, with methods
                     to process different node types.
        """
        raise NotImplementedError