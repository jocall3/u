import random
import hashlib

class GlobalStateEntanglementReader:
    """
    A class to simulate reading and interpreting the entangled state of global code variables.
    This is a highly conceptual and abstract representation, not a literal implementation.
    """

    def __init__(self, global_state, seed=None):
        """
        Initializes the GlobalStateEntanglementReader.

        Args:
            global_state (dict): A dictionary representing the global state of the program.
                                  Keys are variable names (strings), and values are their current values.
            seed (int, optional): A seed for the random number generator, allowing for reproducible results.
                                   If None, the system time is used as the seed.
        """
        self.global_state = global_state
        if seed is None:
            self.seed = random.randint(0, 2**32 - 1)  # Generate a random seed if none is provided
        else:
            self.seed = seed
        random.seed(self.seed)  # Initialize the random number generator

    def read_entangled_state(self, variable_names=None, entanglement_factor=0.1):
        """
        Reads and interprets the "entangled" state of the specified global variables.

        This method simulates entanglement by introducing randomness and dependencies
        between the variables. The degree of entanglement is controlled by the
        `entanglement_factor`.

        Args:
            variable_names (list, optional): A list of variable names to consider.
                                             If None, all variables in the global state are used.
            entanglement_factor (float): A value between 0 and 1 representing the degree of entanglement.
                                         Higher values introduce more randomness and dependencies.

        Returns:
            dict: A dictionary representing the interpreted state of the variables.
                  The values in this dictionary may be modified based on the entanglement simulation.
        """

        if variable_names is None:
            variable_names = list(self.global_state.keys())

        interpreted_state = self.global_state.copy()  # Start with a copy of the global state

        for var_name in variable_names:
            if var_name not in interpreted_state:
                continue  # Skip variables not found in the global state

            original_value = interpreted_state[var_name]

            # Introduce randomness based on the entanglement factor
            random_noise = random.uniform(-entanglement_factor, entanglement_factor)

            # Apply a transformation based on the variable's type
            if isinstance(original_value, (int, float)):
                interpreted_value = original_value * (1 + random_noise)
            elif isinstance(original_value, str):
                # Modify the string based on a hash of its original value and the random noise
                hash_object = hashlib.sha256((original_value + str(random_noise)).encode())
                hex_dig = hash_object.hexdigest()
                interpreted_value = hex_dig[:len(original_value)]  # Truncate to original length
            elif isinstance(original_value, list):
                # Shuffle the list with a probability based on the entanglement factor
                if random.random() < entanglement_factor:
                    random.shuffle(interpreted_value)
                interpreted_value = interpreted_value[:] # create a copy to avoid modifying the original
            elif isinstance(original_value, dict):
                # Add or remove a key-value pair with a probability based on the entanglement factor
                if random.random() < entanglement_factor:
                    if len(original_value) > 0:
                        key_to_remove = random.choice(list(original_value.keys()))
                        del original_value[key_to_remove]
                    else:
                        original_value["random_key"] = random.random()
                interpreted_value = original_value.copy() # create a copy to avoid modifying the original
            else:
                # For other types, simply add the random noise to the string representation
                interpreted_value = str(original_value) + str(random_noise)

            interpreted_state[var_name] = interpreted_value

        return interpreted_state

    def get_seed(self):
        """
        Returns the seed used for the random number generator.

        Returns:
            int: The seed value.
        """
        return self.seed

if __name__ == '__main__':
    # Example usage
    global_state = {
        "x": 10,
        "y": 20.5,
        "message": "Hello, world!",
        "data": [1, 2, 3, 4, 5],
        "config": {"param1": "value1", "param2": 123}
    }

    reader = GlobalStateEntanglementReader(global_state, seed=42)
    entangled_state = reader.read_entangled_state(entanglement_factor=0.3)

    print("Original Global State:", global_state)
    print("Entangled State:", entangled_state)
    print("Seed:", reader.get_seed())

    # Demonstrate reproducibility with the same seed
    reader2 = GlobalStateEntanglementReader(global_state, seed=42)
    entangled_state2 = reader2.read_entangled_state(entanglement_factor=0.3)
    print("Entangled State (reproduced):", entangled_state2)

    # Demonstrate different results with a different seed
    reader3 = GlobalStateEntanglementReader(global_state, seed=123)
    entangled_state3 = reader3.read_entangled_state(entanglement_factor=0.3)
    print("Entangled State (different seed):", entangled_state3)