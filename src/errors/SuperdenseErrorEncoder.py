import random
import numpy as np
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram

class SuperdenseErrorEncoder:
    """
    Encodes error messages using superdense coding with entangled qubit pairs.
    This class simulates the creation of entangled pairs, encoding of classical
    bits onto qubits, and measurement to decode the message.  It also includes
    error injection for simulation purposes.
    """

    def __init__(self, error_rate=0.01):
        """
        Initializes the SuperdenseErrorEncoder.

        Args:
            error_rate (float): The probability of a bit flip error during transmission.
        """
        self.error_rate = error_rate
        self.simulator = Aer.get_backend('qasm_simulator')

    def create_entangled_pair(self):
        """
        Creates an entangled Bell pair (phi+ state).

        Returns:
            QuantumCircuit: A quantum circuit representing the entangled pair.
        """
        circuit = QuantumCircuit(2, 0)  # 2 qubits, 0 classical bits initially
        circuit.h(0)  # Apply Hadamard gate to qubit 0
        circuit.cx(0, 1)  # Apply CNOT gate with qubit 0 as control and qubit 1 as target
        return circuit

    def encode_message(self, circuit, message):
        """
        Encodes a 2-bit classical message onto the entangled pair.

        Args:
            circuit (QuantumCircuit): The quantum circuit containing the entangled pair.
            message (str): A 2-bit classical message (e.g., "00", "01", "10", "11").

        Returns:
            QuantumCircuit: The quantum circuit with the message encoded.
        """
        if len(message) != 2 or not all(bit in '01' for bit in message):
            raise ValueError("Message must be a 2-bit string.")

        if message[1] == '1':
            circuit.x(0)  # Apply X gate if the second bit is 1
        if message[0] == '1':
            circuit.z(0)  # Apply Z gate if the first bit is 1

        return circuit

    def inject_error(self, circuit):
        """
        Simulates a bit-flip error on the transmitted qubit.

        Args:
            circuit (QuantumCircuit): The quantum circuit representing the transmitted qubit.

        Returns:
            QuantumCircuit: The quantum circuit with a potential bit-flip error.
        """
        if random.random() < self.error_rate:
            circuit.x(0)  # Apply X gate (bit-flip) with probability error_rate
        return circuit

    def decode_message(self, circuit):
        """
        Decodes the message from the received qubit.

        Args:
            circuit (QuantumCircuit): The quantum circuit containing the received qubit.

        Returns:
            QuantumCircuit: The quantum circuit with decoding gates applied.
        """
        circuit.cx(0, 1)  # Apply CNOT gate with qubit 0 as control and qubit 1 as target
        circuit.h(0)  # Apply Hadamard gate to qubit 0
        circuit.measure_all() # Measure both qubits
        return circuit

    def run_simulation(self, message, shots=1024):
        """
        Runs the entire superdense coding simulation.

        Args:
            message (str): The 2-bit classical message to send.
            shots (int): The number of simulation shots.

        Returns:
            dict: The measurement results (counts) from the simulation.
        """
        entangled_pair = self.create_entangled_pair()
        encoded_circuit = self.encode_message(entangled_pair, message)
        error_injected_circuit = self.inject_error(encoded_circuit)

        # Create a new circuit to append the error injected circuit
        # to the entangled pair creation circuit.
        full_circuit = QuantumCircuit(2,2)
        full_circuit.h(0)
        full_circuit.cx(0,1)
        full_circuit.barrier()
        full_circuit.append(error_injected_circuit.remove_final_measurements(inplace=False), [0,1])
        full_circuit.barrier()
        decoded_circuit = self.decode_message(full_circuit)

        compiled_circuit = transpile(decoded_circuit, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(compiled_circuit)
        return counts

if __name__ == '__main__':
    encoder = SuperdenseErrorEncoder(error_rate=0.1)
    message = "10"
    results = encoder.run_simulation(message)
    print(f"Message sent: {message}")
    print(f"Measurement results: {results}")

    # Example of how to interpret the results:
    # The keys in the 'results' dictionary represent the measured bit strings.
    # For example, '00' means both qubits were measured as 0.
    # The values represent the number of times that outcome was observed.
    # Ideally, if the message was "10", you would expect to see "10" as the most frequent outcome.
    # However, due to the error rate, other outcomes may also be observed.