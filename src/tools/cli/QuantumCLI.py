import argparse
import random
import numpy as np

class QuantumCLI:
    """
    A command-line interface for exploring quantum concepts,
    including superposition and probabilistic morphing.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Quantum CLI: Explore superposition and probabilistic morphing."
        )
        self.subparsers = self.parser.add_subparsers(
            title="commands", dest="command", help="Available commands"
        )

        # Superposition command
        superposition_parser = self.subparsers.add_parser(
            "superposition", help="Simulate quantum superposition."
        )
        superposition_parser.add_argument(
            "state1", type=str, help="First quantum state (e.g., '0', 'up')"
        )
        superposition_parser.add_argument(
            "state2", type=str, help="Second quantum state (e.g., '1', 'down')"
        )
        superposition_parser.add_argument(
            "--amplitude1",
            type=float,
            default=0.707,
            help="Amplitude of the first state (default: 0.707)",
        )
        superposition_parser.add_argument(
            "--amplitude2",
            type=float,
            default=0.707,
            help="Amplitude of the second state (default: 0.707)",
        )

        # Probabilistic morphing command
        morph_parser = self.subparsers.add_parser(
            "morph", help="Simulate probabilistic morphing between states."
        )
        morph_parser.add_argument(
            "initial_state", type=str, help="The initial state."
        )
        morph_parser.add_argument(
            "final_state", type=str, help="The final state."
        )
        morph_parser.add_argument(
            "--probability",
            type=float,
            default=0.5,
            help="Probability of morphing to the final state (default: 0.5)",
        )
        morph_parser.add_argument(
            "--iterations",
            type=int,
            default=10,
            help="Number of morphing iterations (default: 10)",
        )

        # Entanglement command
        entanglement_parser = self.subparsers.add_parser(
            "entangle", help="Simulate quantum entanglement between two qubits."
        )
        entanglement_parser.add_argument(
            "qubit1_state", type=str, help="Initial state of the first qubit (0 or 1)"
        )
        entanglement_parser.add_argument(
            "qubit2_state", type=str, help="Initial state of the second qubit (0 or 1)"
        )

    def superposition(self, state1, state2, amplitude1, amplitude2):
        """Simulates quantum superposition."""
        if abs(amplitude1**2 + amplitude2**2 - 1) > 1e-6:
            print("Warning: Amplitudes do not normalize to 1. Results may be inaccurate.")

        print(f"Quantum Superposition:")
        print(f"State 1: |{state1}> with amplitude {amplitude1}")
        print(f"State 2: |{state2}> with amplitude {amplitude2}")
        print(f"Combined state: {amplitude1}|{state1}> + {amplitude2}|{state2}>")

        # Simulate measurement
        if random.random() < amplitude1**2:
            print(f"Measurement result: |{state1}>")
        else:
            print(f"Measurement result: |{state2}>")

    def morph(self, initial_state, final_state, probability, iterations):
        """Simulates probabilistic morphing between states."""
        current_state = initial_state
        print(f"Initial state: {current_state}")

        for i in range(iterations):
            if random.random() < probability:
                current_state = final_state
                print(f"Iteration {i+1}: Morphed to {current_state}")
            else:
                print(f"Iteration {i+1}: Remains at {current_state}")

        print(f"Final state: {current_state}")

    def entangle(self, qubit1_state, qubit2_state):
        """Simulates quantum entanglement between two qubits."""
        if qubit1_state not in ("0", "1") or qubit2_state not in ("0", "1"):
            print("Error: Qubit states must be either 0 or 1.")
            return

        print("Quantum Entanglement:")
        print(f"Qubit 1: |{qubit1_state}>")
        print(f"Qubit 2: |{qubit2_state}>")

        if qubit1_state == qubit2_state:
            print("Entangled state: (|00> + |11>)/sqrt(2)")
        else:
            print("Entangled state: (|01> + |10>)/sqrt(2)")

        # Simulate measurement of qubit 1
        measurement_result = random.choice([qubit1_state, qubit2_state])
        print(f"Measuring Qubit 1 yields: |{measurement_result}>")
        print(f"Qubit 2 instantaneously collapses to: |{measurement_result}>")

    def run(self):
        """Parses arguments and executes the corresponding command."""
        args = self.parser.parse_args()

        if args.command == "superposition":
            self.superposition(
                args.state1, args.state2, args.amplitude1, args.amplitude2
            )
        elif args.command == "morph":
            self.morph(args.initial_state, args.final_state, args.probability, args.iterations)
        elif args.command == "entangle":
            self.entangle(args.qubit1_state, args.qubit2_state)
        else:
            self.parser.print_help()


if __name__ == "__main__":
    cli = QuantumCLI()
    cli.run()