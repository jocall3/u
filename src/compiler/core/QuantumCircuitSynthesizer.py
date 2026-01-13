class QASTNode:
    """Base class for all nodes in the Quantum Abstract Syntax Tree (QAST)."""
    pass

class QASTProgram(QASTNode):
    """Represents the root of a QAST, containing declarations and operations."""
    def __init__(self, declarations: list, operations: list):
        self.declarations = declarations  # List of QASTQubitDeclaration, QASTClassicalDeclaration
        self.operations = operations      # List of QASTGateApplication, QASTMeasurement, QASTConditional, etc.

class QASTQubitDeclaration(QASTNode):
    """Represents the declaration of a quantum register or single qubit."""
    def __init__(self, name: str, size: int = 1):
        self.name = name
        self.size = size  # Number of qubits in the register

class QASTClassicalDeclaration(QASTNode):
    """Represents the declaration of a classical register or single bit."""
    def __init__(self, name: str, size: int = 1):
        self.name = name
        self.size = size  # Number of classical bits in the register

class QASTGateApplication(QASTNode):
    """Represents the application of a quantum gate."""
    def __init__(self, gate_type: str, qubits: list[str], params: dict = None):
        self.gate_type = gate_type  # e.g., "H", "CNOT", "RZ"
        self.qubits = qubits        # List of QAST qubit identifiers (e.g., "q[0]", "q[1]")
        self.params = params if params is not None else {} # Dictionary of gate parameters (e.g., {"theta": 0.5})

class QASTMeasurement(QASTNode):
    """Represents a quantum measurement operation."""
    def __init__(self, qubit: str, classical_bit: str):
        self.qubit = qubit            # QAST qubit identifier to measure
        self.classical_bit = classical_bit # QAST classical bit identifier to store the result

class QASTConditional(QASTNode):
    """Represents a classically controlled quantum operation."""
    def __init__(self, classical_register: str, value: int, operation: QASTNode):
        self.classical_register = classical_register # QAST classical bit/register identifier
        self.value = value                           # Integer value to compare against
        self.operation = operation                   # A QASTNode (e.g., QASTGateApplication) to execute conditionally

class QASTBarrier(QASTNode):
    """Represents a quantum barrier instruction."""
    def __init__(self, qubits: list[str] = None):
        self.qubits = qubits # List of QAST qubit identifiers, or None for all active qubits

class Gate:
    """
    Represents a single quantum gate in the synthesized circuit.
    This is a generic representation, not tied to any specific quantum SDK.
    """
    def __init__(self, name: str, qubits: list[int], params: dict = None, classical_condition: tuple = None):
        self.name = name  # Name of the gate (e.g., "H", "CNOT", "MEASURE", "BARRIER")
        self.qubits = qubits  # List of physical qubit indices (integers)
        self.params = params if params is not None else {}  # Dictionary of gate parameters
        # classical_condition: (classical_bit_index, value) if the gate is classically controlled
        self.classical_condition = classical_condition

    def __repr__(self):
        cond_str = f", cond={self.classical_condition}" if self.classical_condition else ""
        return f"Gate(name='{self.name}', qubits={self.qubits}, params={self.params}{cond_str})"

class QuantumCircuit:
    """
    Represents a synthesized quantum circuit as a sequence of gates.
    This is a high-level, hardware-agnostic representation.
    """
    def __init__(self):
        self.num_qubits: int = 0
        self.num_classical_bits: int = 0
        self.gates: list[Gate] = []
        self.qubit_map: dict[str, int] = {}       # Maps QAST qubit identifiers to physical indices
        self.classical_map: dict[str, int] = {}   # Maps QAST classical bit identifiers to physical indices

    def add_gate(self, gate: Gate):
        """Adds a gate to the circuit."""
        self.gates.append(gate)

    def __repr__(self):
        gates_str = "\n    ".join(str(g) for g in self.gates)
        return (f"QuantumCircuit(\n"
                f"  num_qubits={self.num_qubits},\n"
                f"  num_classical_bits={self.num_classical_bits},\n"
                f"  qubit_map={self.qubit_map},\n"
                f"  classical_map={self.classical_map},\n"
                f"  gates=[\n    {gates_str}\n  ]\n)")

class QuantumCircuitSynthesizer:
    """
    Core quantum circuit synthesizer responsible for translating a Quantum Abstract Syntax Tree (QAST)
    into a sequence of quantum gates represented by a QuantumCircuit object.
    """
    def __init__(self):
        self.circuit: QuantumCircuit = None
        self._qubit_counter: int = 0
        self._classical_counter: int = 0
        self._qast_qubit_to_physical: dict[str, int] = {}
        self._qast_classical_to_physical: dict[str, int] = {}

    def _get_physical_qubit(self, qast_qubit_id: str) -> int:
        """
        Retrieves or allocates a physical qubit index for a given QAST qubit identifier.
        """
        if qast_qubit_id not in self._qast_qubit_to_physical:
            self._qast_qubit_to_physical[qast_qubit_id] = self._qubit_counter
            self._qubit_counter += 1
        return self._qast_qubit_to_physical[qast_qubit_id]

    def _get_physical_classical_bit(self, qast_classical_id: str) -> int:
        """
        Retrieves or allocates a physical classical bit index for a given QAST classical identifier.
        """
        if qast_classical_id not in self._qast_classical_to_physical:
            self._qast_classical_to_physical[qast_classical_id] = self._classical_counter
            self._classical_counter += 1
        return self._qast_classical_to_physical[qast_classical_id]

    def synthesize(self, qast_program: QASTProgram) -> QuantumCircuit:
        """
        Translates a Quantum Abstract Syntax Tree (QAST) into a sequence of quantum gates
        represented by a QuantumCircuit object.

        This method performs a two-pass synthesis:
        1. Processes declarations to establish a complete mapping from QAST identifiers
           to physical qubit/classical bit indices.
        2. Processes operations, translating each QAST operation node into one or more
           `Gate` objects and adding them to the `QuantumCircuit`.

        Args:
            qast_program: The root node of the Quantum Abstract Syntax Tree.

        Returns:
            A QuantumCircuit object representing the synthesized quantum program.
        """
        self.circuit = QuantumCircuit()
        self._qubit_counter = 0
        self._classical_counter = 0
        self._qast_qubit_to_physical = {}
        self._qast_classical_to_physical = {}

        # Pass 1: Process declarations to establish initial qubit/classical bit maps.
        # This ensures all declared registers have allocated physical indices before operations
        # are processed, preventing dynamic allocation during operation processing for declared items.
        for decl in qast_program.declarations:
            if isinstance(decl, QASTQubitDeclaration):
                for i in range(decl.size):
                    qast_id = f"{decl.name}[{i}]" if decl.size > 1 else decl.name
                    self._get_physical_qubit(qast_id)  # Allocate physical index
            elif isinstance(decl, QASTClassicalDeclaration):
                for i in range(decl.size):
                    qast_id = f"{decl.name}[{i}]" if decl.size > 1 else decl.name
                    self._get_physical_classical_bit(qast_id)  # Allocate physical index
            # Future: Handle other declaration types like custom gates, etc.
            else:
                pass # Ignore unknown declaration types for pseudocode simplicity

        # Populate the circuit's maps and counts based on the first pass's allocations.
        self.circuit.num_qubits = self._qubit_counter
        self.circuit.num_classical_bits = self._classical_counter
        self.circuit.qubit_map = self._qast_qubit_to_physical.copy()
        self.circuit.classical_map = self._qast_classical_to_physical.copy()

        # Pass 2: Process operations and add gates to the circuit.
        for operation_node in qast_program.operations:
            self._process_operation(operation_node)

        return self.circuit

    def _process_operation(self, node: QASTNode, classical_condition: tuple = None):
        """
        Recursively processes a QAST operation node and adds corresponding gates to the circuit.
        Handles classical conditions for nested operations.

        Args:
            node: The current QAST operation node to process.
            classical_condition: A tuple (classical_bit_index, value) if the current
                                 operation is classically controlled, otherwise None.
        """
        if isinstance(node, QASTGateApplication):
            physical_qubits = [self._get_physical_qubit(q) for q in node.qubits]
            gate = Gate(node.gate_type, physical_qubits, node.params, classical_condition)
            self.circuit.add_gate(gate)

        elif isinstance(node, QASTMeasurement):
            physical_qubit = self._get_physical_qubit(node.qubit)
            physical_classical_bit = self._get_physical_classical_bit(node.classical_bit)
            # Measurement is a special gate type; its classical target is often in its parameters.
            gate = Gate("MEASURE", [physical_qubit], {"target_classical": physical_classical_bit}, classical_condition)
            self.circuit.add_gate(gate)

        elif isinstance(node, QASTConditional):
            # For conditional operations, the condition applies to the *inner* operation.
            # This pseudocode assumes `classical_register` refers to a single classical bit.
            # A full compiler might handle comparisons against multi-bit classical registers.
            physical_classical_bit_index = self._get_physical_classical_bit(node.classical_register)
            condition = (physical_classical_bit_index, node.value)
            # Recursively process the inner operation with the new classical condition.
            self._process_operation(node.operation, condition)

        elif isinstance(node, QASTBarrier):
            # If qubits are specified, apply barrier to them; otherwise, apply to all allocated qubits.
            physical_qubits = ([self._get_physical_qubit(q) for q in node.qubits]
                               if node.qubits else list(self._qast_qubit_to_physical.values()))
            gate = Gate("BARRIER", physical_qubits, classical_condition=classical_condition)
            self.circuit.add_gate(gate)

        else:
            # This handles any QAST node types that are not explicitly supported by the synthesizer.
            raise ValueError(f"Unsupported QAST node type encountered during synthesis: {type(node).__name__}")