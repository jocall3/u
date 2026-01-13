# src/runtime/EnvAwareQubitAllocator.py

import time
import random
import threading
from enum import Enum
from typing import List, Dict, Optional, Tuple, Set

# --- Constants and Configuration ---
# These values would be derived from actual hardware characterization.
BASE_COHERENCE_T1_US = 150.0  # T1 in microseconds
BASE_GATE_FIDELITY_1Q = 0.9998
BASE_GATE_FIDELITY_2Q = 0.995
BASE_READOUT_FIDELITY = 0.98

# Environmental baselines and sensitivity factors
TEMP_BASELINE_MK = 10.0  # Millikelvin
TEMP_SENSITIVITY = 0.05  # 5% coherence degradation per mK deviation
EM_INTERFERENCE_BASELINE_DB = -120.0  # dBm
EM_SENSITIVITY = 0.001 # 0.1% fidelity degradation per dB increase
COSMIC_RAY_FLUX_BASELINE = 0.01 # hits/qubit/sec
COSMIC_RAY_IMPACT_PROB = 0.1 # Probability a hit causes a major decoherence event

# --- Enums and Data Structures ---

class QubitStatus(Enum):
    """Represents the operational state of a physical qubit."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    CALIBRATING = "calibrating"
    UNSTABLE = "unstable"
    OFFLINE = "offline"

class PhysicalQubit:
    """
    Models a single physical qubit on a quantum processor, including its
    intrinsic properties and environmentally-influenced current state.
    """
    def __init__(self, qubit_id: int, location: Tuple[int, int]):
        self.id = qubit_id
        self.location = location # Physical (x, y) on the chip

        # Intrinsic, "ideal" properties (post-fabrication characterization)
        self.base_t1_coherence_us = random.uniform(0.95, 1.05) * BASE_COHERENCE_T1_US
        self.base_gate_fidelity_1q = random.uniform(0.98, 1.02) * BASE_GATE_FIDELITY_1Q
        self.base_gate_fidelity_2q = random.uniform(0.98, 1.02) * BASE_GATE_FIDELITY_2Q
        self.base_readout_fidelity = random.uniform(0.99, 1.01) * BASE_READOUT_FIDELITY

        # Dynamic, real-time properties influenced by the environment
        self.current_t1_coherence_us = self.base_t1_coherence_us
        self.current_gate_fidelity_1q = self.base_gate_fidelity_1q
        self.current_gate_fidelity_2q = self.base_gate_fidelity_2q
        self.current_readout_fidelity = self.base_readout_fidelity
        
        self.status: QubitStatus = QubitStatus.AVAILABLE
        self.last_calibration_time: float = time.time()

    def __repr__(self) -> str:
        return (f"Qubit(id={self.id}, status={self.status.value}, "
                f"T1={self.current_t1_coherence_us:.2f}us, "
                f"F_1Q={self.current_gate_fidelity_1q:.4f}, "
                f"F_2Q={self.current_gate_fidelity_2q:.4f})")

class EnvironmentalSensorSuite:
    """
    Simulates a suite of sensors monitoring the QPU's operational environment.
    In a real system, this would interface with actual hardware sensors.
    """
    def get_cryostat_temperature_mK(self) -> float:
        """Simulates temperature fluctuations around the baseline."""
        return TEMP_BASELINE_MK + (random.random() - 0.5) * 0.5 # +/- 0.25 mK drift

    def get_em_interference_dB(self) -> float:
        """Simulates ambient electromagnetic noise."""
        return EM_INTERFERENCE_BASELINE_DB + random.expovariate(0.5) # Occasional spikes

    def get_cosmic_ray_flux(self) -> float:
        """Simulates detection of high-energy particle events."""
        return COSMIC_RAY_FLUX_BASELINE * (1 + random.uniform(-0.1, 2.0)) # Flux can vary

    def get_magnetic_field_stability(self) -> float:
        """Returns a stability factor (1.0 is perfect)."""
        return 1.0 - random.uniform(0, 0.0001) # Small drifts

class QuantumProcessor:
    """
    Represents the entire quantum processing unit (QPU), containing the qubits,
    their connectivity, and environmental sensors.
    """
    def __init__(self, num_qubits: int, grid_size: Tuple[int, int]):
        self.qubits: Dict[int, PhysicalQubit] = {}
        self.connectivity: Dict[int, Set[int]] = {}
        self._initialize_qubits(num_qubits, grid_size)
        self.sensors = EnvironmentalSensorSuite()

    def _initialize_qubits(self, num_qubits: int, grid_size: Tuple[int, int]):
        """Creates and arranges qubits in a grid topology."""
        rows, cols = grid_size
        if num_qubits > rows * cols:
            raise ValueError("Number of qubits exceeds grid capacity.")
        
        count = 0
        for r in range(rows):
            for c in range(cols):
                if count >= num_qubits:
                    break
                qubit_id = count
                self.qubits[qubit_id] = PhysicalQubit(qubit_id, location=(r, c))
                
                # Establish connectivity with neighbors
                self.connectivity[qubit_id] = set()
                # Left neighbor
                if c > 0: self.connectivity[qubit_id].add(qubit_id - 1)
                # Right neighbor
                if c < cols - 1 and (qubit_id + 1) < num_qubits: self.connectivity[qubit_id].add(qubit_id + 1)
                # Top neighbor
                if r > 0: self.connectivity[qubit_id].add(qubit_id - cols)
                # Bottom neighbor
                if r < rows - 1 and (qubit_id + cols) < num_qubits: self.connectivity[qubit_id].add(qubit_id + cols)
                
                count += 1

# --- Core Allocator Logic ---

class EnvAwareQubitAllocator:
    """
    Dynamically allocates qubits for quantum computations based on real-time
    environmental data and qubit health metrics. This serves as the intelligent
    resource manager between the quantum compiler and the physical hardware.
    """
    def __init__(self, processor: QuantumProcessor):
        self.processor = processor
        self.lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None

    def start_background_monitoring(self, interval_seconds: float = 1.0):
        """
        Initiates a background thread to continuously update qubit states
        based on environmental sensor readings.
        """
        if self._monitoring:
            print("Monitoring is already active.")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval_seconds,), daemon=True
        )
        self._monitor_thread.start()
        print("Environmental monitoring thread started.")

    def stop_background_monitoring(self):
        """Stops the background monitoring thread."""
        if not self._monitoring:
            return
        self._monitoring = False
        self._monitor_thread.join()
        print("Environmental monitoring thread stopped.")

    def _monitor_loop(self, interval_seconds: float):
        """The core loop for the background monitoring thread."""
        while self._monitoring:
            self._update_all_qubit_states()
            time.sleep(interval_seconds)

    def _update_all_qubit_states(self):
        """
        Polls environmental sensors and updates the dynamic properties of all
        qubits on the processor. This is the heart of the environment-aware system.
        """
        with self.lock:
            # 1. Get current environmental readings
            temp = self.processor.sensors.get_cryostat_temperature_mK()
            em_noise = self.processor.sensors.get_em_interference_dB()
            cosmic_flux = self.processor.sensors.get_cosmic_ray_flux()
            mag_stability = self.processor.sensors.get_magnetic_field_stability()

            # 2. Calculate environmental degradation factors
            temp_deviation = abs(temp - TEMP_BASELINE_MK)
            temp_degradation = 1.0 - (temp_deviation * TEMP_SENSITIVITY)
            
            em_deviation = max(0, em_noise - EM_INTERFERENCE_BASELINE_DB)
            em_degradation = 1.0 - (em_deviation * EM_SENSITIVITY)

            # 3. Apply updates to each qubit
            for qubit in self.processor.qubits.values():
                # Update coherence based on temperature
                qubit.current_t1_coherence_us = qubit.base_t1_coherence_us * temp_degradation * mag_stability

                # Update fidelities based on EM noise
                qubit.current_gate_fidelity_1q = qubit.base_gate_fidelity_1q * em_degradation
                qubit.current_gate_fidelity_2q = qubit.base_gate_fidelity_2q * em_degradation
                qubit.current_readout_fidelity = qubit.base_readout_fidelity * em_degradation

                # Stochastic event handling (e.g., cosmic ray strikes)
                if random.random() < cosmic_flux * COSMIC_RAY_IMPACT_PROB:
                    print(f"EVENT: Cosmic ray strike detected near Qubit {qubit.id}. Marking as unstable.")
                    qubit.status = QubitStatus.UNSTABLE
                    # In a real system, this would trigger a recalibration routine
                    qubit.current_t1_coherence_us *= 0.1 # Drastic temporary degradation
                
                # Simple state machine for recovery
                if qubit.status == QubitStatus.UNSTABLE and random.random() < 0.2:
                    print(f"EVENT: Qubit {qubit.id} has been recalibrated and is now available.")
                    qubit.status = QubitStatus.AVAILABLE


    def _calculate_quality_metric(self, qubit: PhysicalQubit) -> float:
        """
        Computes a holistic quality score for a qubit based on its current state.
        The weights can be tuned based on the target algorithm's sensitivity
        (e.g., some algorithms are more sensitive to coherence, others to readout).
        """
        if qubit.status != QubitStatus.AVAILABLE:
            return 0.0

        # Normalize metrics to a common scale (e.g., 0 to 1)
        norm_t1 = min(1.0, qubit.current_t1_coherence_us / BASE_COHERENCE_T1_US)
        norm_f1q = (qubit.current_gate_fidelity_1q - 0.99) / (1.0 - 0.99)
        norm_f2q = (qubit.current_gate_fidelity_2q - 0.98) / (1.0 - 0.98)
        norm_fr = (qubit.current_readout_fidelity - 0.95) / (1.0 - 0.95)

        # Weighted sum for the final score
        # Weights prioritize 2Q fidelity and coherence, as they are often bottlenecks.
        weights = {'t1': 0.3, 'f1q': 0.1, 'f2q': 0.4, 'fr': 0.2}
        
        score = (weights['t1'] * norm_t1 +
                 weights['f1q'] * norm_f1q +
                 weights['f2q'] * norm_f2q +
                 weights['fr'] * norm_fr)
        
        return max(0.0, score) # Ensure score is non-negative

    def request_qubits(self, num_qubits: int, min_quality_score: float = 0.7) -> Optional[List[int]]:
        """
        The primary interface for requesting a set of high-quality qubits.
        
        Args:
            num_qubits: The number of qubits required for the computation.
            min_quality_score: The minimum acceptable quality score for any qubit in the set.

        Returns:
            A list of qubit IDs if the request can be fulfilled, otherwise None.
        """
        with self.lock:
            # Ensure our view of the hardware is current
            self._update_all_qubit_states()

            # 1. Score all available qubits
            scored_qubits = []
            for qubit in self.processor.qubits.values():
                if qubit.status == QubitStatus.AVAILABLE:
                    score = self._calculate_quality_metric(qubit)
                    if score >= min_quality_score:
                        scored_qubits.append((score, qubit))
            
            # 2. Sort by score in descending order
            scored_qubits.sort(key=lambda x: x[0], reverse=True)

            # 3. Check if enough high-quality qubits exist
            if len(scored_qubits) < num_qubits:
                print(f"Allocation failed: Not enough high-quality qubits available. "
                      f"Found {len(scored_qubits)}, need {num_qubits}.")
                return None

            # 4. Select the top N qubits.
            # A more advanced allocator would consider the required connectivity graph here.
            # For this pseudocode, we simply take the best N.
            selected_qubits = [qubit for score, qubit in scored_qubits[:num_qubits]]
            selected_ids = [qubit.id for qubit in selected_qubits]

            # 5. Mark selected qubits as allocated
            for qubit in selected_qubits:
                qubit.status = QubitStatus.ALLOCATED

            print(f"Successfully allocated {num_qubits} qubits: {selected_ids}")
            return selected_ids

    def release_qubits(self, qubit_ids: List[int]):
        """
        Returns a set of allocated qubits to the available pool.
        """
        with self.lock:
            for q_id in qubit_ids:
                if q_id in self.processor.qubits:
                    qubit = self.processor.qubits[q_id]
                    if qubit.status == QubitStatus.ALLOCATED:
                        qubit.status = QubitStatus.AVAILABLE
                    else:
                        print(f"Warning: Attempted to release qubit {q_id} which was not allocated.")
            print(f"Released qubits: {qubit_ids}")

    def get_hardware_snapshot(self) -> str:
        """Provides a string representation of the current state of all qubits."""
        with self.lock:
            report = "--- Quantum Processor State Snapshot ---\n"
            for q_id, qubit in sorted(self.processor.qubits.items()):
                report += f"  {qubit}\n"
            report += "----------------------------------------\n"
            return report

# --- Demonstration ---

if __name__ == "__main__":
    print("Initializing a 16-qubit quantum processor (4x4 grid)...")
    qpu = QuantumProcessor(num_qubits=16, grid_size=(4, 4))
    
    print("Instantiating the Environment-Aware Qubit Allocator...")
    allocator = EnvAwareQubitAllocator(qpu)
    
    print("\nStarting background environmental monitoring...")
    allocator.start_background_monitoring(interval_seconds=2.0)
    
    # Allow some time for the monitor to run and states to fluctuate
    time.sleep(3)

    print("\n--- Allocation Scenario 1: Requesting 5 high-quality qubits ---")
    print(allocator.get_hardware_snapshot())
    
    allocated_set_1 = allocator.request_qubits(num_qubits=5, min_quality_score=0.75)
    
    if allocated_set_1:
        print(f"\nReceived qubit set 1: {allocated_set_1}")
        print("Simulating a quantum computation for 5 seconds...")
        time.sleep(5)
        print(allocator.get_hardware_snapshot()) # Show state during allocation
        allocator.release_qubits(allocated_set_1)
    else:
        print("\nCould not fulfill request for qubit set 1.")

    print("\n--- Allocation Scenario 2: Requesting 12 qubits (might fail) ---")
    # This request is larger and might fail if environmental conditions are poor
    # or if a cosmic ray has marked some qubits as unstable.
    time.sleep(3) # Wait for more environmental changes
    print(allocator.get_hardware_snapshot())
    
    allocated_set_2 = allocator.request_qubits(num_qubits=12, min_quality_score=0.6)
    
    if allocated_set_2:
        print(f"\nReceived qubit set 2: {allocated_set_2}")
        print("Simulating another computation...")
        time.sleep(4)
        allocator.release_qubits(allocated_set_2)
    else:
        print("\nCould not fulfill request for qubit set 2, as expected under fluctuating conditions.")

    print("\n--- Final State ---")
    print(allocator.get_hardware_snapshot())

    print("Stopping background monitoring...")
    allocator.stop_background_monitoring()
    print("Demonstration complete.")