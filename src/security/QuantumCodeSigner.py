import random
import hashlib
from typing import Tuple

class QuantumCodeSigner:
    """
    A pseudocode implementation of a Quantum Code Signer.
    This class demonstrates the conceptual steps involved in using
    quantum entanglement (Bell pairs) for cryptographic code signing.

    Note: This is a simplified, illustrative example and does not
    represent a fully secure or practical quantum cryptographic system.
    It serves to demonstrate the core ideas.
    """

    def __init__(self):
        self.entangled_pairs = {}  # Store entangled qubit pairs (simulated)

    def generate_bell_pair(self) -> Tuple[int, int]:
        """
        Simulates the creation of an entangled Bell pair.
        In reality, this would involve quantum hardware.
        For simplicity, we use random numbers that are correlated.
        """
        state = random.choice([0, 1])
        return (state, state)  # Perfect correlation for demonstration

    def distribute_key(self, code_hash: str, signer_id: str) -> None:
        """
        Distributes a quantum key (simulated) based on the code hash.
        Each bit of the hash corresponds to a Bell pair.
        """
        self.entangled_pairs[signer_id] = []
        for bit in code_hash:
            pair = self.generate_bell_pair()
            self.entangled_pairs[signer_id].append(pair)

    def sign_code(self, code: bytes, signer_id: str) -> str:
        """
        Signs the code using the distributed quantum key.
        This involves "measuring" the qubits (simulated by reading the correlated values).
        The measurement results form the signature.
        """
        code_hash = hashlib.sha256(code).hexdigest()
        if signer_id not in self.entangled_pairs:
            raise ValueError("Signer ID not found. Key distribution required.")

        if len(code_hash) != len(self.entangled_pairs[signer_id]):
            raise ValueError("Code hash length does not match key length.")

        signature = ""
        for i, bit in enumerate(code_hash):
            # Simulate measurement by reading the entangled pair value
            qubit1, qubit2 = self.entangled_pairs[signer_id][i]
            signature += str(qubit1)  # Use the first qubit's value as the signature bit

        return signature

    def verify_signature(self, code: bytes, signature: str, signer_id: str) -> bool:
        """
        Verifies the signature against the code.
        This involves re-creating the expected signature based on the code
        and comparing it to the provided signature.
        """
        code_hash = hashlib.sha256(code).hexdigest()
        expected_signature = ""

        if signer_id not in self.entangled_pairs:
            raise ValueError("Signer ID not found. Key distribution required.")

        if len(code_hash) != len(self.entangled_pairs[signer_id]):
            raise ValueError("Code hash length does not match key length.")

        for i, bit in enumerate(code_hash):
            qubit1, qubit2 = self.entangled_pairs[signer_id][i]
            expected_signature += str(qubit1)

        return signature == expected_signature

if __name__ == '__main__':
    # Example Usage
    signer = QuantumCodeSigner()
    code = b"This is the code to be signed."
    signer_id = "Alice"

    # Distribute the quantum key
    code_hash = hashlib.sha256(code).hexdigest()
    signer.distribute_key(code_hash, signer_id)

    # Sign the code
    signature = signer.sign_code(code, signer_id)
    print(f"Signature: {signature}")

    # Verify the signature
    is_valid = signer.verify_signature(code, signature, signer_id)
    print(f"Signature is valid: {is_valid}")

    # Tamper with the code
    tampered_code = b"This is the code to be signed (tampered)."
    is_valid_tampered = signer.verify_signature(tampered_code, signature, signer_id)
    print(f"Signature is valid for tampered code: {is_valid_tampered}")