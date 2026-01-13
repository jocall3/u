import random
import hashlib

class QuantumValue:
    """
    Represents a value in a quantum superposition.  The actual value is not
    determined until observed.  Uses a hash to represent the superposition
    state.
    """

    def __init__(self, possible_values):
        """
        Initializes the QuantumValue with a set of possible values.

        Args:
            possible_values: A list or set of possible values.  Must be hashable.
        """
        if not isinstance(possible_values, (list, set)):
            raise TypeError("possible_values must be a list or set")
        if not all(isinstance(x, (int, float, str, tuple, bytes, frozenset)) for x in possible_values):
            raise ValueError("All values in possible_values must be hashable (int, float, str, tuple, bytes, frozenset)")

        self.possible_values = frozenset(possible_values)  # Use frozenset for hashing
        self.superposition_hash = self._calculate_hash()
        self.observed_value = None

    def _calculate_hash(self):
        """
        Calculates a hash representing the superposition state.  The order
        of the possible values does not matter.
        """
        sorted_values = sorted(map(str, self.possible_values))  # Sort for consistent hashing
        combined_string = "".join(sorted_values).encode('utf-8')
        return hashlib.sha256(combined_string).hexdigest()

    def observe(self):
        """
        Observes the QuantumValue, collapsing the superposition and
        returning a single value.  The value is chosen randomly from the
        possible values.  Subsequent calls to observe will return the same value.
        """
        if self.observed_value is None:
            self.observed_value = random.choice(list(self.possible_values))
        return self.observed_value

    def get_superposition_hash(self):
        """
        Returns the hash representing the superposition state.
        """
        return self.superposition_hash

    def __repr__(self):
        if self.observed_value is None:
            return f"QuantumValue(superposition_hash='{self.superposition_hash}', possible_values={list(self.possible_values)})"
        else:
            return f"QuantumValue(observed_value={self.observed_value})"


class QuantumPublisher:
    """
    A publisher that maintains published values in a quantum superposition
    until they are observed.
    """

    def __init__(self):
        self.published_values = {}  # key: topic, value: QuantumValue

    def publish(self, topic, possible_values):
        """
        Publishes a value to the given topic.  The value is initially in a
        quantum superposition of the possible values.

        Args:
            topic: The topic to publish to (string).
            possible_values: A list or set of possible values.
        """
        if not isinstance(topic, str):
            raise TypeError("Topic must be a string")
        self.published_values[topic] = QuantumValue(possible_values)

    def observe(self, topic):
        """
        Observes the value for the given topic, collapsing the superposition
        and returning a single value.

        Args:
            topic: The topic to observe (string).

        Returns:
            The observed value.
        """
        if topic not in self.published_values:
            raise KeyError(f"Topic '{topic}' not published")
        return self.published_values[topic].observe()

    def get_superposition_hash(self, topic):
        """
        Returns the hash representing the superposition state for the given topic.

        Args:
            topic: The topic to get the hash for (string).

        Returns:
            The superposition hash.
        """
        if topic not in self.published_values:
            raise KeyError(f"Topic '{topic}' not published")
        return self.published_values[topic].get_superposition_hash()

    def __repr__(self):
        return f"QuantumPublisher(published_values={self.published_values})"


if __name__ == '__main__':
    # Example usage
    publisher = QuantumPublisher()

    # Publish a value to the "temperature" topic, with possible values 20, 21, and 22
    publisher.publish("temperature", [20, 21, 22])

    # Get the superposition hash for the "temperature" topic
    superposition_hash = publisher.get_superposition_hash("temperature")
    print(f"Superposition hash for temperature: {superposition_hash}")

    # Observe the value for the "temperature" topic
    observed_temperature = publisher.observe("temperature")
    print(f"Observed temperature: {observed_temperature}")

    # Observe the value again - it should be the same
    observed_temperature2 = publisher.observe("temperature")
    print(f"Observed temperature again: {observed_temperature2}")

    # Publish a string value
    publisher.publish("status", ["online", "offline", "busy"])
    print(f"Status superposition hash: {publisher.get_superposition_hash('status')}")
    print(f"Observed status: {publisher.observe('status')}")

    # Example with different data types
    publisher.publish("mixed_data", [1, "hello", 3.14, (1, 2)])
    print(f"Mixed data superposition hash: {publisher.get_superposition_hash('mixed_data')}")
    print(f"Observed mixed data: {publisher.observe('mixed_data')}")

    # Example with a set of possible values
    publisher.publish("set_data", {1, 2, 3})
    print(f"Set data superposition hash: {publisher.get_superposition_hash('set_data')}")
    print(f"Observed set data: {publisher.observe('set_data')}")