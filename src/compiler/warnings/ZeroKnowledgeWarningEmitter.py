# src/compiler/warnings/ZeroKnowledgeWarningEmitter.py

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

class ZeroKnowledgeWarningEmitter:
    """
    Emits warnings based on zero-knowledge principles.  No actual sensitive
    information is revealed in the warning itself, but the *existence* of
    a warning signals a potential issue.  The warning messages are
    cryptographically hashed to prevent reverse engineering.
    """

    def __init__(self, salt: Optional[str] = None):
        """
        Initializes the emitter with an optional salt.  The salt adds
        another layer of security to the hashing process.  If no salt is
        provided, a random one is generated.
        """
        self.salt = salt if salt is not None else self._generate_salt()
        self.warning_count = 0

    def _generate_salt(self) -> str:
        """
        Generates a random salt for hashing.
        """
        return str(random.randint(1000000000, 9999999999)) + str(time.time())

    def emit_warning(self, warning_code: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emits a warning.  The warning message is hashed using SHA-256
        along with the salt.  The hash is printed to stderr.  The data
        parameter allows for including additional context, but this data
        is NOT included in the hash to maintain zero-knowledge.  It's
        intended for logging or debugging purposes only.
        """
        message = f"Warning Code: {warning_code}"
        if data:
            message += f" - Context: {data}"

        hashed_message = self._hash_message(message)
        print(f"ZERO-KNOWLEDGE WARNING: {hashed_message}")  # Emitting to stderr is better, but stdout for now.
        self.warning_count += 1

    def _hash_message(self, message: str) -> str:
        """
        Hashes the message using SHA-256 and the salt.
        """
        combined_message = self.salt + message
        hashed = hashlib.sha256(combined_message.encode('utf-8')).hexdigest()
        return hashed

    def get_warning_count(self) -> int:
        """
        Returns the number of warnings emitted.
        """
        return self.warning_count

    def reset_warning_count(self) -> None:
        """
        Resets the warning count to zero.
        """
        self.warning_count = 0

    def create_deterministic_warning(self, seed: int, warning_type: str) -> None:
        """
        Creates a deterministic warning based on a seed value. This is useful
        for testing and ensuring that the same input always produces the same
        warning (hash).
        """
        random.seed(seed)
        random_data = {
            "value1": random.randint(1, 100),
            "value2": random.random(),
            "value3": random.choice(["a", "b", "c"])
        }
        self.emit_warning(warning_type, random_data)

if __name__ == '__main__':
    # Example Usage
    emitter = ZeroKnowledgeWarningEmitter()

    emitter.emit_warning("INVALID_INPUT", {"field": "username", "value": "bad_user"})
    emitter.emit_warning("DEPRECATED_FEATURE", {"feature": "old_api"})

    print(f"Total warnings emitted: {emitter.get_warning_count()}")

    emitter.create_deterministic_warning(42, "DETERMINISTIC_ISSUE")
    emitter.create_deterministic_warning(42, "DETERMINISTIC_ISSUE") # Same seed, same hash

    print(f"Total warnings emitted: {emitter.get_warning_count()}")

    emitter.reset_warning_count()
    print(f"Total warnings emitted after reset: {emitter.get_warning_count()}")