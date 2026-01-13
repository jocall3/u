# src/distributed/QPUClusterManager.py

import threading
import time
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import random
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Enums and Data Structures ---

class QPUStatus(Enum):
    """Enumeration for the operational status of a Quantum Processing Unit."""
    ONLINE_IDLE = "ONLINE_IDLE"
    ONLINE_BUSY = "ONLINE_BUSY"
    CALIBRATING = "CALIBRATING"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

class JobStatus(Enum):
    """Enumeration for the status of a submitted quantum computation job."""
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class QuantumJob:
    """
    Represents a quantum computation job submitted to the cluster.
    This structure encapsulates the quantum circuit and its execution requirements.
    """
    def __init__(self, circuit: Any, required_qubits: int, priority: int = 0, metadata: Optional[Dict] = None):
        self.job_id = str(uuid.uuid4())
        self.circuit = circuit  # Could be a Qiskit, Cirq, or other framework's circuit object
        self.required_qubits = required_qubits
        self.priority = priority
        self.metadata = metadata if metadata is not None else {}
        self.status = JobStatus.PENDING
        self.submission_time = time.time()
        self.execution_start_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.assigned_qpu_id: Optional[str] = None
        self.results: Optional[Any] = None
        self.error_message: Optional[str] = None

        # Advanced requirements for sophisticated scheduling
        self.required_connectivity: Optional[List[Tuple[int, int]]] = self.metadata.get("connectivity")
        self.required_coherence_t1: Optional[float] = self.metadata.get("min_t1_us")
        self.required_gate_fidelity: Optional[Dict[str, float]] = self.metadata.get("min_gate_fidelity")

    def __repr__(self):
        return f"<QuantumJob id={self.job_id} status={self.status.value} qubits={self.required_qubits}>"

class QPUDescriptor:
    """
    Represents a single QPU within the cluster, holding its static capabilities
    and dynamic state information.
    """
    def __init__(self, qpu_id: str, capabilities: Dict[str, Any]):
        self.qpu_id = qpu_id
        self.status = QPUStatus.OFFLINE
        self.last_heartbeat = 0.0

        # Static Capabilities
        self.total_qubits: int = capabilities.get("qubit_count", 0)
        self.topology: List[Tuple[int, int]] = capabilities.get("connectivity_graph", [])
        self.supported_gates: List[str] = capabilities.get("gate_set", [])
        self.native_architecture: str = capabilities.get("architecture", "unknown")

        # Dynamic State & Performance Metrics (updated via telemetry)
        self.current_job_id: Optional[str] = None
        self.job_queue_depth: int = 0
        self.qubit_fidelities: Dict[int, float] = {} # Qubit index -> Readout fidelity
        self.gate_fidelities: Dict[str, Dict[Tuple, float]] = {} # Gate name -> Qubits -> Fidelity
        self.coherence_times_t1: Dict[int, float] = {} # Qubit index -> T1 time in µs
        self.coherence_times_t2: Dict[int, float] = {} # Qubit index -> T2 time in µs

    def update_telemetry(self, telemetry_data: Dict[str, Any]):
        """Updates the QPU's dynamic state from incoming telemetry."""
        self.status = telemetry_data.get("status", self.status)
        self.job_queue_depth = telemetry_data.get("queue_depth", self.job_queue_depth)
        self.qubit_fidelities = telemetry_data.get("qubit_fidelities", self.qubit_fidelities)
        self.gate_fidelities = telemetry_data.get("gate_fidelities", self.gate_fidelities)
        self.coherence_times_t1 = telemetry_data.get("t1_times", self.coherence_times_t1)
        self.coherence_times_t2 = telemetry_data.get("t2_times", self.coherence_times_t2)
        self.last_heartbeat = time.time()

    def is_available_for_job(self, job: QuantumJob) -> bool:
        """Checks if this QPU is a potential candidate for a given job."""
        if self.status != QPUStatus.ONLINE_IDLE:
            return False
        if self.total_qubits < job.required_qubits:
            return False
        # More complex checks (topology mapping, fidelity) would go here
        return True

    def __repr__(self):
        return f"<QPUDescriptor id={self.qpu_id} status={self.status.value} qubits={self.total_qubits}>"


# --- The Main Orchestrator ---

class QPUClusterManager:
    """
    Orchestrates the dynamic distribution of quantum computations across a
    heterogeneous cluster of QPUs. This class acts as the central brain,
    managing job queues, QPU states, and intelligent scheduling.
    """
    def __init__(self, heartbeat_timeout: int = 60):
        self.qpu_registry: Dict[str, QPUDescriptor] = {}
        self.job_queue: deque[QuantumJob] = deque()
        self.running_jobs: Dict[str, QuantumJob] = {}
        self.completed_jobs: Dict[str, QuantumJob] = {}

        self._lock = threading.Lock()
        self._orchestration_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.heartbeat_timeout = heartbeat_timeout

    def register_qpu(self, qpu_id: str, capabilities: Dict[str, Any]):
        """Registers a new QPU with the cluster."""
        with self._lock:
            if qpu_id in self.qpu_registry:
                logger.warning(f"QPU {qpu_id} is already registered. Updating capabilities.")
            else:
                logger.info(f"Registering new QPU: {qpu_id} with {capabilities.get('qubit_count')} qubits.")
            self.qpu_registry[qpu_id] = QPUDescriptor(qpu_id, capabilities)

    def update_qpu_telemetry(self, qpu_id: str, telemetry_data: Dict[str, Any]):
        """Receives and processes a heartbeat/telemetry update from a QPU."""
        with self._lock:
            qpu = self.qpu_registry.get(qpu_id)
            if qpu:
                qpu.update_telemetry(telemetry_data)
                logger.debug(f"Received telemetry for QPU {qpu_id}. Status: {qpu.status.value}")
            else:
                logger.warning(f"Received telemetry for unregistered QPU {qpu_id}.")

    def submit_job(self, job: QuantumJob) -> str:
        """Submits a new quantum job to the cluster's central queue."""
        with self._lock:
            self.job_queue.append(job)
            logger.info(f"Job {job.job_id} submitted and added to queue. Queue size: {len(self.job_queue)}")
        return job.job_id

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Retrieves the status and results of a specific job."""
        with self._lock:
            job = self.running_jobs.get(job_id) or self.completed_jobs.get(job_id)
            if job:
                return {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "assigned_qpu": job.assigned_qpu_id,
                    "submission_time": job.submission_time,
                    "start_time": job.execution_start_time,
                    "completion_time": job.completion_time,
                    "results": job.results,
                    "error": job.error_message
                }
            # Check the pending queue as well
            for pending_job in self.job_queue:
                if pending_job.job_id == job_id:
                    return {"job_id": job_id, "status": JobStatus.PENDING.value}
        return None

    def _calculate_qpu_score(self, qpu: QPUDescriptor, job: QuantumJob) -> float:
        """
        Calculates a suitability score for a QPU-job pair.
        This is the core of the scheduling heuristic. A higher score is better.
        A score of -1.0 indicates the QPU is not a candidate.
        """
        if not qpu.is_available_for_job(job):
            return -1.0

        # --- Scoring Factors ---
        # 1. Qubit Headroom (prefer QPUs that are not a tight fit)
        qubit_headroom = qpu.total_qubits - job.required_qubits
        score = 0.2 * (1 - 1 / (1 + qubit_headroom)) # Normalized headroom factor

        # 2. Coherence Time Score (critical for deep circuits)
        if job.required_coherence_t1 and qpu.coherence_times_t1:
            # Simple average T1 time for now. A real implementation would map to specific qubits.
            avg_t1 = sum(qpu.coherence_times_t1.values()) / len(qpu.coherence_times_t1)
            if avg_t1 < job.required_coherence_t1:
                return -1.0 # Hard requirement not met
            score += 0.4 * (avg_t1 / (job.required_coherence_t1 * 2)) # Reward higher T1

        # 3. Job Queue Depth (prefer less busy QPUs)
        score += 0.2 * (1 - qpu.job_queue_depth / 10.0) # Assume max queue of 10 for normalization

        # 4. Randomness Factor (for tie-breaking and exploration)
        score += 0.1 * random.random()
        
        # 5. Topology Match (placeholder for a complex graph isomorphism/subgraph problem)
        if job.required_connectivity:
            # This is a very hard problem. A simple proxy is to check edge density.
            # A real implementation would use a sophisticated mapping algorithm.
            pass # For now, we don't penalize if not specified

        return max(0, score) # Ensure score is non-negative

    def _find_optimal_qpu(self, job: QuantumJob) -> Optional[str]:
        """
        Selects the best available QPU for a given job based on a scoring model.
        """
        best_qpu_id = None
        max_score = -1.0

        available_qpus = [qpu for qpu in self.qpu_registry.values() if qpu.status == QPUStatus.ONLINE_IDLE]
        if not available_qpus:
            return None

        logger.debug(f"Finding optimal QPU for job {job.job_id} among {len(available_qpus)} idle QPUs.")

        for qpu in available_qpus:
            score = self._calculate_qpu_score(qpu, job)
            logger.debug(f"QPU {qpu.qpu_id} scored {score:.4f} for job {job.job_id}.")
            if score > max_score:
                max_score = score
                best_qpu_id = qpu.qpu_id

        if best_qpu_id:
            logger.info(f"Optimal QPU for job {job.job_id} is {best_qpu_id} with score {max_score:.4f}.")
        else:
            logger.info(f"No suitable QPU found for job {job.job_id} at this time.")

        return best_qpu_id

    def _dispatch_job(self, job: QuantumJob, qpu_id: str):
        """
        "Dispatches" a job to a QPU. In a real system, this would involve
        communicating with the QPU's control hardware/API.
        """
        with self._lock:
            qpu = self.qpu_registry[qpu_id]
            job.status = JobStatus.RUNNING
            job.assigned_qpu_id = qpu_id
            job.execution_start_time = time.time()
            self.running_jobs[job.job_id] = job
            
            qpu.status = QPUStatus.ONLINE_BUSY
            qpu.current_job_id = job.job_id

        logger.info(f"Dispatching job {job.job_id} to QPU {qpu_id}.")
        # --- SIMULATION HOOK ---
        # In a real system, this would be an async API call to the QPU controller.
        # Here, we simulate the execution in a separate thread.
        threading.Thread(target=self._simulate_qpu_execution, args=(job.job_id, qpu_id)).start()

    def _simulate_qpu_execution(self, job_id: str, qpu_id: str):
        """A placeholder function to simulate a QPU running a job."""
        # Simulate execution time based on circuit complexity
        job = self.running_jobs[job_id]
        execution_time = 2 + job.required_qubits * 0.1 + random.uniform(0, 2)
        time.sleep(execution_time)

        # Simulate a result or a failure
        if random.random() > 0.05: # 95% success rate
            # Simulate quantum measurement results
            results = {"counts": {bin(i)[2:].zfill(job.required_qubits): random.randint(0, 1024) for i in range(2**min(job.required_qubits, 4))}}
            self._handle_job_completion(job_id, results, None)
        else:
            error_msg = "Simulated decoherence cascade failure."
            self._handle_job_completion(job_id, None, error_msg)

    def _handle_job_completion(self, job_id: str, results: Optional[Any], error_message: Optional[str]):
        """Callback to handle the completion of a job."""
        with self._lock:
            if job_id not in self.running_jobs:
                logger.warning(f"Received completion for an unknown or already completed job: {job_id}")
                return

            job = self.running_jobs.pop(job_id)
            job.completion_time = time.time()
            job.results = results
            job.error_message = error_message
            job.status = JobStatus.COMPLETED if error_message is None else JobStatus.FAILED
            
            self.completed_jobs[job.job_id] = job

            # Update the QPU status
            qpu = self.qpu_registry.get(job.assigned_qpu_id)
            if qpu:
                qpu.status = QPUStatus.ONLINE_IDLE
                qpu.current_job_id = None
            
            if job.status == JobStatus.COMPLETED:
                logger.info(f"Job {job.job_id} completed successfully on QPU {job.assigned_qpu_id}.")
            else:
                logger.error(f"Job {job.job_id} failed on QPU {job.assigned_qpu_id}: {job.error_message}")

    def _check_qpu_heartbeats(self):
        """Periodically checks for stale QPUs and marks them as offline."""
        with self._lock:
            now = time.time()
            for qpu_id, qpu in self.qpu_registry.items():
                if qpu.status not in [QPUStatus.OFFLINE, QPUStatus.MAINTENANCE]:
                    if now - qpu.last_heartbeat > self.heartbeat_timeout:
                        logger.warning(f"QPU {qpu_id} heartbeat timed out. Marking as OFFLINE.")
                        qpu.status = QPUStatus.OFFLINE
                        # Handle job that was running on the failed QPU
                        if qpu.current_job_id:
                            self._requeue_failed_job(qpu.current_job_id)

    def _requeue_failed_job(self, job_id: str):
        """Handles requeuing a job from a failed QPU."""
        job = self.running_jobs.pop(job_id, None)
        if job:
            logger.info(f"Requeuing job {job.job_id} from failed QPU {job.assigned_qpu_id}.")
            job.status = JobStatus.PENDING
            job.assigned_qpu_id = None
            job.execution_start_time = None
            # Put it at the front of the queue
            self.job_queue.appendleft(job)

    def _orchestration_loop(self):
        """The main control loop for the cluster manager."""
        logger.info("QPU Cluster Manager orchestration loop started.")
        while not self._stop_event.is_set():
            try:
                self._check_qpu_heartbeats()

                with self._lock:
                    if not self.job_queue:
                        time.sleep(1) # Wait if no jobs
                        continue

                    # Prioritize jobs (simple for now, could be more complex)
                    # self.job_queue = deque(sorted(self.job_queue, key=lambda j: j.priority, reverse=True))
                    
                    job_to_schedule = self.job_queue[0] # Peek at the first job

                # Find a QPU outside the lock to avoid blocking telemetry updates
                optimal_qpu_id = self._find_optimal_qpu(job_to_schedule)

                if optimal_qpu_id:
                    with self._lock:
                        # Re-verify that the job is still at the front of the queue
                        if self.job_queue and self.job_queue[0].job_id == job_to_schedule.job_id:
                            job = self.job_queue.popleft()
                            job.status = JobStatus.SCHEDULED
                            self._dispatch_job(job, optimal_qpu_id)
                else:
                    # No suitable QPU found, wait before retrying
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}", exc_info=True)
                time.sleep(5) # Avoid rapid-fire errors

    def start(self):
        """Starts the manager's orchestration thread."""
        if self._orchestration_thread is not None:
            logger.warning("Manager is already running.")
            return
        self._stop_event.clear()
        self._orchestration_thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        self._orchestration_thread.start()

    def stop(self):
        """Stops the manager's orchestration thread gracefully."""
        if self._orchestration_thread is None:
            logger.warning("Manager is not running.")
            return
        logger.info("Stopping QPU Cluster Manager...")
        self._stop_event.set()
        self._orchestration_thread.join(timeout=5)
        self._orchestration_thread = None
        logger.info("QPU Cluster Manager stopped.")


if __name__ == '__main__':
    # --- Example Usage and Simulation ---
    print("--- QPU Cluster Manager Simulation ---")

    # 1. Initialize the Manager
    manager = QPUClusterManager()
    manager.start()

    # 2. Simulate QPUs coming online and registering
    qpu1_caps = {
        "qubit_count": 16,
        "connectivity_graph": [(i, i + 1) for i in range(15)],
        "gate_set": ["CX", "U3", "H"],
        "architecture": "SuperconductingTransmon_v1"
    }
    qpu2_caps = {
        "qubit_count": 64,
        "connectivity_graph": [(i, i + 8) for i in range(56)], # Grid-like
        "gate_set": ["CX", "U3", "H", "RZ"],
        "architecture": "SuperconductingTransmon_v2"
    }
    qpu3_caps = {
        "qubit_count": 8,
        "connectivity_graph": [], # All-to-all
        "gate_set": ["MS", "RY", "RX"],
        "architecture": "TrappedIon_v3"
    }
    manager.register_qpu("qpu-aspen-1", qpu1_caps)
    manager.register_qpu("qpu-eagle-1", qpu2_caps)
    manager.register_qpu("qpu-ionq-aria-sim", qpu3_caps)

    # 3. Simulate telemetry updates from QPUs
    def telemetry_simulator(qpu_id, stop_event):
        while not stop_event.is_set():
            telemetry = {
                "status": random.choice([QPUStatus.ONLINE_IDLE, QPUStatus.ONLINE_IDLE, QPUStatus.CALIBRATING]),
                "queue_depth": random.randint(0, 3),
                "t1_times": {i: random.uniform(80, 120) for i in range(manager.qpu_registry[qpu_id].total_qubits)},
            }
            # Only send telemetry if the manager thinks the QPU is online
            if manager.qpu_registry[qpu_id].status != QPUStatus.ONLINE_BUSY:
                 manager.update_qpu_telemetry(qpu_id, telemetry)
            time.sleep(random.uniform(3, 6))

    stop_sim_event = threading.Event()
    sim_threads = [
        threading.Thread(target=telemetry_simulator, args=("qpu-aspen-1", stop_sim_event)),
        threading.Thread(target=telemetry_simulator, args=("qpu-eagle-1", stop_sim_event)),
        threading.Thread(target=telemetry_simulator, args=("qpu-ionq-aria-sim", stop_sim_event)),
    ]
    for t in sim_threads:
        t.start()

    # 4. Simulate job submissions
    time.sleep(2) # Wait for initial telemetry
    job_ids = []
    for i in range(10):
        qubits_needed = random.randint(4, 20)
        job = QuantumJob(
            circuit=f"Simulated circuit for {qubits_needed} qubits",
            required_qubits=qubits_needed,
            metadata={"min_t1_us": 90.0}
        )
        job_id = manager.submit_job(job)
        job_ids.append(job_id)
        time.sleep(random.uniform(0.5, 2))

    # 5. Monitor job statuses until all are complete
    print("\n--- Monitoring Jobs ---")
    all_done = False
    while not all_done:
        all_done = True
        statuses = []
        for job_id in job_ids:
            status_info = manager.get_job_status(job_id)
            statuses.append(f"Job {job_id[:8]}: {status_info['status']:<10} on {status_info.get('assigned_qpu', 'N/A')}")
            if status_info['status'] not in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
                all_done = False
        print(" | ".join(statuses), end='\r')
        time.sleep(1)

    print("\n\n--- All Jobs Processed ---")
    for job_id in job_ids:
        print(manager.get_job_status(job_id))

    # 6. Clean up
    stop_sim_event.set()
    for t in sim_threads:
        t.join()
    manager.stop()
    print("\n--- Simulation Finished ---")