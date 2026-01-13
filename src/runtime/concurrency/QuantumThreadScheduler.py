import random
import threading
import time
from typing import List, Callable, Any, Dict

class QuantumThread:
    """
    Represents a thread in the quantum thread scheduler.
    Each thread has a probability of execution and can be entangled with other threads.
    """

    def __init__(self, target: Callable[[], Any], args: tuple = (), name: str = None, probability: float = 0.5):
        """
        Initializes a QuantumThread.

        Args:
            target: The function to be executed by the thread.
            args: The arguments to be passed to the target function.
            name: The name of the thread.
            probability: The probability of the thread being selected for execution in a given time slice.
        """
        self.target = target
        self.args = args
        self.name = name or f"QuantumThread-{id(self)}"
        self.probability = probability
        self.entangled_threads: List[QuantumThread] = []
        self.thread = threading.Thread(target=self._execute, name=self.name)
        self.result: Any = None
        self.exception: Exception = None
        self.is_done: bool = False
        self._lock = threading.Lock()

    def _execute(self):
        """
        Executes the thread's target function and captures any exceptions.
        """
        try:
            self.result = self.target(*self.args)
        except Exception as e:
            self.exception = e
        finally:
            with self._lock:
                self.is_done = True

    def start(self):
        """
        Starts the thread.
        """
        self.thread.start()

    def join(self, timeout: float = None):
        """
        Waits for the thread to complete.

        Args:
            timeout: The maximum time to wait for the thread to complete, in seconds.
        """
        self.thread.join(timeout)

    def entangle(self, other: 'QuantumThread'):
        """
        Entangles this thread with another thread.  Entanglement affects the probability
        of execution; if one entangled thread is chosen, the others are also more likely
        to be chosen.

        Args:
            other: The other QuantumThread to entangle with.
        """
        if other not in self.entangled_threads:
            self.entangled_threads.append(other)
        if self not in other.entangled_threads:
            other.entangled_threads.append(self)

    def is_alive(self) -> bool:
        """
        Checks if the underlying thread is still alive.
        """
        return self.thread.is_alive()

class QuantumThreadScheduler:
    """
    A scheduler for managing and executing quantum threads.
    It uses probabilistic selection and entanglement to simulate quantum-like behavior.
    """

    def __init__(self, time_slice: float = 0.01):
        """
        Initializes the QuantumThreadScheduler.

        Args:
            time_slice: The duration of each time slice in seconds.
        """
        self.threads: List[QuantumThread] = []
        self.time_slice = time_slice
        self._running: bool = False
        self._lock = threading.Lock()

    def create_thread(self, target: Callable[[], Any], args: tuple = (), name: str = None, probability: float = 0.5) -> QuantumThread:
        """
        Creates a new quantum thread and adds it to the scheduler.

        Args:
            target: The function to be executed by the thread.
            args: The arguments to be passed to the target function.
            name: The name of the thread.
            probability: The probability of the thread being selected for execution.

        Returns:
            The newly created QuantumThread.
        """
        thread = QuantumThread(target, args, name, probability)
        with self._lock:
            self.threads.append(thread)
        return thread

    def start(self):
        """
        Starts the scheduler, initiating the execution of quantum threads.
        """
        self._running = True
        self._run_loop()

    def stop(self):
        """
        Stops the scheduler.
        """
        self._running = False

    def _run_loop(self):
        """
        The main loop of the scheduler, responsible for selecting and executing threads.
        """
        while self._running:
            eligible_threads = [t for t in self.threads if t.is_alive()]
            if not eligible_threads:
                break  # Exit if no threads are running

            selected_threads = self._select_threads(eligible_threads)

            for thread in selected_threads:
                if not thread.thread.is_alive():
                    thread.start()

            time.sleep(self.time_slice)

    def _select_threads(self, eligible_threads: List[QuantumThread]) -> List[QuantumThread]:
        """
        Selects threads for execution based on their probabilities and entanglement.

        Args:
            eligible_threads: A list of threads that are eligible for execution.

        Returns:
            A list of threads that have been selected for execution in this time slice.
        """
        selected_threads: List[QuantumThread] = []
        for thread in eligible_threads:
            probability = thread.probability
            # Increase probability if entangled threads are already selected
            for entangled_thread in thread.entangled_threads:
                if entangled_thread in selected_threads:
                    probability = min(1.0, probability * 1.5)  # Increase probability, but cap at 1.0

            if random.random() < probability:
                selected_threads.append(thread)

        return selected_threads

    def join_all(self, timeout: float = None):
        """
        Waits for all threads to complete.

        Args:
            timeout: The maximum time to wait for all threads to complete, in seconds.
        """
        start_time = time.time()
        for thread in self.threads:
            remaining_time = timeout - (time.time() - start_time) if timeout else None
            if remaining_time is not None and remaining_time <= 0:
                break
            thread.join(remaining_time)

    def get_results(self) -> List[Any]:
        """
        Returns a list of results from all threads.  If a thread raised an exception,
        it will be re-raised here.
        """
        results = []
        for thread in self.threads:
            if thread.exception:
                raise thread.exception
            results.append(thread.result)
        return results

    def get_thread_states(self) -> Dict[str, bool]:
        """
        Returns a dictionary of thread names and their 'is_done' status.
        """
        return {thread.name: thread.is_done for thread in self.threads}

if __name__ == '__main__':
    # Example usage
    def task1(x: int) -> int:
        print(f"Task 1 executing with x={x}")
        time.sleep(0.1)
        return x * 2

    def task2(y: str) -> str:
        print(f"Task 2 executing with y={y}")
        time.sleep(0.2)
        return y.upper()

    def task3():
        print("Task 3 executing")
        time.sleep(0.3)
        raise ValueError("Task 3 failed")

    scheduler = QuantumThreadScheduler(time_slice=0.02)

    thread1 = scheduler.create_thread(target=task1, args=(5,), name="Thread-1", probability=0.7)
    thread2 = scheduler.create_thread(target=task2, args=("hello",), name="Thread-2", probability=0.6)
    thread3 = scheduler.create_thread(target=task3, name="Thread-3", probability=0.8)

    thread1.entangle(thread2)  # Entangle thread1 and thread2

    scheduler.start()
    scheduler.join_all(timeout=1.0)
    scheduler.stop()

    print("All threads finished.")

    try:
        results = scheduler.get_results()
        print("Results:", results)
    except Exception as e:
        print("Exception caught:", e)

    print("Thread states:", scheduler.get_thread_states())