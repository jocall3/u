import random
import secrets
import hashlib
from typing import Tuple, Dict, Callable

class QuantumKeyManager:
    """
    Manages the generation, distribution, and verification of quantum keys.
    This is a simplified, conceptual model and does not implement actual quantum mechanics.
    """

    def __init__(self, key_length: int = 256, error_rate_threshold: float = 0.05):
        """
        Initializes the QuantumKeyManager.

        Args:
            key_length: The desired length of the quantum key in bits.
            error_rate_threshold: The maximum acceptable error rate during key sifting.
        """
        self.key_length = key_length
        self.error_rate_threshold = error_rate_threshold
        self.quantum_channel = QuantumChannel()  # Simulate a quantum channel

    def generate_quantum_key(self) -> Tuple[str, str, Dict[int, str], Dict[int, str]]:
        """
        Generates a raw quantum key using a simulated quantum process.

        Returns:
            A tuple containing:
            - Alice's raw key (string of bits).
            - Bob's raw key (string of bits).
            - Alice's bases (dictionary mapping bit index to basis).
            - Bob's bases (dictionary mapping bit index to basis).
        """
        alice_key = ''.join(secrets.choice(['0', '1']) for _ in range(self.key_length))
        alice_bases = {i: secrets.choice(['+', 'x']) for i in range(self.key_length)}  # '+' for rectilinear, 'x' for diagonal

        bob_bases = {i: secrets.choice(['+', 'x']) for i in range(self.key_length)}
        bob_key = self.quantum_channel.transmit(alice_key, alice_bases, bob_bases)

        return alice_key, bob_key, alice_bases, bob_bases

    def sift_key(self, alice_key: str, bob_key: str, alice_bases: Dict[int, str], bob_bases: Dict[int, str]) -> Tuple[str, str]:
        """
        Sifts the raw keys to create a shared secret key.

        Args:
            alice_key: Alice's raw key.
            bob_key: Bob's raw key.
            alice_bases: Alice's bases.
            bob_bases: Bob's bases.

        Returns:
            A tuple containing Alice's sifted key and Bob's sifted key.
        """
        alice_sifted_key = ""
        bob_sifted_key = ""
        for i in range(len(alice_key)):
            if alice_bases[i] == bob_bases[i]:
                alice_sifted_key += alice_key[i]
                bob_sifted_key += bob_key[i]

        return alice_sifted_key, bob_sifted_key

    def estimate_error_rate(self, alice_key: str, bob_key: str, sample_size: int = 100) -> float:
        """
        Estimates the error rate between Alice's and Bob's keys by comparing a random sample.

        Args:
            alice_key: Alice's key.
            bob_key: Bob's key.
            sample_size: The number of bits to compare.

        Returns:
            The estimated error rate.
        """
        if len(alice_key) != len(bob_key):
            raise ValueError("Keys must be of equal length for error rate estimation.")

        if len(alice_key) < sample_size:
            sample_size = len(alice_key)

        indices = random.sample(range(len(alice_key)), sample_size)
        errors = 0
        for i in indices:
            if alice_key[i] != bob_key[i]:
                errors += 1

        return errors / sample_size

    def key_reconciliation(self, alice_key: str, bob_key: str) -> Tuple[str, str]:
        """
        Performs key reconciliation to correct errors in the sifted keys.
        This is a placeholder; a real implementation would use error correction codes.

        Args:
            alice_key: Alice's sifted key.
            bob_key: Bob's sifted key.

        Returns:
            A tuple containing Alice's reconciled key and Bob's reconciled key.
        """
        # In a real implementation, this would involve error correction.
        # For simplicity, we just truncate the keys to the shorter length.
        min_length = min(len(alice_key), len(bob_key))
        return alice_key[:min_length], bob_key[:min_length]

    def privacy_amplification(self, key: str, new_length: int) -> str:
        """
        Reduces the information an eavesdropper might have gained about the key.
        This uses a cryptographic hash function to generate a shorter, more secure key.

        Args:
            key: The key to amplify.
            new_length: The desired length of the amplified key.

        Returns:
            The amplified key.
        """
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        # Take the first 'new_length' bits of the hash.  This is a simplification.
        binary_hash = bin(int(hashed_key, 16))[2:].zfill(256) # Ensure it's 256 bits
        return binary_hash[:new_length]

    def run_bb84(self) -> str:
        """
        Executes the BB84 quantum key distribution protocol.

        Returns:
            The final shared secret key.  Returns None if key generation fails.
        """
        alice_key, bob_key, alice_bases, bob_bases = self.generate_quantum_key()
        alice_sifted_key, bob_sifted_key = self.sift_key(alice_key, bob_key, alice_bases, bob_bases)

        error_rate = self.estimate_error_rate(alice_sifted_key, bob_sifted_key)
        if error_rate > self.error_rate_threshold:
            print(f"Error rate too high: {error_rate}. Key generation failed.")
            return None

        alice_reconciled_key, bob_reconciled_key = self.key_reconciliation(alice_sifted_key, bob_sifted_key)
        final_key_length = int(len(alice_reconciled_key) * 0.5)  # Reduce key length for privacy amplification
        final_key = self.privacy_amplification(alice_reconciled_key, final_key_length)

        return final_key


class QuantumChannel:
    """
    Simulates a quantum channel for key transmission.
    This is a simplified model and does not implement actual quantum mechanics.
    It introduces a small probability of error during transmission.
    """

    def __init__(self, error_probability: float = 0.01):
        """
        Initializes the QuantumChannel.

        Args:
            error_probability: The probability of a bit flip during transmission.
        """
        self.error_probability = error_probability

    def transmit(self, alice_key: str, alice_bases: Dict[int, str], bob_bases: Dict[int, str]) -> str:
        """
        Simulates the transmission of a quantum key through the channel.

        Args:
            alice_key: Alice's key.
            alice_bases: Alice's bases.
            bob_bases: Bob's bases.

        Returns:
            Bob's received key.
        """
        bob_key = ""
        for i in range(len(alice_key)):
            bit = alice_key[i]
            if random.random() < self.error_probability:
                bit = '1' if bit == '0' else '0'  # Simulate a bit flip
            bob_key += bit
        return bob_key

if __name__ == '__main__':
    key_manager = QuantumKeyManager()
    shared_key = key_manager.run_bb84()

    if shared_key:
        print(f"Shared secret key: {shared_key}")
    else:
        print("Key generation failed.")