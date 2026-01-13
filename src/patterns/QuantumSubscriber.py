import random
import time
import threading
from typing import Callable, Any, Dict, List

class QuantumSubscriber:
    """
    A subscriber that reacts to published values based on a simulated quantum entanglement.
    The reaction is probabilistic and influenced by a 'collapse' function.
    """

    def __init__(self, subscriber_id: str, collapse_function: Callable[[Any], float], entanglement_strength: float = 0.5):
        """
        Initializes the QuantumSubscriber.

        Args:
            subscriber_id: A unique identifier for the subscriber.
            collapse_function: A function that takes the published value and returns a probability (0.0 to 1.0).
            entanglement_strength: A float between 0.0 and 1.0 representing the strength of the entanglement.
                                   Higher values mean a stronger correlation with the published value.
        """
        self.subscriber_id = subscriber_id
        self.collapse_function = collapse_function
        self.entanglement_strength = entanglement_strength
        self.received_values: List[Any] = []
        self.lock = threading.Lock()

    def receive(self, value: Any) -> None:
        """
        Receives a published value and reacts to it based on the collapse function and entanglement strength.

        Args:
            value: The published value.
        """
        with self.lock:
            self.received_values.append(value)
            probability = self.collapse_function(value)

            # Simulate quantum randomness influenced by entanglement strength
            random_factor = random.uniform(-self.entanglement_strength, self.entanglement_strength)
            adjusted_probability = max(0.0, min(1.0, probability + random_factor))  # Ensure probability stays within [0, 1]

            if random.random() < adjusted_probability:
                self.react(value)
            else:
                self.no_react(value)

    def react(self, value: Any) -> None:
        """
        The reaction to a published value.  This is a placeholder; subclasses should override.

        Args:
            value: The published value.
        """
        print(f"Subscriber {self.subscriber_id} reacted to: {value}")
        time.sleep(random.uniform(0.1, 0.5))  # Simulate processing time

    def no_react(self, value: Any) -> None:
        """
        The action taken when the subscriber does not react. This is a placeholder; subclasses should override.

        Args:
            value: The published value.
        """
        print(f"Subscriber {self.subscriber_id} did not react to: {value}")
        time.sleep(random.uniform(0.05, 0.2))  # Simulate a shorter processing time

    def get_received_values(self) -> List[Any]:
        """
        Returns a list of all values received by the subscriber.

        Returns:
            A list of received values.
        """
        with self.lock:
            return list(self.received_values)  # Return a copy to avoid external modification

    def __repr__(self) -> str:
        return f"QuantumSubscriber(id={self.subscriber_id}, entanglement={self.entanglement_strength})"


if __name__ == '__main__':
    # Example usage:

    def example_collapse_function(data: Any) -> float:
        """
        A simple example collapse function that returns a probability based on the data type.
        """
        if isinstance(data, int):
            return 0.8  # High probability for integers
        elif isinstance(data, str):
            return 0.3  # Low probability for strings
        else:
            return 0.5  # Medium probability for other types

    subscriber1 = QuantumSubscriber("Sub1", example_collapse_function, entanglement_strength=0.7)
    subscriber2 = QuantumSubscriber("Sub2", example_collapse_function, entanglement_strength=0.3)

    # Simulate publishing values
    values_to_publish = [10, "hello", 3.14, 5, "world"]

    for value in values_to_publish:
        print(f"\nPublishing: {value}")
        subscriber1.receive(value)
        subscriber2.receive(value)

    print(f"\nSubscriber 1 received: {subscriber1.get_received_values()}")
    print(f"Subscriber 2 received: {subscriber2.get_received_values()}")