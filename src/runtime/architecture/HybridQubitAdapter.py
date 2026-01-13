# src/runtime/architecture/HybridQubitAdapter.py

import abc
import random
import typing as t

class AbstractQubitAdapter(abc.ABC):
    """
    Abstract base class for adapting code execution to different qubit types.
    This class defines the interface for interacting with various qubit substrates.
    """

    @abc.abstractmethod
    def initialize_qubit(self, qubit_id: int) -> None:
        """
        Initializes a qubit with the given ID.

        Args:
            qubit_id: The ID of the qubit to initialize.
        """
        pass

    @abc.abstractmethod
    def apply_gate(self, gate_name: str, qubit_ids: t.List[int], params: t.Optional[t.Dict[str, float]] = None) -> None:
        """
        Applies a quantum gate to the specified qubit(s).

        Args:
            gate_name: The name of the gate to apply (e.g., "H", "CNOT", "RX").
            qubit_ids: A list of qubit IDs to which the gate should be applied.
            params: Optional parameters for the gate (e.g., rotation angle).
        """
        pass

    @abc.abstractmethod
    def measure_qubit(self, qubit_id: int) -> int:
        """
        Measures the state of a qubit.

        Args:
            qubit_id: The ID of the qubit to measure.

        Returns:
            The measurement result (0 or 1).
        """
        pass

    @abc.abstractmethod
    def get_qubit_type(self) -> str:
        """
        Returns the type of qubit this adapter is designed for.

        Returns:
            A string representing the qubit type (e.g., "superconducting", "trapped_ion").
        """
        pass

    @abc.abstractmethod
    def get_connectivity(self) -> t.Dict[int, t.List[int]]:
        """
        Returns the connectivity graph of the qubits.

        Returns:
            A dictionary where keys are qubit IDs and values are lists of connected qubit IDs.
        """
        pass

    @abc.abstractmethod
    def reset_qubit(self, qubit_id: int) -> None:
        """
        Resets a qubit to the |0> state.

        Args:
            qubit_id: The ID of the qubit to reset.
        """
        pass


class SimulatedQubitAdapter(AbstractQubitAdapter):
    """
    A simulated qubit adapter for testing and development.
    """

    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.qubit_states = [0] * num_qubits  # Initialize all qubits to |0>
        self.connectivity = self._generate_random_connectivity(num_qubits)

    def _generate_random_connectivity(self, num_qubits: int) -> t.Dict[int, t.List[int]]:
        """
        Generates a random connectivity graph for the qubits.
        """
        connectivity = {}
        for i in range(num_qubits):
            neighbors = []
            num_neighbors = random.randint(0, min(3, num_qubits - 1))  # Limit to 3 neighbors for simplicity
            possible_neighbors = list(range(num_qubits))
            possible_neighbors.remove(i)  # Don't connect to itself

            neighbors = random.sample(possible_neighbors, num_neighbors)
            connectivity[i] = neighbors
        return connectivity

    def initialize_qubit(self, qubit_id: int) -> None:
        if 0 <= qubit_id < self.num_qubits:
            self.qubit_states[qubit_id] = 0  # Reset to |0>
        else:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

    def apply_gate(self, gate_name: str, qubit_ids: t.List[int], params: t.Optional[t.Dict[str, float]] = None) -> None:
        if gate_name == "H":
            if len(qubit_ids) != 1:
                raise ValueError("Hadamard gate requires one qubit.")
            qubit_id = qubit_ids[0]
            if 0 <= qubit_id < self.num_qubits:
                # Simulate Hadamard gate (50/50 chance of flipping)
                if random.random() < 0.5:
                    self.qubit_states[qubit_id] = 1 - self.qubit_states[qubit_id]
            else:
                raise ValueError(f"Invalid qubit ID: {qubit_id}")
        elif gate_name == "CNOT":
            if len(qubit_ids) != 2:
                raise ValueError("CNOT gate requires two qubits.")
            control_qubit = qubit_ids[0]
            target_qubit = qubit_ids[1]
            if 0 <= control_qubit < self.num_qubits and 0 <= target_qubit < self.num_qubits:
                if self.qubit_states[control_qubit] == 1:
                    self.qubit_states[target_qubit] = 1 - self.qubit_states[target_qubit]
            else:
                raise ValueError("Invalid qubit ID(s).")
        elif gate_name == "RX":
            if len(qubit_ids) != 1 or params is None or "angle" not in params:
                raise ValueError("RX gate requires one qubit and an angle parameter.")
            qubit_id = qubit_ids[0]
            angle = params["angle"]
            # In a real implementation, this would involve a rotation of the qubit state.
            # For simulation, we can approximate it with a probability based on the angle.
            probability = abs(angle) / (2 * 3.14159)  # Crude approximation
            if random.random() < probability:
                self.qubit_states[qubit_id] = 1 - self.qubit_states[qubit_id]
        else:
            raise ValueError(f"Unsupported gate: {gate_name}")

    def measure_qubit(self, qubit_id: int) -> int:
        if 0 <= qubit_id < self.num_qubits:
            # Simulate measurement (no collapse in this simple simulation)
            return self.qubit_states[qubit_id]
        else:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")

    def get_qubit_type(self) -> str:
        return "simulated"

    def get_connectivity(self) -> t.Dict[int, t.List[int]]:
        return self.connectivity

    def reset_qubit(self, qubit_id: int) -> None:
        if 0 <= qubit_id < self.num_qubits:
            self.qubit_states[qubit_id] = 0
        else:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")


class HybridQubitManager:
    """
    Manages a collection of different qubit adapters.
    This allows for running quantum algorithms on a hybrid quantum system.
    """

    def __init__(self, adapters: t.List[AbstractQubitAdapter]):
        self.adapters = adapters
        self.qubit_mapping: t.Dict[int, t.Tuple[AbstractQubitAdapter, int]] = {} # Maps global qubit ID to (adapter, local qubit ID)
        self.next_global_qubit_id = 0

    def allocate_qubit(self, adapter_index: int) -> int:
        """
        Allocates a qubit from a specific adapter.

        Args:
            adapter_index: The index of the adapter to allocate from.

        Returns:
            A unique global qubit ID.
        """
        if 0 <= adapter_index < len(self.adapters):
            adapter = self.adapters[adapter_index]
            # Assuming each adapter manages its own local qubit IDs starting from 0.
            # We need a way to track which local IDs are available.  For simplicity,
            # we'll just assume we can always allocate a new one.  A real implementation
            # would need a more sophisticated resource management strategy.
            local_qubit_id = self.get_next_available_local_id(adapter) # Placeholder
            self.qubit_mapping[self.next_global_qubit_id] = (adapter, local_qubit_id)
            global_id = self.next_global_qubit_id
            self.next_global_qubit_id += 1
            adapter.initialize_qubit(local_qubit_id) # Initialize the qubit on the adapter
            return global_id
        else:
            raise ValueError(f"Invalid adapter index: {adapter_index}")

    def get_next_available_local_id(self, adapter: AbstractQubitAdapter) -> int:
        """
        Placeholder for a more sophisticated local qubit ID management system.
        In a real implementation, this would track available local IDs within the adapter.
        For now, it just returns a simple incrementing ID.
        """
        # This is a very naive implementation and will likely lead to issues
        # if qubits are deallocated and reallocated.
        used_ids = [local_id for _, (a, local_id) in self.qubit_mapping.items() if a == adapter]
        if not used_ids:
            return 0
        else:
            return max(used_ids) + 1

    def apply_gate(self, gate_name: str, qubit_ids: t.List[int], params: t.Optional[t.Dict[str, float]] = None) -> None:
        """
        Applies a gate to the specified qubits, routing the operation to the correct adapter(s).

        Args:
            gate_name: The name of the gate to apply.
            qubit_ids: A list of global qubit IDs.
            params: Optional parameters for the gate.
        """
        # Group qubits by adapter
        adapter_groups: t.Dict[AbstractQubitAdapter, t.List[int]] = {}
        for global_qubit_id in qubit_ids:
            if global_qubit_id not in self.qubit_mapping:
                raise ValueError(f"Invalid qubit ID: {global_qubit_id}")
            adapter, local_qubit_id = self.qubit_mapping[global_qubit_id]
            if adapter not in adapter_groups:
                adapter_groups[adapter] = []
            adapter_groups[adapter].append(local_qubit_id)

        # Apply the gate to each group of qubits on the same adapter
        for adapter, local_qubit_ids in adapter_groups.items():
            adapter.apply_gate(gate_name, local_qubit_ids, params)

    def measure_qubit(self, qubit_id: int) -> int:
        """
        Measures a qubit and returns the result.

        Args:
            qubit_id: The global qubit ID.

        Returns:
            The measurement result (0 or 1).
        """
        if qubit_id not in self.qubit_mapping:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")
        adapter, local_qubit_id = self.qubit_mapping[qubit_id]
        return adapter.measure_qubit(local_qubit_id)

    def get_qubit_type(self, qubit_id: int) -> str:
        """
        Returns the type of qubit for a given global qubit ID.
        """
        if qubit_id not in self.qubit_mapping:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")
        adapter, _ = self.qubit_mapping[qubit_id]
        return adapter.get_qubit_type()

    def get_connectivity(self) -> t.Dict[int, t.List[int]]:
        """
        Returns the connectivity graph of the entire hybrid system.
        This is a simplified version that only considers connectivity within each adapter.
        A more sophisticated implementation would need to handle inter-adapter connectivity.
        """
        connectivity: t.Dict[int, t.List[int]] = {}
        for global_qubit_id, (adapter, local_qubit_id) in self.qubit_mapping.items():
            local_connectivity = adapter.get_connectivity()
            # Map local qubit IDs to global qubit IDs in the connectivity graph
            global_neighbors: t.List[int] = []
            if local_qubit_id in local_connectivity:
                for local_neighbor in local_connectivity[local_qubit_id]:
                    # Find the global qubit ID corresponding to the local neighbor
                    global_neighbor = next((g_id for g_id, (a, l_id) in self.qubit_mapping.items() if a == adapter and l_id == local_neighbor), None)
                    if global_neighbor is not None:
                        global_neighbors.append(global_neighbor)
            connectivity[global_qubit_id] = global_neighbors
        return connectivity

    def reset_qubit(self, qubit_id: int) -> None:
        """
        Resets a qubit to the |0> state.
        """
        if qubit_id not in self.qubit_mapping:
            raise ValueError(f"Invalid qubit ID: {qubit_id}")
        adapter, local_qubit_id = self.qubit_mapping[qubit_id]
        adapter.reset_qubit(local_qubit_id)

if __name__ == '__main__':
    # Example usage
    adapter1 = SimulatedQubitAdapter(num_qubits=5)
    adapter2 = SimulatedQubitAdapter(num_qubits=3)
    hybrid_manager = HybridQubitManager([adapter1, adapter2])

    # Allocate qubits from different adapters
    qubit1 = hybrid_manager.allocate_qubit(0)  # From adapter1
    qubit2 = hybrid_manager.allocate_qubit(1)  # From adapter2
    qubit3 = hybrid_manager.allocate_qubit(0)  # From adapter1

    print(f"Allocated qubit IDs: {qubit1}, {qubit2}, {qubit3}")

    # Apply a Hadamard gate to qubit1
    hybrid_manager.apply_gate("H", [qubit1])

    # Apply a CNOT gate between qubit1 and qubit2
    hybrid_manager.apply_gate("CNOT", [qubit1, qubit2])

    # Measure qubit2
    measurement_result = hybrid_manager.measure_qubit(qubit2)
    print(f"Measurement result for qubit {qubit2}: {measurement_result}")

    # Get the qubit type for qubit3
    qubit_type = hybrid_manager.get_qubit_type(qubit3)
    print(f"Qubit type for qubit {qubit3}: {qubit_type}")

    # Get the connectivity graph
    connectivity = hybrid_manager.get_connectivity()
    print(f"Connectivity graph: {connectivity}")

    # Reset qubit1
    hybrid_manager.reset_qubit(qubit1)
    print(f"Qubit {qubit1} reset.")