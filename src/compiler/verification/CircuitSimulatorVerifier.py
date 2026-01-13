import numpy as np
from typing import List, Tuple, Dict, Union, Callable

class CircuitSimulatorVerifier:
    """
    Pseudocode for a quantum simulator used to verify the generated circuit's behavior
    before final emission. This simulator strictly adheres to quantum mechanical
    principles, where "quantum becomes the law."

    It provides a conceptual, step-by-step simulation of quantum circuits,
    handling state evolution under unitary gates and probabilistic measurements.
    """

    def __init__(self, num_qubits: int):
        """
        Initializes the quantum simulator with a specified number of qubits.
        The initial state is always |0...0⟩.

        Args:
            num_qubits (int): The number of qubits in the quantum system.
        """
        if not isinstance(num_qubits, int) or num_qubits <= 0:
            raise ValueError("Number of qubits must be a positive integer.")

        self.num_qubits = num_qubits
        self.state_vector = self._initialize_state()
        self.classical_register: Dict[int, int] = {} # To store measurement results

        # Pre-defined common quantum gates
        self.gates = {
            "I": np.array([[1, 0], [0, 1]], dtype=complex),
            "X": np.array([[0, 1], [1, 0]], dtype=complex), # Pauli-X (NOT)
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex), # Pauli-Y
            "Z": np.array([[1, 0], [0, -1]], dtype=complex), # Pauli-Z
            "H": 1/np.sqrt(2) * np.array([[1, 1], [1, -1]], dtype=complex), # Hadamard
            "S": np.array([[1, 0], [0, 1j]], dtype=complex), # Phase gate (sqrt(Z))
            "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex), # Pi/8 gate (sqrt(S))
            "CNOT": np.array([ # Controlled-NOT (control, target)
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ], dtype=complex),
            "SWAP": np.array([ # SWAP gate
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ], dtype=complex),
        }

    def _initialize_state(self) -> np.ndarray:
        """
        Initializes the quantum state vector to |0...0⟩.
        This corresponds to the first basis state (index 0) having amplitude 1,
        and all other states having amplitude 0.

        Returns:
            np.ndarray: The initial state vector.
        """
        state_size = 2**self.num_qubits
        state = np.zeros(state_size, dtype=complex)
        state[0] = 1.0 + 0.0j # |0...0> state
        return state

    def _get_full_gate_matrix(self, gate_matrix: np.ndarray, target_qubits: Union[int, List[int]]) -> np.ndarray:
        """
        Constructs the full N-qubit gate matrix for a given gate acting on specific qubits.
        This involves using Kronecker products to combine the gate with identity matrices
        for non-target qubits.

        Args:
            gate_matrix (np.ndarray): The matrix of the gate to apply (e.g., 2x2 for single-qubit, 4x4 for two-qubit).
            target_qubits (Union[int, List[int]]): The index or list of indices of the qubits
                                                    the gate acts upon.

        Returns:
            np.ndarray: The full 2^N x 2^N matrix representing the gate operation on the
                        entire quantum system.
        """
        if isinstance(target_qubits, int):
            target_qubits = [target_qubits]

        if not all(0 <= q < self.num_qubits for q in target_qubits):
            raise ValueError(f"Target qubit indices {target_qubits} are out of bounds for {self.num_qubits} qubits.")

        num_gate_qubits = int(np.log2(gate_matrix.shape[0]))
        if num_gate_qubits != len(target_qubits):
            raise ValueError(f"Gate matrix expects {num_gate_qubits} qubits, but {len(target_qubits)} were provided.")

        # Sort target qubits to ensure consistent Kronecker product order
        # This is crucial for multi-qubit gates like CNOT where control/target order matters
        # For CNOT, the gate_matrix is typically defined for (control, target)
        # If target_qubits is [q_control, q_target], the gate_matrix should match this order.
        # For simplicity, we assume the gate_matrix is defined for qubits in the order they appear in target_qubits.

        # Initialize with identity matrix for the first qubit (or an empty matrix if no qubits before first target)
        full_gate = np.array([[1]], dtype=complex) # Placeholder for initial Kronecker product

        # Build the full gate matrix by iterating through all qubits
        # and applying the gate or identity as appropriate.
        # This approach correctly handles arbitrary qubit positions.
        # Example: H on qubit 1 in a 3-qubit system (I x H x I)
        # Example: CNOT on (0, 2) in a 3-qubit system (CNOT_02 x I_1)
        
        # This is a more complex construction for arbitrary multi-qubit gates
        # and requires careful handling of basis states.
        # A simpler approach for verification might be to define specific multi-qubit gates
        # for specific qubit combinations, or to use a more abstract representation.

        # For a general N-qubit system, applying a K-qubit gate to target_qubits:
        # We need to construct a 2^N x 2^N matrix.
        # The most robust way is to iterate through all 2^N basis states,
        # apply the K-qubit gate to the relevant K bits, and map to the new basis state.

        # Let's simplify for common cases: single-qubit and two-qubit gates.
        # For single-qubit gates:
        if num_gate_qubits == 1:
            q_target = target_qubits[0]
            op_list = [self.gates["I"]] * self.num_qubits
            op_list[q_target] = gate_matrix
            full_gate = op_list[0]
            for i in range(1, self.num_qubits):
                full_gate = np.kron(full_gate, op_list[i])
            return full_gate
        
        # For two-qubit gates (like CNOT, SWAP):
        elif num_gate_qubits == 2:
            q1, q2 = target_qubits[0], target_qubits[1]
            
            # This is a common way to construct the full CNOT matrix for arbitrary qubits
            # It's more involved than simple Kronecker products of I and the gate.
            # A CNOT(control, target) flips target if control is 1.
            # We need to build the matrix element by element or use a permutation approach.

            # Let's use a more direct construction for verification purposes.
            # The CNOT gate matrix (4x4) is defined for qubits 0 and 1.
            # If we want CNOT(q1, q2), we need to permute the basis states.
            
            # A more general approach for multi-qubit gates:
            # Create an identity matrix of size 2^N
            full_gate = np.eye(2**self.num_qubits, dtype=complex)
            
            # Iterate through all computational basis states
            for i in range(2**self.num_qubits):
                # Convert index i to its binary representation (qubit states)
                binary_state = [int(x) for x in bin(i)[2:].zfill(self.num_qubits)]
                
                # Extract the states of the target qubits
                target_qubit_states = [binary_state[q] for q in target_qubits]
                
                # Convert target_qubit_states to an integer index for the small gate matrix
                target_idx = sum(s * (2**(len(target_qubits) - 1 - k)) for k, s in enumerate(target_qubit_states))
                
                # Apply the small gate matrix to the target part of the state
                # This gives the amplitudes for the output states of the target qubits
                output_amplitudes = gate_matrix[target_idx, :]
                
                # For each possible output state of the target qubits:
                for j in range(2**num_gate_qubits):
                    # Convert j back to binary for the target qubits
                    output_target_states = [int(x) for x in bin(j)[2:].zfill(num_gate_qubits)]
                    
                    # Construct the full output binary state
                    new_binary_state = list(binary_state) # Copy
                    for k, q_idx in enumerate(target_qubits):
                        new_binary_state[q_idx] = output_target_states[k]
                    
                    # Convert the new binary state back to an integer index
                    new_idx = int("".join(map(str, new_binary_state)), 2)
                    
                    # Set the corresponding element in the full gate matrix
                    # This is (new_idx, i) because we are transforming state i to state new_idx
                    full_gate[new_idx, i] = output_amplitudes[j]
            
            return full_gate

        else:
            raise NotImplementedError(f"Gate construction for {num_gate_qubits}-qubit gates not fully generalized yet.")


    def apply_gate(self, gate_name: str, target_qubits: Union[int, List[int]], params: Dict = None):
        """
        Applies a named quantum gate to the specified qubits.
        The state vector is updated by multiplying with the corresponding unitary matrix.

        Args:
            gate_name (str): The name of the gate (e.g., "H", "CNOT", "X").
            target_qubits (Union[int, List[int]]): The index or list of indices of the qubits
                                                    the gate acts upon. For multi-qubit gates,
                                                    the order in the list matters (e.g., control, target).
            params (Dict, optional): Additional parameters for parameterized gates (e.g., "Rx", "Ry", "Rz").
                                     Expected to contain a 'theta' key for rotation angles.
        """
        if isinstance(target_qubits, int):
            target_qubits = [target_qubits]

        if not all(0 <= q < self.num_qubits for q in target_qubits):
            raise ValueError(f"Target qubit indices {target_qubits} are out of bounds for {self.num_qubits} qubits.")

        gate_matrix = None
        if gate_name in self.gates:
            gate_matrix = self.gates[gate_name]
        elif gate_name in ["Rx", "Ry", "Rz"]:
            if params is None or 'theta' not in params:
                raise ValueError(f"Parameterized gate '{gate_name}' requires 'theta' parameter.")
            theta = params['theta']
            if gate_name == "Rx":
                gate_matrix = np.array([
                    [np.cos(theta/2), -1j * np.sin(theta/2)],
                    [-1j * np.sin(theta/2), np.cos(theta/2)]
                ], dtype=complex)
            elif gate_name == "Ry":
                gate_matrix = np.array([
                    [np.cos(theta/2), -np.sin(theta/2)],
                    [np.sin(theta/2), np.cos(theta/2)]
                ], dtype=complex)
            elif gate_name == "Rz":
                gate_matrix = np.array([
                    [np.exp(-1j * theta/2), 0],
                    [0, np.exp(1j * theta/2)]
                ], dtype=complex)
        else:
            raise ValueError(f"Unknown gate: {gate_name}")

        full_gate_op = self._get_full_gate_matrix(gate_matrix, target_qubits)
        self.state_vector = np.dot(full_gate_op, self.state_vector)
        
        # Ensure normalization (due to floating point errors)
        self.state_vector = self.state_vector / np.linalg.norm(self.state_vector)

    def _get_probabilities(self) -> np.ndarray:
        """
        Calculates the probabilities of measuring each computational basis state.

        Returns:
            np.ndarray: An array of probabilities, where each element corresponds
                        to the probability of measuring the state represented by its index.
        """
        return np.abs(self.state_vector)**2

    def measure(self, qubits_to_measure: Union[int, List[int]], shots: int = 1) -> List[List[int]]:
        """
        Performs a projective measurement on the specified qubits.
        This collapses the quantum state and yields classical bit results.

        Args:
            qubits_to_measure (Union[int, List[int]]): The index or list of indices of the qubits to measure.
            shots (int): The number of times to repeat the measurement.

        Returns:
            List[List[int]]: A list of measurement outcomes. Each inner list represents
                             a single shot, containing the classical bits for the measured qubits
                             in the order they were provided.
        """
        if isinstance(qubits_to_measure, int):
            qubits_to_measure = [qubits_to_measure]

        if not all(0 <= q < self.num_qubits for q in qubits_to_measure):
            raise ValueError(f"Qubit indices {qubits_to_measure} are out of bounds for {self.num_qubits} qubits.")

        probabilities = self._get_probabilities()
        outcomes = []

        for _ in range(shots):
            # Sample a single outcome based on probabilities
            measured_index = np.random.choice(len(self.state_vector), p=probabilities)
            
            # Convert the measured index to its binary representation
            measured_binary_state = [int(x) for x in bin(measured_index)[2:].zfill(self.num_qubits)]
            
            # Extract the classical bits for the specific qubits that were measured
            classical_bits = [measured_binary_state[q] for q in qubits_to_measure]
            outcomes.append(classical_bits)

            # Collapse the state: set amplitude of measured_index to 1 and others to 0
            # This is a strong measurement, collapsing the entire state to the measured basis state.
            # For verification, this is often sufficient.
            collapsed_state = np.zeros_like(self.state_vector)
            collapsed_state[measured_index] = 1.0 + 0.0j
            self.state_vector = collapsed_state
            
            # Store results in classical register (optional, for tracking)
            for i, q_idx in enumerate(qubits_to_measure):
                self.classical_register[q_idx] = classical_bits[i]

        return outcomes

    def get_state_vector(self) -> np.ndarray:
        """
        Returns the current quantum state vector.

        Returns:
            np.ndarray: The complex-valued state vector.
        """
        return self.state_vector

    def get_classical_register(self) -> Dict[int, int]:
        """
        Returns the current state of the classical register, storing the last
        measurement outcomes for each qubit.

        Returns:
            Dict[int, int]: A dictionary mapping qubit index to its last measured classical value.
        """
        return self.classical_register

    def reset_state(self):
        """
        Resets the simulator's quantum state back to the initial |0...0⟩ state.
        """
        self.state_vector = self._initialize_state()
        self.classical_register = {}

    def run_circuit(self, circuit_description: List[Tuple[str, Union[int, List[int]], Dict]]):
        """
        Executes a sequence of quantum operations defined in a circuit description.
        This is the primary entry point for verifying a generated circuit.

        Args:
            circuit_description (List[Tuple[str, Union[int, List[int]], Dict]]):
                A list of operations. Each operation is a tuple:
                (gate_name: str, target_qubits: Union[int, List[int]], params: Dict (optional))
                Example: [
                    ("H", 0, None),
                    ("CNOT", [0, 1], None),
                    ("Rx", 2, {"theta": np.pi/2}),
                    ("MEASURE", [0, 1], {"shots": 1024}) # Special operation for measurement
                ]

        Returns:
            Dict[str, Union[np.ndarray, List[List[int]]]]:
                A dictionary containing the final state vector and/or measurement results.
                Keys: 'final_state_vector', 'measurement_results'.
        """
        self.reset_state() # Ensure a clean start for each circuit run
        
        results = {
            "final_state_vector": None,
            "measurement_results": {}
        }

        for op in circuit_description:
            op_type = op[0]
            target_qubits = op[1]
            params = op[2] if len(op) > 2 else None

            if op_type == "MEASURE":
                shots = params.get("shots", 1) if params else 1
                measurement_outcomes = self.measure(target_qubits, shots=shots)
                # Store results by measured qubits, e.g., "0,1" -> [[0,0], [0,1], ...]
                key = ",".join(map(str, sorted(target_qubits)))
                results["measurement_results"][key] = measurement_outcomes
            else:
                self.apply_gate(op_type, target_qubits, params)
        
        results["final_state_vector"] = self.get_state_vector()
        return results

# Example Usage (for internal testing and demonstration):
if __name__ == "__main__":
    print("--- CircuitSimulatorVerifier Demonstration ---")

    # 1. Simulate a Bell State (2 qubits)
    print("\n--- Bell State Circuit (2 qubits) ---")
    bell_circuit = [
        ("H", 0),          # Hadamard on qubit 0
        ("CNOT", [0, 1]),  # CNOT with control 0, target 1
        ("MEASURE", [0, 1], {"shots": 1024}) # Measure both qubits
    ]

    simulator_bell = CircuitSimulatorVerifier(num_qubits=2)
    bell_results = simulator_bell.run_circuit(bell_circuit)

    print("Final State Vector (before measurement collapse):")
    print(bell_results["final_state_vector"])
    # Expected: [0.707, 0, 0, 0.707] for |00> + |11> (or similar, depending on phase)
    # After CNOT, the state should be 1/sqrt(2) * (|00> + |11>)
    # So, amplitudes for |00> and |11> should be 1/sqrt(2) ~ 0.707
    
    print("\nMeasurement Results (1024 shots):")
    measured_qubits_key = "0,1"
    if measured_qubits_key in bell_results["measurement_results"]:
        outcomes = bell_results["measurement_results"][measured_qubits_key]
        counts = {}
        for outcome in outcomes:
            outcome_str = "".join(map(str, outcome))
            counts[outcome_str] = counts.get(outcome_str, 0) + 1
        print(f"Counts: {counts}")
        # Expected: roughly 512 for "00" and 512 for "11"

    # 2. Simulate a simple 1-qubit circuit
    print("\n--- Single Qubit Circuit (1 qubit) ---")
    single_qubit_circuit = [
        ("H", 0),          # Hadamard on qubit 0
        ("Rz", 0, {"theta": np.pi/2}), # Rz(pi/2) on qubit 0
        ("H", 0),          # Hadamard on qubit 0
        ("MEASURE", 0, {"shots": 100}) # Measure qubit 0
    ]

    simulator_single = CircuitSimulatorVerifier(num_qubits=1)
    single_results = simulator_single.run_circuit(single_qubit_circuit)

    print("Final State Vector (before measurement collapse):")
    print(single_results["final_state_vector"])
    # Initial |0> -> H -> 1/sqrt(2)(|0> + |1>)
    # -> Rz(pi/2) -> 1/sqrt(2)(|0> + e^(i*pi/2)|1>) = 1/sqrt(2)(|0> + i|1>)
    # -> H -> 1/sqrt(2) * [1/sqrt(2)(|0> + |1>) + i/sqrt(2)(|0> - |1>)]
    # = 1/2 * [(1+i)|0> + (1-i)|1>]
    # Probabilities: |(1+i)/2|^2 = (1^2+1^2)/4 = 2/4 = 0.5
    #                |(1-i)/2|^2 = (1^2+(-1)^2)/4 = 2/4 = 0.5
    # So, 50% for |0> and 50% for |1>

    print("\nMeasurement Results (100 shots):")
    measured_qubits_key_single = "0"
    if measured_qubits_key_single in single_results["measurement_results"]:
        outcomes_single = single_results["measurement_results"][measured_qubits_key_single]
        counts_single = {}
        for outcome in outcomes_single:
            outcome_str = "".join(map(str, outcome))
            counts_single[outcome_str] = counts_single.get(outcome_str, 0) + 1
        print(f"Counts: {counts_single}")
        # Expected: roughly 50 for "0" and 50 for "1"

    # 3. Demonstrate state vector access and reset
    print("\n--- State Vector Access and Reset ---")
    simulator_access = CircuitSimulatorVerifier(num_qubits=1)
    print(f"Initial state: {simulator_access.get_state_vector()}")
    simulator_access.apply_gate("H", 0)
    print(f"State after H: {simulator_access.get_state_vector()}")
    simulator_access.reset_state()
    print(f"State after reset: {simulator_access.get_state_vector()}")
    
    # 4. Demonstrate 3-qubit CNOT (control 0, target 2)
    print("\n--- 3-Qubit CNOT (0, 2) ---")
    three_qubit_circuit = [
        ("H", 0),
        ("X", 1), # Put qubit 1 in |1> state
        ("CNOT", [0, 2]), # CNOT with control 0, target 2
        ("MEASURE", [0, 1, 2], {"shots": 1})
    ]
    simulator_three = CircuitSimulatorVerifier(num_qubits=3)
    three_results = simulator_three.run_circuit(three_qubit_circuit)
    print("Final State Vector (before measurement collapse):")
    print(three_results["final_state_vector"])
    # Initial: |000>
    # H 0: 1/sqrt(2) (|000> + |100>)
    # X 1: 1/sqrt(2) (|010> + |110>)
    # CNOT 0,2:
    #   |010> -> |010> (control 0 is 0, target 2 unchanged)
    #   |110> -> |111> (control 0 is 1, target 2 flipped)
    # Final state: 1/sqrt(2) (|010> + |111>)
    # Amplitudes for |010> (index 2) and |111> (index 7) should be 1/sqrt(2)
    
    print("\nMeasurement Results (1 shot):")
    measured_qubits_key_three = "0,1,2"
    if measured_qubits_key_three in three_results["measurement_results"]:
        print(f"Outcome: {three_results['measurement_results'][measured_qubits_key_three][0]}")
        # Expected: either [0,1,0] or [1,1,1]
    
    print("\n--- End of Demonstration ---")