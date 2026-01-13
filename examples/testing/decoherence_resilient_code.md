# Decoherence-Resilient Quantum Code Examples

This document provides examples of quantum code designed to be resilient to decoherence. Decoherence is the loss of quantum information to the environment, a major obstacle in building practical quantum computers. These examples demonstrate techniques to mitigate decoherence effects and maintain computational accuracy.

## 1. Quantum Error Correction (QEC) - Shor Code

The Shor code is a fundamental quantum error correction code that protects against both bit-flip and phase-flip errors.

```python
import qiskit
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel, pauli_error, depolarizing_error

# Create a quantum circuit for the Shor code
qc = QuantumCircuit(9, 1)

# Encoding:
qc.cx(0, 3)
qc.cx(0, 6)
qc.h(0)
qc.h(3)
qc.h(6)
qc.cx(0, 1)
qc.cx(3, 4)
qc.cx(6, 7)
qc.cx(0, 2)
qc.cx(3, 5)
qc.cx(6, 8)
qc.barrier()

# Simulate a bit-flip error on qubit 0
qc.x(0)
qc.barrier()

# Error correction:
qc.cx(0, 1)
qc.cx(3, 4)
qc.cx(6, 7)
qc.cx(0, 2)
qc.cx(3, 5)
qc.cx(6, 8)
qc.toffoli(2, 1, 0)
qc.toffoli(5, 4, 3)
qc.toffoli(8, 7, 6)
qc.h(0)
qc.h(3)
qc.h(6)
qc.cx(0, 3)
qc.cx(0, 6)
qc.ccx(6, 3, 0)
qc.barrier()

# Measurement
qc.measure(0, 0)

# Simulate with noise
simulator = AerSimulator(method='stabilizer')
compiled_circuit = transpile(qc, simulator)

# Define a noise model (example: depolarizing noise)
noise_model = NoiseModel()
error = depolarizing_error(0.1, 1)  # 10% depolarizing noise
noise_model.add_all_qubit_quantum_error(error, ['cx', 'id', 'rz', 'h'])

# Execute the circuit with noise
job = simulator.run(compiled_circuit, shots=1024, noise_model=noise_model)
result = job.result()
counts = result.get_counts(compiled_circuit)

print("Results with noise:", counts)

# Execute the circuit without noise for comparison
job_ideal = simulator.run(compiled_circuit, shots=1024)
result_ideal = job_ideal.result()
counts_ideal = result_ideal.get_counts(compiled_circuit)

print("Results without noise:", counts_ideal)
```

## 2. Dynamical Decoupling

Dynamical decoupling involves applying a sequence of pulses to qubits to average out the effects of environmental noise.

```python
import qiskit
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel, pauli_error, depolarizing_error

# Create a quantum circuit
qc = QuantumCircuit(1, 1)

# Apply a Hadamard gate
qc.h(0)

# Dynamical decoupling sequence (X-X sequence)
qc.x(0)
qc.x(0)

# Apply another Hadamard gate
qc.h(0)

# Measure the qubit
qc.measure(0, 0)

# Simulate with noise
simulator = AerSimulator(method='stabilizer')
compiled_circuit = transpile(qc, simulator)

# Define a noise model (example: depolarizing noise)
noise_model = NoiseModel()
error = depolarizing_error(0.01, 1)  # 1% depolarizing noise
noise_model.add_all_qubit_quantum_error(error, ['cx', 'id', 'rz', 'h', 'x'])

# Execute the circuit with noise
job = simulator.run(compiled_circuit, shots=1024, noise_model=noise_model)
result = job.result()
counts = result.get_counts(compiled_circuit)

print("Results with noise:", counts)

# Execute the circuit without noise for comparison
job_ideal = simulator.run(compiled_circuit, shots=1024)
result_ideal = job_ideal.result()
counts_ideal = result_ideal.get_counts(compiled_circuit)

print("Results without noise:", counts_ideal)
```

## 3. Error Mitigation Techniques - Readout Error Mitigation

Readout error mitigation corrects for errors that occur during the measurement process.

```python
import qiskit
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel, pauli_error, depolarizing_error
from qiskit.ignis.mitigation.measurement import (complete_meas_cal,
                                                  MeasurementFilter,
                                                  circuits_from_calibration_pattern)

# Create a simple quantum circuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

# Simulate with noise
simulator = AerSimulator(method='stabilizer')
compiled_circuit = transpile(qc, simulator)

# Define a noise model (example: readout error)
noise_model = NoiseModel()
error_readout = pauli_error([('X', 0.1), ('I', 0.9)])  # 10% chance of bit flip
noise_model.add_readout_error(error_readout, [0])

# Execute the circuit with noise
job = simulator.run(compiled_circuit, shots=1024, noise_model=noise_model)
result = job.result()
counts = result.get_counts(compiled_circuit)

print("Results with noise (before mitigation):", counts)

# Create measurement calibration circuits
qr = qiskit.QuantumRegister(1)
meas_calibs, state_labels = complete_meas_cal(qr=qr, circlabel='mcal')

# Execute the calibration circuits with noise
t_circs = transpile(meas_calibs, simulator, optimization_level=0)
job = simulator.run(t_circs, shots=1024, noise_model=noise_model)
cal_results = job.result()

# Create a measurement filter
meas_filter = MeasurementFilter(cal_results, state_labels)

# Apply the filter to the noisy results
mitigated_counts = meas_filter.apply(counts)

print("Results with noise (after mitigation):", mitigated_counts)

# Execute the circuit without noise for comparison
job_ideal = simulator.run(compiled_circuit, shots=1024)
result_ideal = job_ideal.result()
counts_ideal = result_ideal.get_counts(compiled_circuit)

print("Results without noise:", counts_ideal)
```

## 4. Topological Quantum Computation (Conceptual)

Topological quantum computation uses anyons, quasiparticles with exotic exchange statistics, to encode and process quantum information.  The inherent robustness of topological qubits to local perturbations makes them highly resistant to decoherence.  While a full code implementation is beyond the scope of this example, we illustrate the conceptual advantage.

```python
# Conceptual example - Topological Qubit
# In topological quantum computation, qubits are encoded in the entanglement
# of multiple physical qubits (anyons).  Local noise affects only individual
# physical qubits, but the encoded logical qubit remains protected.

# Imagine a logical qubit encoded in 7 physical qubits.
# A single bit-flip error on one physical qubit does not affect the logical state.

# This is a conceptual representation and not executable code.
# Actual topological quantum computation requires specialized hardware and
# control sequences.
```

## 5. Decoherence-Free Subspaces (DFS)

Decoherence-free subspaces are specific subspaces of a multi-qubit system that are immune to certain types of noise.

```python
import qiskit
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel, pauli_error, depolarizing_error

# Create a quantum circuit using two qubits
qc = QuantumCircuit(2, 1)

# Prepare an entangled state (Bell state) - within the DFS
qc.h(0)
qc.cx(0, 1)
qc.barrier()

# Simulate a collective dephasing noise (same noise on both qubits)
# In a DFS, this noise should not affect the encoded information.

# Measure the first qubit
qc.measure(0, 0)

# Simulate with noise
simulator = AerSimulator(method='stabilizer')
compiled_circuit = transpile(qc, simulator)

# Define a noise model (example: collective dephasing noise)
noise_model = NoiseModel()
error = pauli_error([('Z', 0.05), ('I', 0.95)])  # 5% chance of Z error
noise_model.add_quantum_error(error, ['id'], [0]) # Apply to qubit 0
noise_model.add_quantum_error(error, ['id'], [1]) # Apply to qubit 1 - collective noise

# Execute the circuit with noise
job = simulator.run(compiled_circuit, shots=1024, noise_model=noise_model)
result = job.result()
counts = result.get_counts(compiled_circuit)

print("Results with noise:", counts)

# Execute the circuit without noise for comparison
job_ideal = simulator.run(compiled_circuit, shots=1024)
result_ideal = job_ideal.result()
counts_ideal = result_ideal.get_counts(compiled_circuit)

print("Results without noise:", counts_ideal)
```

## 6. Concatenated Codes

Concatenated codes involve combining multiple error correction codes to achieve higher levels of protection against decoherence.

```python
# Conceptual example - Concatenated Code
# A concatenated code uses one error correction code to protect the logical qubits
# of another error correction code.  This provides a hierarchical level of protection.

# Example: Concatenate the Shor code with a repetition code.

# 1. Encode a logical qubit using the Shor code (as shown in Example 1).
# 2. Treat each of the 9 physical qubits of the Shor code as a logical qubit
#    and encode it using a repetition code (e.g., 3-qubit repetition code).

# This results in a highly redundant encoding that is very resilient to noise.

# This is a conceptual representation and not a complete code implementation.
```

## 7. Circuit Optimization for Noise Reduction

Optimizing quantum circuits can reduce the number of gates and the duration of the computation, thereby minimizing the impact of decoherence.

```python
import qiskit
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel, pauli_error, depolarizing_error
from qiskit.compiler import optimize_1q_gates

# Create a quantum circuit
qc = QuantumCircuit(1, 1)

# Add a sequence of single-qubit gates
qc.h(0)
qc.rz(0.5, 0)
qc.h(0)
qc.rz(0.2, 0)
qc.h(0)

# Measure the qubit
qc.measure(0, 0)

# Optimize the circuit
optimized_qc = optimize_1q_gates(qc)

# Simulate with noise
simulator = AerSimulator(method='stabilizer')
compiled_circuit = transpile(qc, simulator)
optimized_compiled_circuit = transpile(optimized_qc, simulator)

# Define a noise model (example: depolarizing noise)
noise_model = NoiseModel()
error = depolarizing_error(0.005, 1)  # 0.5% depolarizing noise
noise_model.add_all_qubit_quantum_error(error, ['cx', 'id', 'rz', 'h'])

# Execute the original circuit with noise
job = simulator.run(compiled_circuit, shots=1024, noise_model=noise_model)
result = job.result()
counts = result.get_counts(compiled_circuit)

print("Results with original circuit (with noise):", counts)

# Execute the optimized circuit with noise
job_optimized = simulator.run(optimized_compiled_circuit, shots=1024, noise_model=noise_model)
result_optimized = job_optimized.result()
counts_optimized = result_optimized.get_counts(optimized_compiled_circuit)

print("Results with optimized circuit (with noise):", counts_optimized)

# Execute the circuits without noise for comparison
job_ideal = simulator.run(compiled_circuit, shots=1024)
result_ideal = job_ideal.result()
counts_ideal = result_ideal.get_counts(compiled_circuit)

print("Results with original circuit (without noise):", counts_ideal)

job_optimized_ideal = simulator.run(optimized_compiled_circuit, shots=1024)
result_optimized_ideal = job_optimized_ideal.result()
counts_optimized_ideal = result_optimized_ideal.get_counts(optimized_compiled_circuit)

print("Results with optimized circuit (without noise):", counts_optimized_ideal)