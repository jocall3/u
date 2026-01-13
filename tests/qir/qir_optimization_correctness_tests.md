# Quantum Intermediate Representation (QIR) Optimization Pass Correctness and Efficacy Verification Suite

## 1. Abstract and Mandate

This document specifies the test suite for validating the semantic correctness, performance efficacy, and quantum-physical integrity of optimization passes applied to the Quantum Intermediate Representation (QIR). The primary mandate is to ensure that any transformation of a QIR module by the optimization toolchain results in a program that is either physically equivalent or provides a quantifiable improvement in a target metric (e.g., fidelity, resource reduction) without violating the underlying quantum computational model. A significant focus is placed on the verification of entanglement distillation protocols, where the interplay between quantum operations and classical control is paramount.

## 2. Testbed Configuration and Metrological Standards

All verification procedures defined herein shall be executed within a strictly controlled environment to ensure reproducibility and consistency of results.

*   **QIR Toolchain:**
    *   LLVM/Clang: Version 14.0.0 or later, with QIR dialect support.
    *   `qir-opt` (QIR Optimizer): Target build from main branch, commit hash to be recorded with test results.
    *   QIR Generators: `pyqir` v0.8.0+, `qiskit-qir` v0.3.0+.
*   **Simulation Backends:**
    *   **State Vector Simulator:** A full-state simulator capable of calculating the final state vector $|\psi_f\rangle$ for noiseless correctness verification. Required precision: `complex<double>`.
    *   **Density Matrix Simulator:** A simulator capable of evolving a density matrix $\rho$ under noisy quantum channels (e.g., Depolarizing, Amplitude Damping). Required for fidelity calculations in realistic scenarios.
*   **Primary Metrics for Verification:**
    *   **State Fidelity:** $F(|\psi_1\rangle, |\psi_2\rangle) = |\langle\psi_1|\psi_2\rangle|^2$. For pure state comparisons.
    *   **Process Fidelity:** $F_{process}(E, U) = \int d\psi \langle\psi|U^\dagger E(|\psi\rangle\langle\psi|)U|\psi\rangle$. For comparing quantum channels.
    *   **Gate Complexity:**
        *   Total Gate Count.
        *   Two-Qubit Gate Count (specifically CNOT-count).
        *   T-depth / T-count (for fault-tolerant contexts).
    *   **Circuit Depth:** The longest path of causally connected gates in the circuit DAG.
    *   **Compilation Latency:** Wall-clock time for `qir-opt` to complete all specified passes.

---

## 3. Invariance and Semantic Equivalence Assays

This section details test cases designed to prove that optimizations preserve the logical quantum operation defined by the input QIR. The fundamental principle is that for any unitary operation $U_{unopt}$ represented by the initial QIR, the optimized QIR must represent a unitary $U_{opt}$ such that $U_{opt} = e^{i\phi} U_{unopt}$ for some global phase $\phi$.

### Assay ISEA-001: Pauli Frame Commutation and Cancellation

*   **Objective:** Verify that the optimizer correctly identifies and eliminates redundant sequences of Pauli and Clifford gates.
*   **Input QIR:** A module containing sequences like `H(q0); Z(q0); H(q0);` (equivalent to `X(q0)`) and `Y(q1); Y(q1);` (equivalent to Identity).
*   **Optimization Pass(es):** `qir-gate-cancellation`, `qir-clifford-simplification`.
*   **Expected Output QIR:** The QIR should be transformed to contain only the minimal equivalent operations, e.g., a single `X(q0)` and the complete removal of the `Y(q1); Y(q1);` sequence.
*   **Verification Method:**
    1.  Generate the unitary matrix for the original and optimized circuits.
    2.  Calculate the normalized Frobenius norm of the difference: $||U_{orig} - U_{opt}||_F$.
*   **Success Criteria:** The Frobenius norm of the difference must be less than a machine epsilon tolerance of $1 \times 10^{-12}$.

### Assay ISEA-002: Unused Qubit and Result Elision

*   **Objective:** Ensure that qubits and classical results that are allocated but never used or do not influence the final measured output are correctly identified and removed.
*   **Input QIR:** A program that allocates 5 qubits but only applies gates to qubits 0 and 2. It measures qubit 2 into `result2` but the program output only depends on a measurement of qubit 0 into `result0`.
*   **Optimization Pass(es):** `dead-code-elimination`, `global-dce`.
*   **Expected Output QIR:** The optimized QIR should contain no references to qubits 1, 3, 4, or `result2`. The number of allocated qubits should be reduced to 2.
*   **Verification Method:**
    1.  Execute both the original and optimized QIR modules 10,000 times.
    2.  Collect the measurement statistics for the meaningful output (`result0`).
    3.  Perform a Chi-squared test on the two resulting probability distributions.
*   **Success Criteria:** The p-value of the Chi-squared test must be greater than 0.05, indicating that the null hypothesis (that the distributions are identical) cannot be rejected.

---

## 4. Entanglement Distillation Protocol Integrity Verification

These tests are critical for validating optimizations on hybrid quantum-classical algorithms that form the basis of quantum networking and error correction. The optimizer must reduce resource costs without compromising the primary function of the protocol: increasing the fidelity of an entangled state.

### Verification Scenario EDP-BBPSSW-01: Single-Round BBPSSW Fidelity Analysis

*   **Objective:** To confirm that optimization of a BBPSSW distillation circuit does not negatively impact the post-selection fidelity of the resulting Bell pair when executed under a realistic noise model.
*   **Input QIR:** A QIR module implementing one round of the BBPSSW protocol. The initial state consists of two Bell pairs, each prepared with a fidelity of ~0.85 by applying a depolarizing channel after the ideal state preparation. The protocol involves CNOTs and local measurements, with classical communication dictating a final joint measurement.
*   **Optimization Pass(es):** Full pipeline (`-O3`), including `sccp`, `bdce`, `simplify-cfg`.
*   **Expected Output QIR:** A circuit with potentially fewer gates and a simplified classical control flow graph.
*   **Verification Method:**
    1.  Using a density matrix simulator, execute the unoptimized QIR. Simulate the initial noisy states $\rho_{in} = \rho_{01} \otimes \rho_{23}$.
    2.  Run the protocol. Upon successful classical measurement outcome (post-selection), calculate the fidelity of the output state $\rho_{out}$ with respect to the ideal Bell state $|\Phi^+\rangle$: $F(\rho_{out}, |\Phi^+\rangle)$.
    3.  Repeat steps 1-2 for the optimized QIR.
*   **Success Criteria:**
    *   `Fidelity_optimized >= Fidelity_unoptimized - 1e-9`. A negligible tolerance is allowed for floating-point discrepancies, but no systematic degradation is permissible.
    *   The post-selection probability must remain identical between the two versions.

### Verification Scenario EDP-DEJMPS-02: Recursive Distillation Resource Scaling

*   **Objective:** To analyze the resource reduction achieved by the optimizer on a multi-round, recursive DEJMPS distillation protocol.
*   **Input QIR:** A QIR module implementing a two-level recursive DEJMPS protocol. This involves nested conditional logic based on measurement outcomes from previous rounds.
*   **Optimization Pass(es):** `qir-adapter`, `instcombine`, `simplify-cfg`.
*   **Expected Output QIR:** The classical control flow should be flattened where possible. Redundant quantum operations across different classical branches should be hoisted or combined.
*   **Verification Method:**
    1.  Perform a static analysis of the unoptimized and optimized QIR modules.
    2.  Count the total number of:
        *   `call @__quantum__qis__cnot`
        *   `call @__quantum__qis__mz`
        *   `br i1 %cond, label %if.then, label %if.else` (basic blocks related to quantum results).
*   **Success Criteria:**
    *   The CNOT count in the optimized QIR must be at least 15% lower than the original.
    *   The number of conditional branches must be reduced or, in the worst case, remain the same.

---

## 5. Quantum-Classical Computation Stress Assays

This section targets the optimizer's ability to handle QIR's most powerful feature: the seamless integration of complex classical computation with quantum operations.

### Stress Test QCHC-ST-001: Variational Algorithm Parameter Propagation

*   **Objective:** Verify that classical constant propagation and function inlining work correctly for parametric quantum circuits, such as those in VQE or QAOA.
*   **Input QIR:** A VQE ansatz circuit where rotation angles are computed by a separate classical function (e.g., `calculate_angles(params)`) and passed as arguments to `Ry` and `Rz` gates. The test will invoke this with constant parameter inputs.
*   **Optimization Pass(es):** `function-inlining`, `sccp`, `instcombine`.
*   **Expected Output QIR:** The `calculate_angles` function should be inlined. All classical arithmetic should be pre-computed, and the `Ry`/`Rz` gates should have constant floating-point arguments directly embedded.
*   **Verification Method:**
    1.  Execute the optimized QIR on a state vector simulator and store the final state vector $|\psi_{opt}\rangle$.
    2.  Execute the unoptimized QIR and store its final state vector $|\psi_{unopt}\rangle$.
    3.  Calculate the fidelity $F(|\psi_{opt}\rangle, |\psi_{unopt}\rangle)$.
*   **Success Criteria:** Fidelity must be greater than $1 - 1 \times 10^{-12}$. The optimized QIR must contain no `call` instructions to the classical angle calculation function.

### Stress Test QCHC-ST-002: Dynamic Circuit Generation via Mid-Circuit Measurement

*   **Objective:** To validate optimizations on dynamic circuits where the structure of subsequent quantum operations depends on the outcome of a mid-circuit measurement.
*   **Input QIR:** A circuit that implements a measurement-based quantum computation primitive. For example, preparing a 3-qubit linear cluster state, measuring the first qubit in a specific basis, and then applying a correction to the third qubit conditional on the measurement outcome.
*   **Optimization Pass(es):** `simplify-cfg`, `tail-call-elimination`.
*   **Expected Output QIR:** The control flow graph must remain logically equivalent. The optimizer should not reorder quantum operations past the measurement if they are causally dependent on its result.
*   **Verification Method:**
    1.  Execute both versions of the QIR 100,000 times.
    2.  For each execution, record the mid-circuit measurement outcome and the final state of the system (via state tomography on the remaining qubits).
    3.  Verify that for a given measurement outcome (e.g., '0'), the final state produced by the optimized circuit is identical to the final state produced by the unoptimized circuit. Repeat for all possible outcomes.
*   **Success Criteria:** For each classical outcome branch, the fidelity between the final quantum states of the optimized and unoptimized circuits must be > 0.9999. The probability distribution of the mid-circuit measurement outcomes must be statistically identical.