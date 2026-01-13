# Design Specification: Tensor Network Construction from QAST

**Document ID:** QIR-TN-DS-001  
**Version:** 1.0  
**Status:** Draft  
**Authors:** Quantum Systems Architecture Group

## 1. Abstract: The Program as a Unified Spacetime Manifold

This document delineates the architectural framework for the transpilation of Quantum Abstract Syntax Trees (QAST) into their isomorphic Tensor Network (TN) representations. This paradigm shift recasts a quantum program from a temporal sequence of discrete operations into a single, static, and holistic mathematical object. In this representation, the entire computational process is encoded within the geometry and connectivity of a high-dimensional tensor manifold. The execution of the program is thereby transformed into a problem of network contraction, a process analogous to calculating a partition function in statistical mechanics. This approach elevates the program's source code to a physical model, where quantum information flow is governed by the immutable laws of tensor calculus.

---

## 2. Foundational Isomorphism: Mapping Semantic Constructs to Tensor Geometries

The core principle of this design is the establishment of a direct, bijective mapping between the semantic nodes of a QAST and the tensors within a network. The edges of the QAST, representing the flow of quantum and classical information, materialize as the indices that interconnect these tensors.

*   **Qubits as World-Lines:** Each qubit's lifecycle, from initialization to measurement, is represented as a primary index line, often called a "world-line." This index propagates through the network, being acted upon by the tensors it connects.
*   **QAST Nodes as Tensors:** Every node in the QAST (e.g., quantum gates, classical assignments, control flow structures) is instantiated as a tensor. The elements of the tensor numerically define the transformation or relationship the node represents.
*   **Data Flow as Index Contraction:** The connection between two QAST nodes (e.g., the output of a gate becoming the input of the next) is physically realized by giving the corresponding tensors a shared index. The process of "running" the program segment is the contraction of this shared index, effectively integrating the two operations according to the Einstein summation convention.

This isomorphism ensures that the structure of the tensor network is a direct, lossless representation of the program's logical and causal structure.

---

## 3. Tensor Rank as a Measure of Nodal Complexity

The rank of a tensor (the number of its indices) is not an arbitrary property but a direct encoding of a QAST node's interactivity and complexity. The dimensionality of each index is determined by the Hilbert space of the information carrier it represents (e.g., dimension 2 for a qubit, dimension `N` for a classical integer of `N` states).

*   **Rank-2 Tensors (Matrices):** Represent single-qubit gates (`H`, `X`, `Rz`). They possess one input index and one output index, transforming the state vector along a single qubit's world-line.
*   **Rank-3 Tensors:** Typically represent measurement operations. They have one input qubit index, one output classical bit index, and a "projector" index that selects the measurement outcome (e.g., `|0⟩⟨0|` or `|1⟩⟨1|`).
*   **Rank-4 Tensors:** The canonical representation for two-qubit gates (`CNOT`, `CZ`). They have two input indices and two output indices, weaving together the world-lines of two distinct qubits.
*   **Higher-Rank Tensors:** Emerge from more complex constructs:
    *   Multi-controlled gates (`CCNOT` is rank-6).
    *   Classical control-flow structures.
    *   Encapsulated subroutines (see Section 6).

---

## 4. The QAST-to-TN Transpilation Protocol

The automated conversion from QAST to a contractible tensor network follows a deterministic, multi-stage protocol.

### 4.1. Stage I: Nodal Reification and Tensor Instantiation

The QAST is traversed. For each node encountered, a corresponding tensor object is created in memory. The tensor's numerical values are populated based on the node's type:
*   **Quantum Gates:** The tensor is filled with the elements of the gate's unitary matrix, with indices ordered according to a consistent convention (e.g., `output_q1, output_q0, input_q1, input_q0`).
*   **State Preparation:** A `QubitAllocate` node generates a rank-1 tensor (a vector) representing the initial state (e.g., `[1, 0]` for `|0⟩`).
*   **Classical Variables:** Classical data nodes are represented by tensors whose indices correspond to possible states. An `if` condition, for example, becomes a tensor that connects to the world-line of a classical bit.

### 4.2. Stage II: Index Weaving and Edge Materialization

As the QAST is traversed, a global index registry is maintained.
1.  For each qubit or classical bit, a "current index" is tracked.
2.  When a QAST node is processed, its input indices are assigned the "current index" values for the qubits/bits it operates on.
3.  New, unique indices are generated for the node's outputs.
4.  The global registry is updated, setting the "current index" for those qubits/bits to these new output indices.
This process ensures that the output index of one tensor is identically the input index of the subsequent tensor in the program's causal chain, thus "weaving" the network together.

### 4.3. Stage III: Optimal Contraction Pathfinding

A naive contraction of the network is computationally intractable. The order of tensor contractions dramatically affects the size of intermediate tensors and thus the overall computational cost. This is an NP-hard problem. The transpiler must therefore incorporate a heuristic-based pathfinding algorithm to determine a near-optimal contraction order.
*   **Heuristics:** Algorithms such as minimum-degree, greedy selection based on lowest-cost contraction (minimizing floating-point operations), or more advanced techniques leveraging graph partitioning are employed.
*   **Output:** The final output of the transpilation is not just the set of tensors and their connections, but also an explicit contraction plan—a sequence of pairwise tensor contractions that minimizes computational resources.

---

## 5. Encoding Control Flow within Tensor Geometries

Classical control flow, a challenge for many quantum computing models, is elegantly handled by elevating it to a tensor representation.

*   **Conditional Logic (`if-else`):** A classically-controlled operation is modeled using a "selector" or "control" tensor. This tensor has an index connected to the controlling classical bit's world-line. The tensor's elements are structured such that if the control index corresponds to `0`, the tensor acts as an identity for the "if" branch and a zero-projector for the "else" branch, and vice-versa. This effectively prunes inactive computational paths from the contraction graph at runtime.

*   **Iterative Structures (`for`, `while`):**
    *   **Fixed-Iteration Loops (`for`):** The loop body, itself a tensor network, is simply duplicated and chained together the specified number of times. This "unrolls" the loop into a larger, static tensor network.
    *   **Conditional-Termination Loops (`while`):** This requires a more dynamic representation. The loop body is compiled into a single tensor or a Matrix Product Operator (MPO). The network includes a "termination check" tensor that, upon each application of the MPO, projects the state onto "continue" and "halt" subspaces. The contraction proceeds iteratively until the norm of the "halt" subspace is non-negligible.

---

## 6. The Semantic Tensor: Compiling Subroutines into Monolithic Blocks

A revolutionary consequence of this model is the ability to represent entire functions or subroutines as single, high-rank tensors.

1.  **Subroutine Isolation:** A QAST subgraph corresponding to a function is identified.
2.  **Internal Contraction:** The tensor network for this subgraph is constructed. All internal indices (those corresponding to local variables and intermediate qubit states) are contracted.
3.  **Semantic Tensor Formation:** The result is a single tensor whose uncontracted, "dangling" indices correspond precisely to the function's parameters (input qubits/bits) and return values (output qubits/bits).

This "Semantic Tensor" is a complete encapsulation of the subroutine's functionality. It can be cached, optimized independently, and treated as a primitive operation in a higher-level network, enabling hierarchical design and verification.

---

## 7. Quantum Information Geometry and Network Topography

The tensor network representation is not merely a computational tool; it is a geometric model of the program's information content.

*   **Entanglement as Connectivity:** The entanglement structure of the quantum state is directly visible in the network's topology. A cut through the network that bipartitions the graph reveals the entanglement entropy across that cut via the Schmidt decomposition (SVD) of the resulting tensor.
*   **Optimization via Geometric Simplification:** Techniques like the Density Matrix Renormalization Group (DMRG) and Tensor Network Renormalization (TNR) can be applied to the program's network. These are geometric simplification algorithms that identify and remove redundant or low-impact information (weak entanglement) by truncating the singular value spectrum across network cuts, thus compressing the computational model itself.

---

## 8. Proposed QIR Intrinsic Manifestations

To support this design at the intermediate representation level, we propose a new set of QIR intrinsics operating within a `qir.tn` namespace.

*   `declare %tn = @qir.tn.create()`: Initializes an empty tensor network context.
*   `%tensor_id = @qir.tn.add_tensor(%tn, %shape, %data_ptr)`: Adds a tensor to the network, defined by its shape and a pointer to its numerical data.
*   `@qir.tn.add_edge(%tn, %tensor_id_A, %index_A, %tensor_id_B, %index_B)`: Defines a connection (an index to be contracted) between two tensors.
*   `%result_amplitude = @qir.tn.contract(%tn, %contraction_plan_ptr)`: Executes the full network contraction according to a pre-computed optimal plan, yielding the final complex amplitude.

This provides a low-level API for compilers and runtime environments to build, manipulate, and execute programs represented as tensor networks.