# Design Document: Non-Local Correlation Manager (NLCM)

## 1. Axiomatic Foundations of Correlated State Vector Management

### 1.1. Abstract

This document delineates the architectural design for the Non-Local Correlation Manager (NLCM), a critical control-plane service for distributed quantum computing fabrics. The primary mandate of the NLCM is to deterministically manage the state, lifecycle, and causal dependencies arising from quantum teleportation protocols. As distributed quantum algorithms increasingly rely on the transference of quantum states between physically separated Quantum Processing Units (QPUs), the classical information dependency created by Bell State Measurements (BSMs) and the consumption of entangled resources become a first-order concern. The NLCM serves as the authoritative source of truth for these non-local correlations, ensuring the logical integrity and causal consistency of the global computational state vector across the distributed system.

### 1.2. The Inevitability of Non-Local State Management

In a monolithic quantum computer, the state vector evolves under a series of unitary transformations, and all operations are causally ordered by the local execution timeline. In a distributed architecture, this paradigm is shattered. The act of teleporting a qubit `|ψ⟩` from Node A to Node B fundamentally entangles the future state of Node B with the past measurement outcome at Node A. This creates a light-cone dependency that must be respected.

The NLCM addresses the following core challenges:

*   **Entanglement as a Consumable Resource:** Entangled pairs (e.g., Bell pairs) are the substrate for teleportation. They are a finite, fragile, and costly resource. The NLCM must manage their allocation, track their fidelity, and orchestrate their consumption.
*   **Causality Enforcement:** The Pauli corrections (X and/or Z gates) required at the destination node are contingent upon the classical bits resulting from the BSM at the source. Executing subsequent gates on the teleported qubit before these corrections are applied will corrupt the computation. The NLCM enforces this causal ordering.
*   **State Synchronization:** The logical "location" of a qubit is no longer a static property. The NLCM maintains a dynamic topology of the logical qubit graph, tracking which physical QPU currently hosts which logical qubit.
*   **Fault Tolerance:** Classical communication channels can be lossy or latent. Entangled pairs can decohere. The NLCM must implement protocols to handle these failures gracefully, ensuring the global state does not become irrecoverably inconsistent.

## 2. The Ontological Framework for Entanglement as a Distributed Resource

### 2.1. Architectural Postulates

The NLCM is designed as a logically centralized, but potentially physically distributed, stateful service. It operates on the control plane, orchestrating data-plane operations on the QPUs and classical networks.

1.  **Separation of Concerns:** The NLCM does *not* execute quantum gates. It directs the QPUs (via local controllers) to execute them. It does not manage the physical layer of entanglement distribution; it interfaces with a service that does (the Entanglement Distribution Network, or EDN).
2.  **State as a First-Class Citizen:** The core function of the NLCM is the management of state. This includes the state of all entangled pairs, all in-flight teleportation operations, and the current mapping of logical qubits to physical locations.
3.  **Idempotency and Atomicity:** Interactions with the NLCM must be designed to be idempotent where possible. Teleportation operations should be treated as atomic transactions that can either succeed completely or be rolled back to a consistent state.
4.  **Temporal Logic as a Guiding Principle:** The protocols must be verifiable against temporal logic models to formally prove that causality is never violated. A state `S_B` at Node B at time `t_B` that depends on a measurement `M_A` at Node A at time `t_A` must strictly adhere to `t_B > t_A + Δt_classical`, where `Δt_classical` is the classical communication latency.

## 3. Deconstruction of the Correlation Manifold: Systemic Components and N-Dimensional Interfaces

The NLCM is not a monolith. It is a composite system interacting with other distributed services through well-defined, versioned APIs.

### 3.1. Core Components

*   **NLCM Registry:** A high-consistency database (e.g., using Raft or Paxos for consensus) that stores the state of all managed entities. This is the heart of the NLCM.
*   **Protocol Engine:** A state machine that processes teleportation requests and drives them through their lifecycle (from `INITIATED` to `COMPLETED` or `FAILED`).
*   **Causality Graph Manager:** An internal service that maintains a directed acyclic graph (DAG) of all computational dependencies. A teleportation operation adds a directed edge from the source node's BSM event to the destination node's correction event.
*   **Fidelity Estimator:** A component that models and tracks the expected fidelity of entangled resources and the teleported state, factoring in storage times, channel noise, and gate errors.

### 3.2. External Interfaces (APIs)

*   **`QuantumApplicationInterface` (for user-level programs):**
    *   `Teleport(sourceQubitID, destinationNodeID) -> Promise<TeleportationTicket>`: Asynchronously initiates a teleportation operation. Returns a ticket that can be used to query the status.

*   **`QPUControllerInterface` (for local QPU schedulers):**
    *   `RequestEntanglement(nodeA, nodeB, requiredFidelity) -> EntangledPairID`: Requests an entangled pair for a specific link.
    *   `ReportBSM(teleportationTicket, bsmOutcome[bit, bit]) -> Ack`: Reports the classical outcome of the Bell measurement.
    *   `AwaitCorrection(logicalQubitID) -> PauliCorrection[op, op]`: A blocking call for a destination QPU to wait for the necessary correction operations for a newly arrived qubit.

*   **`EntanglementDistributionNetworkInterface` (for the quantum network):**
    *   `AllocatePair(nodeA, nodeB) -> EntangledPair`: Provides a specific, usable entangled pair.
    *   `ReleasePair(pairID, reason)`: Releases a pair back to the pool (e.g., consumed, decohered).

## 4. Spacetime State Tensors: Modeling Correlated Qubit Lifecycles

The NLCM's internal state is modeled through a set of relational schemas designed for high-consistency and auditability.

### 4.1. Primary Data Schema: `TeleportationOperation`

| Field | Type | Description |
| :--- | :--- | :--- |
| `operation_id` | UUID | Primary key for the transaction. |
| `logical_qubit_id` | UUID | The globally unique identifier for the qubit being moved. |
| `source_node_id` | UUID | The identifier of the originating QPU. |
| `destination_node_id` | UUID | The identifier of the target QPU. |
| `entangled_pair_id` | UUID | Foreign key to the `EntangledPair` resource used. |
| `status` | Enum | `REQUESTED`, `RESOURCE_ALLOCATED`, `BSM_REPORTED`, `CORRECTION_DISPATCHED`, `COMPLETED`, `TIMED_OUT`, `FAILED`. |
| `creation_timestamp` | VectorClock | Timestamp of the request initiation. |
| `bsm_outcome` | BINARY(2) | The two classical bits from the BSM. Null until reported. |
| `correction_ops` | VARCHAR | The calculated Pauli corrections (e.g., "XZ"). Null until calculated. |
| `completion_timestamp` | VectorClock | Timestamp of final confirmation. |

### 4.2. Resource Schema: `EntangledPair`

| Field | Type | Description |
| :--- | :--- | :--- |
| `pair_id` | UUID | Primary key for the entangled resource. |
| `node_A_id` | UUID | The first node sharing the pair. |
| `node_B_id` | UUID | The second node sharing the pair. |
| `state` | Enum | `AVAILABLE`, `RESERVED`, `CONSUMED`, `DECOHERED`. |
| `creation_fidelity` | FLOAT | Estimated fidelity at the time of generation. |
| `generation_timestamp` | VectorClock | Timestamp of when the pair was certified as available. |

### 4.3. The Causality Graph

This is not a simple table but a graph data structure. Each node in the graph is a quantum operation (`op_id`). A directed edge `(u, v)` exists if operation `v` is causally dependent on the classical outcome of operation `u`. The NLCM ensures that the distributed scheduler never executes an operation until all of its predecessors in the graph have completed. A teleportation operation `T` from A to B adds an edge from `BSM(T)` at A to `Correction(T)` at B.

## 5. Choreography of Quantum State Transference: A Protocol-Level Analysis

The following sequence describes the end-to-end flow of a single teleportation event managed by the NLCM.

1.  **Initiation:** A quantum program running on `Node A` requires moving `LogicalQubit-5` to `Node B`. It calls `NLCM.Teleport(LogicalQubit-5, NodeB)`. The NLCM creates a new `TeleportationOperation` record with status `REQUESTED`.

2.  **Resource Reservation:** The NLCM's Protocol Engine queries the EDN interface for an available, high-fidelity entangled pair between `A` and `B`. Upon success, it receives a `pair_id`. It updates the `TeleportationOperation` record with this `pair_id` and changes its status to `RESOURCE_ALLOCATED`. It also marks the `EntangledPair` as `RESERVED`.

3.  **Source-Side Execution:** The NLCM notifies the QPU Controller at `Node A` that the resources are ready. The controller schedules the local gates (CNOT, Hadamard) and the BSM on `LogicalQubit-5` and its half of the entangled pair.

4.  **Outcome Reporting:** Upon measurement, `Node A`'s controller immediately sends the two classical bits to the NLCM via `ReportBSM(op_id, [b1, b2])`.

5.  **Correction Calculation and Dispatch:** The NLCM receives the outcome.
    *   It updates the `TeleportationOperation` record with the `bsm_outcome` and changes the status to `BSM_REPORTED`.
    *   It calculates the required corrections: if `b2` is 1, apply X; if `b1` is 1, apply Z. It stores this in the `correction_ops` field.
    *   It updates the logical qubit registry to indicate `LogicalQubit-5` is now physically located at `Node B`, but in a "pending correction" state.
    *   It places a `CorrectionTask(LogicalQubit-5, [X, Z])` message onto a reliable, ordered message queue for `Node B`. The status is updated to `CORRECTION_DISPATCHED`.

6.  **Destination-Side Execution:** The QPU Controller at `Node B` has been polling for the arrival of `LogicalQubit-5`. It receives the `CorrectionTask` from its message queue. It applies the specified Pauli gates to its half of the entangled pair, which has now *become* `LogicalQubit-5`.

7.  **Finalization:** `Node B`'s controller sends a confirmation `Ack(op_id)` to the NLCM. The NLCM updates the `TeleportationOperation` status to `COMPLETED`, marks the `EntangledPair` as `CONSUMED`, and removes the "pending correction" flag from `LogicalQubit-5` in its registry. The qubit is now fully operational at its new location.

## 6. Navigating Decoherence and Channel Asymmetry: Robustness Paradigms

*   **Entanglement Timeout:** Every `EntangledPair` record has a `generation_timestamp`. If a pair remains in the `AVAILABLE` or `RESERVED` state for longer than a configured coherence time (`T2*`), a background process marks it as `DECOHERED` and purges it. If a teleportation operation is assigned a pair that subsequently decoheres, the operation is `FAILED` and must be retried.
*   **Classical Message Loss:** All communication between controllers and the NLCM uses a protocol with guaranteed delivery and acknowledgements. If the `ReportBSM` message from `Node A` is lost, the `TeleportationOperation` will eventually time out. The NLCM will then mark the operation as `FAILED`, release the resources, and notify the application. The state of the source qubit is now unknown and likely destroyed; higher-level error correction must handle this.
*   **Race Conditions:** The NLCM Registry's use of a consensus protocol like Raft prevents split-brain scenarios. All state-mutating operations are serialized through the Raft log, ensuring a single, linearizable history of all non-local events.

## 7. Extrapolating the Manifold: Multi-Hop Teleportation and Entanglement Swapping

The NLCM architecture is extensible to more complex non-local operations.

*   **Entanglement Swapping:** To create entanglement between `Node A` and `Node C` via an intermediary `Node B`, the application would request it from the NLCM. The NLCM would orchestrate the process:
    1.  Allocate an (A, B) pair and a (B, C) pair.
    2.  Instruct `Node B` to perform a BSM on its two halves of the pairs.
    3.  Receive the classical outcome from `Node B`.
    4.  Calculate the necessary Pauli correction for `Node C`'s qubit.
    5.  Dispatch the correction to `Node C`.
    This entire sequence is managed as a single atomic transaction within the NLCM.

*   **Integration with Logical Qubits:** When teleporting a qubit encoded in a QEC code, the `correction_ops` are not simple Pauli gates but logical Pauli operators. The NLCM must be aware of the QEC code being used to dispatch the correct sequence of physical gates that implements the required logical correction. The `LogicalQubit` registry would contain metadata about the encoding scheme for each qubit. This ensures that the non-local operations preserve the error-correcting properties of the computation.