import threading
import time
import random
import queue

class QuantumThread:
    """
    Represents a quantum thread with an associated entanglement state.
    """
    def __init__(self, thread_id, initial_entanglement_level=0.5):
        self.thread_id = thread_id
        self.entanglement_level = initial_entanglement_level
        self.is_running = False
        self.lock = threading.Lock()

    def update_entanglement(self, delta):
        """
        Updates the entanglement level of the thread.
        """
        with self.lock:
            self.entanglement_level += delta
            self.entanglement_level = max(0.0, min(1.0, self.entanglement_level))  # Clamp between 0 and 1

    def get_entanglement_level(self):
        """
        Returns the current entanglement level.
        """
        with self.lock:
            return self.entanglement_level

    def start(self):
        """
        Marks the thread as running.
        """
        self.is_running = True

    def stop(self):
        """
        Marks the thread as stopped.
        """
        self.is_running = False

    def is_alive(self):
        """
        Checks if the thread is running.
        """
        return self.is_running

class EntanglementEvent:
    """
    Represents an event related to entanglement changes.
    """
    def __init__(self, thread_id, old_level, new_level, timestamp=None):
        self.thread_id = thread_id
        self.old_level = old_level
        self.new_level = new_level
        self.timestamp = timestamp if timestamp is not None else time.time()

    def __str__(self):
        return f"EntanglementEvent(thread_id={self.thread_id}, old_level={self.old_level:.2f}, new_level={self.new_level:.2f}, timestamp={self.timestamp})"


class ThreadEntanglementMonitor:
    """
    Monitors and manages the entanglement states of quantum threads.
    """
    def __init__(self, decay_rate=0.01, entanglement_threshold=0.9, event_queue_size=100):
        self.threads = {}  # thread_id: QuantumThread
        self.decay_rate = decay_rate
        self.entanglement_threshold = entanglement_threshold
        self.event_queue = queue.Queue(maxsize=event_queue_size)
        self.lock = threading.Lock()
        self.monitoring_thread = None
        self.is_monitoring = False

    def register_thread(self, thread_id, initial_entanglement_level=0.5):
        """
        Registers a new quantum thread with the monitor.
        """
        with self.lock:
            if thread_id in self.threads:
                raise ValueError(f"Thread with ID {thread_id} already registered.")
            self.threads[thread_id] = QuantumThread(thread_id, initial_entanglement_level)

    def unregister_thread(self, thread_id):
        """
        Unregisters a quantum thread from the monitor.
        """
        with self.lock:
            if thread_id not in self.threads:
                raise ValueError(f"Thread with ID {thread_id} not registered.")
            del self.threads[thread_id]

    def get_thread(self, thread_id):
        """
        Retrieves a registered thread.
        """
        with self.lock:
            if thread_id not in self.threads:
                raise ValueError(f"Thread with ID {thread_id} not registered.")
            return self.threads[thread_id]

    def start_monitoring(self, interval=0.1):
        """
        Starts the entanglement monitoring process.
        """
        if self.is_monitoring:
            return  # Already monitoring

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """
        Stops the entanglement monitoring process.
        """
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
            self.monitoring_thread = None

    def _monitor_loop(self, interval):
        """
        The main monitoring loop.
        """
        while self.is_monitoring:
            with self.lock:
                for thread_id, thread in self.threads.items():
                    if thread.is_alive():
                        old_level = thread.get_entanglement_level()
                        # Simulate entanglement decay and random fluctuations
                        decay = -self.decay_rate * old_level
                        fluctuation = random.uniform(-0.05, 0.05)  # Small random fluctuation
                        delta = decay + fluctuation

                        thread.update_entanglement(delta)
                        new_level = thread.get_entanglement_level()

                        if abs(new_level - old_level) > 0.001: # Only log significant changes
                            event = EntanglementEvent(thread_id, old_level, new_level)
                            try:
                                self.event_queue.put_nowait(event)
                            except queue.Full:
                                print("Event queue is full.  Dropping event.") # Handle queue overflow

                        if new_level > self.entanglement_threshold:
                            print(f"Thread {thread_id} exceeded entanglement threshold: {new_level:.2f}")
                            # Potentially trigger some action, like reducing load on the thread
                            # or initiating a controlled disentanglement process.
                            # Example: self.reduce_thread_load(thread_id)
            time.sleep(interval)

    def get_next_event(self, timeout=None):
        """
        Retrieves the next entanglement event from the queue.
        """
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def reduce_thread_load(self, thread_id):
        """
        Placeholder for a function to reduce the load on a thread.
        This would need to be implemented based on the specific application.
        """
        print(f"Reducing load on thread {thread_id} (implementation needed).")
        # In a real system, this would involve signaling the thread to reduce its workload,
        # potentially by pausing computations, reducing data processing rates, etc.
        pass

    def get_all_threads(self):
        """
        Returns a dictionary of all registered threads.
        """
        with self.lock:
            return self.threads.copy() # Return a copy to avoid external modification