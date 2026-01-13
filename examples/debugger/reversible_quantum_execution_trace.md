# Reversible Quantum Execution Trace: Examples

This document provides examples of using a time-reversal debugger to step forward and backward through quantum code execution. We will explore various scenarios, highlighting the benefits of this debugging approach for understanding and correcting quantum algorithms.

## Example 1: Simple Hadamard Gate

This example demonstrates the basic functionality of stepping through a simple quantum circuit consisting of a single Hadamard gate applied to a qubit initialized in the |0⟩ state.

### Code

```python
from qiskit import QuantumCircuit, execute, Aer

# Create a quantum circuit with one qubit
qc = QuantumCircuit(1, 1)

# Apply a Hadamard gate
qc.h(0)

# Measure the qubit
qc.measure(0, 0)

# Simulate the circuit
simulator = Aer.get_backend('qasm_simulator')
job = execute(qc, simulator, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print(counts)
```

### Debugging with Time-Reversal

1.  **Initial State:** The qubit is initialized in the |0⟩ state. The debugger shows the state vector as [1, 0].

2.  **Hadamard Gate:** Stepping forward executes the Hadamard gate. The debugger shows the state vector transforming to approximately [0.707, 0.707], representing an equal superposition of |0⟩ and |1⟩.

3.  **Measurement:** Stepping forward executes the measurement. The debugger shows the probabilities of measuring |0⟩ and |1⟩, which should be approximately 50% each.

4.  **Time-Reversal:** Stepping backward from the measurement allows us to observe the state *before* the measurement collapsed the superposition. We can see the [0.707, 0.707] state vector again.

5.  **Reversing Hadamard:** Stepping backward again reverses the Hadamard gate, returning the qubit to its initial |0⟩ state, represented by the state vector [1, 0].

### Observations

*   The time-reversal debugger allows us to observe the quantum state at each step of the circuit, including intermediate states that are not directly accessible through measurement.
*   We can verify that the Hadamard gate correctly creates a superposition.
*   We can understand the effect of measurement on the quantum state.

## Example 2: CNOT Gate and Entanglement

This example demonstrates the creation of entanglement using a CNOT gate and how the time-reversal debugger can help visualize this process.

### Code

```python
from qiskit import QuantumCircuit, execute, Aer

# Create a quantum circuit with two qubits
qc = QuantumCircuit(2, 2)

# Apply a Hadamard gate to the first qubit
qc.h(0)

# Apply a CNOT gate with the first qubit as control and the second as target
qc.cx(0, 1)

# Measure both qubits
qc.measure([0, 1], [0, 1])

# Simulate the circuit
simulator = Aer.get_backend('qasm_simulator')
job = execute(qc, simulator, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print(counts)
```

### Debugging with Time-Reversal

1.  **Initial State:** Both qubits are initialized in the |0⟩ state. The state vector is [1, 0, 0, 0].

2.  **Hadamard Gate:** Stepping forward applies the Hadamard gate to the first qubit, creating a superposition. The state vector becomes approximately [0.707, 0, 0.707, 0].

3.  **CNOT Gate:** Stepping forward applies the CNOT gate. The debugger shows the state vector transforming to approximately [0.707, 0, 0, 0.707], representing the entangled state (|00⟩ + |11⟩)/√2.

4.  **Measurement:** Stepping forward executes the measurement. The debugger shows the probabilities of measuring |00⟩ and |11⟩, which should be approximately 50% each.

5.  **Time-Reversal:** Stepping backward from the measurement allows us to observe the entangled state *before* the measurement.

6.  **Reversing CNOT:** Stepping backward again reverses the CNOT gate, returning the first qubit to its superposition state and the second qubit to its initial |0⟩ state.

7.  **Reversing Hadamard:** Stepping backward again reverses the Hadamard gate, returning the first qubit to its initial |0⟩ state.

### Observations

*   The time-reversal debugger allows us to visualize the creation of entanglement by observing the state vector after the CNOT gate.
*   We can verify that the CNOT gate correctly entangles the two qubits.
*   We can understand how the CNOT gate affects the state vector based on the state of the control qubit.

## Example 3: Quantum Teleportation

This example demonstrates a more complex quantum algorithm: quantum teleportation. The time-reversal debugger is invaluable for understanding the steps involved and verifying the correctness of the implementation.

### Code

```python
from qiskit import QuantumCircuit, execute, Aer, QuantumRegister, ClassicalRegister

# Create quantum registers
qr = QuantumRegister(3, 'q')
crz = ClassicalRegister(1, 'crz')
crx = ClassicalRegister(1, 'crx')
cr = ClassicalRegister(2, 'cr')
teleportation_circuit = QuantumCircuit(qr, crz, crx, cr, name='teleportation')

# Prepare the state to be teleported (e.g., |+⟩ state)
teleportation_circuit.h(0)
teleportation_circuit.barrier()

# Create entanglement between qubits 1 and 2
teleportation_circuit.h(1)
teleportation_circuit.cx(1, 2)
teleportation_circuit.barrier()

# Bell measurement on qubits 0 and 1
teleportation_circuit.cx(0, 1)
teleportation_circuit.h(0)
teleportation_circuit.barrier()

# Classical measurements
teleportation_circuit.measure(0, crz)
teleportation_circuit.measure(1, crx)

# Corrective gates on qubit 2 based on measurement results
teleportation_circuit.z(2).c_if(crz, 1)
teleportation_circuit.x(2).c_if(crx, 1)

# Measure the teleported qubit
teleportation_circuit.measure(2, cr)

# Simulate the circuit
simulator = Aer.get_backend('qasm_simulator')
job = execute(teleportation_circuit, simulator, shots=1024)
result = job.result()
counts = result.get_counts(teleportation_circuit)

print(counts)
```

### Debugging with Time-Reversal

1.  **Initial State:** All qubits are initialized in the |0⟩ state.

2.  **State Preparation:** The first qubit is prepared in the |+⟩ state using a Hadamard gate.

3.  **Entanglement Creation:** A Bell pair is created between qubits 1 and 2 using a Hadamard and CNOT gate.

4.  **Bell Measurement:** A Bell measurement is performed on qubits 0 and 1. The debugger allows us to observe the correlations between the measurement outcomes and the state of qubit 2.

5.  **Classical Measurements:** The measurement results are stored in classical registers.

6.  **Corrective Gates:** Corrective gates (Z and X) are applied to qubit 2 based on the classical measurement results. The debugger allows us to verify that the correct gates are applied based on the measurement outcomes.

7.  **Final Measurement:** The final measurement of qubit 2 should yield the same state as the initial state of qubit 0.

8.  **Time-Reversal:** Stepping backward through the circuit allows us to trace the evolution of the quantum state and verify that each step is performed correctly. We can observe the entanglement being created, the Bell measurement being performed, and the corrective gates being applied.

### Observations

*   The time-reversal debugger is essential for understanding the complex steps involved in quantum teleportation.
*   We can verify that the entanglement is correctly created and that the Bell measurement is performed as expected.
*   We can ensure that the corrective gates are applied correctly based on the measurement outcomes.
*   By stepping backward, we can trace the flow of quantum information and verify that the teleportation process is successful.

## Conclusion

These examples demonstrate the power of a time-reversal debugger for understanding and debugging quantum algorithms. By allowing us to step forward and backward through the execution of a quantum circuit, we can gain insights into the evolution of the quantum state and verify the correctness of our code. This is particularly useful for complex algorithms like quantum teleportation, where the intermediate states are not directly accessible through measurement. The ability to observe and manipulate the quantum state at each step of the circuit is a valuable tool for quantum software development.