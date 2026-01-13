# Verification Suite: Bra-Ket Notation Comment Parser and Amplitude Renderer

## 1. Objective and Scope

This document outlines a comprehensive suite of test cases designed to validate the functionality of the Bra-Ket notation parser and its associated amplitude-based rendering engine. The tests cover a wide range of quantum state representations, from fundamental basis states to complex multi-qubit entangled systems. The primary objective is to ensure syntactical correctness, semantic accuracy according to the postulates of quantum mechanics, and faithful visual representation of quantum amplitudes.

---

## 2. Foundational Basis State Axioms

### Test Case ID: FND-001
- **Description:** Verification of the parser's ability to correctly identify and process the computational basis state Ket |0⟩.
- **Input String:** `# |0⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "0" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visual representation indicating 100% probability for the |0⟩ state. This could be a fully filled bar, a solid color block, or a vector pointing directly to the north pole of the Bloch sphere.

### Test Case ID: FND-002
- **Description:** Validation of the parser's handling of the computational basis state Ket |1⟩.
- **Input String:** `# |1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visual representation indicating 100% probability for the |1⟩ state. This could be a fully filled bar for the |1⟩ component, or a vector pointing directly to the south pole of the Bloch sphere.

---

## 3. Superposition Principle Validation

### Test Case ID: SUP-001
- **Description:** Parsing of a standard Hadamard state, |+⟩, with real, equal amplitudes.
- **Input String:** `# (1/sqrt(2))|0⟩ + (1/sqrt(2))|1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visual representation showing equal probability amplitudes (50% probability each) for both |0⟩ and |1⟩ states. On a Bloch sphere, this corresponds to a vector pointing along the +X axis.

### Test Case ID: SUP-002
- **Description:** Parsing of the |-⟩ state, demonstrating handling of negative real amplitudes and relative phase.
- **Input String:** `# 1/sqrt(2) * |0⟩ - 1/sqrt(2) * |1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": -0.70710678, "imag": 0.0 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visual representation showing equal probability amplitudes but with a phase difference of π. On a Bloch sphere, this corresponds to a vector pointing along the -X axis.

---

## 4. Complex Amplitude and Phase Coherence

### Test Case ID: CPLX-001
- **Description:** Parsing of a state with a complex amplitude, specifically the |i⟩ state (also known as |R⟩).
- **Input String:** `# (1/sqrt(2))|0⟩ + i*(1/sqrt(2))|1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": 0.0, "imag": 0.70710678 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A representation indicating equal probability amplitudes for |0⟩ and |1⟩, but with a relative phase of π/2. On a Bloch sphere, this is a vector pointing along the +Y axis. The rendering should visually distinguish phase, perhaps with a color wheel or an angle indicator.

### Test Case ID: CPLX-002
- **Description:** Parsing of a state with a negative imaginary amplitude, |-i⟩ (also known as |L⟩).
- **Input String:** `# (1/sqrt(2))|0⟩ - i/sqrt(2) * |1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": 0.0, "imag": -0.70710678 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A representation indicating equal probability amplitudes for |0⟩ and |1⟩, but with a relative phase of -π/2. On a Bloch sphere, this is a vector pointing along the -Y axis.

---

## 5. Multi-Qubit System and Entanglement Parsing

### Test Case ID: ENT-001
- **Description:** Verification of the Bell state |Φ⁺⟩, a fundamental entangled state.
- **Input String:** `# (1/sqrt(2)) * (|00⟩ + |11⟩)`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 2,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "00" },
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "11" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visualization that clearly shows non-separability. This could be a density matrix plot or a "q-sphere" representation showing correlations. A simple bar chart would show 50% probability for |00⟩ and 50% for |11⟩, with zero for |01⟩ and |10⟩.

### Test Case ID: ENT-002
- **Description:** Parsing the Greenberger–Horne–Zeilinger (GHZ) state for a 3-qubit system.
- **Input String:** `# (1/sqrt(2))|000⟩ + (1/sqrt(2))|111⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "ket",
    "qubits": 3,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "000" },
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "111" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** A visualization for a 3-qubit system showing 50% probability for the |000⟩ state and 50% for the |111⟩ state, with all other 6 basis states having zero amplitude.

---

## 6. Dual Space (Bra) Notation and Inner Product Axioms

### Test Case ID: BRA-001
- **Description:** Parsing a simple Bra vector, ⟨1|.
- **Input String:** `# ⟨1|`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "bra",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** No direct amplitude rendering is typical for a Bra alone. The system should recognize it as an operator awaiting a Ket. A textual confirmation of a valid Bra is sufficient.

### Test Case ID: BRA-002
- **Description:** Parsing a Bra vector in superposition with complex conjugate amplitudes, ⟨i|.
- **Input String:** `# (1/sqrt(2))⟨0| - i*(1/sqrt(2))⟨1|`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "bra",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 0.70710678, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": 0.0, "imag": -0.70710678 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** Similar to BRA-001, a textual confirmation is expected. The parser must correctly compute the complex conjugate of the corresponding Ket's amplitudes.

### Test Case ID: INNER-001
- **Description:** Parsing and evaluation of an inner product representing orthogonality, ⟨0|1⟩.
- **Input String:** `# ⟨0|1⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "inner_product",
    "bra": { "type": "bra", "state": [{ "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "0" }] },
    "ket": { "type": "ket", "state": [{ "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "1" }] },
    "result": { "real": 0.0, "imag": 0.0 }
  }
  ```
- **Expected Amplitude-Based Rendering:** A scalar value of `0`. The rendering should clearly display this numerical result.

### Test Case ID: INNER-002
- **Description:** Parsing and evaluation of an inner product representing projection, ⟨+|ψ⟩ where |ψ⟩ = |0⟩.
- **Input String:** `# ⟨+|0⟩`
- **Expected Parsed Structure:**
  ```json
  {
    "type": "inner_product",
    "bra": { "type": "bra", "state": [...] },
    "ket": { "type": "ket", "state": [...] },
    "result": { "real": 0.70710678, "imag": 0.0 }
  }
  ```
- **Expected Amplitude-Based Rendering:** A scalar value of `1/√2`. The rendering should display this numerical result.

---

## 7. Syntactic Flexibility and Edge Case Robustness

### Test Case ID: FLEX-001
- **Description:** Verification of parser tolerance to variable whitespace and parentheses.
- **Input String:** `#   ( 1/sqrt(2) )  *  |0⟩   +   (1/sqrt(2))   |1⟩`
- **Expected Parsed Structure:** Identical to SUP-001.
- **Expected Amplitude-Based Rendering:** Identical to SUP-001.

### Test Case ID: FLEX-002
- **Description:** Verification of parser handling of different coefficient notations (implicit vs. explicit multiplication).
- **Input String:** `# (1/sqrt(2))|0⟩ + (i/sqrt(2))|1⟩`
- **Input String (Alternative):** `# (1/sqrt(2)) * |0⟩ + (i/sqrt(2)) * |1⟩`
- **Expected Parsed Structure:** Both inputs must yield the same structure as CPLX-001.
- **Expected Amplitude-Based Rendering:** Identical to CPLX-001.

### Test Case ID: EDGE-001
- **Description:** Handling of a state with a zero-amplitude component explicitly included.
- **Input String:** `# 1.0|0⟩ + 0.0|1⟩`
- **Expected Parsed Structure:** Functionally equivalent to FND-001, but the parser may retain the zero-amplitude term.
  ```json
  {
    "type": "ket",
    "qubits": 1,
    "state": [
      { "amplitude": { "real": 1.0, "imag": 0.0 }, "basis": "0" },
      { "amplitude": { "real": 0.0, "imag": 0.0 }, "basis": "1" }
    ]
  }
  ```
- **Expected Amplitude-Based Rendering:** Identical to FND-001. The zero-amplitude component should not be rendered or should be explicitly shown as having zero magnitude.

---

## 8. Error Handling and Malformed Input Rejection

### Test Case ID: ERR-001
- **Description:** Rejection of a non-normalized state vector.
- **Input String:** `# 0.8|0⟩ + 0.8|1⟩`
- **Expected Behavior:** The parser must reject the input and raise a `NormalizationError`. The sum of squared amplitudes (0.64 + 0.64 = 1.28) is not equal to 1.
- **Expected Amplitude-Based Rendering:** A clear error message: "State vector is not normalized. Sum of squared magnitudes is 1.28."

### Test Case ID: ERR-002
- **Description:** Rejection of mismatched bra-ket notation.
- **Input String:** `# ⟨0|1>`
- **Expected Behavior:** The parser must reject the input and raise a `SyntaxError`.
- **Expected Amplitude-Based Rendering:** An error message indicating a syntax violation: "Mismatched delimiter: Expected '⟩' but found end of string."

### Test Case ID: ERR-003
- **Description:** Rejection of an invalid basis state label.
- **Input String:** `# (1/sqrt(2))|a⟩ + (1/sqrt(2))|b⟩`
- **Expected Behavior:** The parser must reject the input and raise a `BasisError`, as 'a' and 'b' are not valid computational basis labels.
- **Expected Amplitude-Based Rendering:** An error message: "Invalid basis state label 'a'. Basis states must be represented by '0' or '1'."

### Test Case ID: ERR-004
- **Description:** Rejection of inconsistent qubit dimensions within a single state vector.
- **Input String:** `# (1/sqrt(2))|0⟩ + (1/sqrt(2))|11⟩`
- **Expected Behavior:** The parser must reject the input and raise a `DimensionMismatchError`.
- **Expected Amplitude-Based Rendering:** An error message: "Inconsistent number of qubits in superposition. Found basis states with 1 and 2 qubits."

### Test Case ID: ERR-005
- **Description:** Rejection of an invalid coefficient expression.
- **Input String:** `# (1/sqrt(2))|0⟩ + (1/0)|1⟩`
- **Expected Behavior:** The parser's mathematical evaluator must reject the input and raise a `MathError`.
- **Expected Amplitude-Based Rendering:** An error message: "Mathematical evaluation failed: Division by zero."