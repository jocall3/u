import json
import os
import random
import hashlib
from typing import Dict, List, Any, Tuple

class LogStateReader:
    """
    A class to read, analyze, and potentially alter log states.
    This class focuses on performing measurements on log data and
    introducing controlled randomness to simulate quantum-like behavior
    in the log analysis process.
    """

    def __init__(self, log_directory: str):
        """
        Initializes the LogStateReader with the directory containing log files.

        Args:
            log_directory (str): The path to the directory containing log files.
        """
        self.log_directory = log_directory
        self.log_files = self._discover_log_files()
        self.quantum_constant = random.uniform(1e-34, 6.626e-34)  # Planck's constant range

    def _discover_log_files(self) -> List[str]:
        """
        Discovers all log files within the specified log directory.

        Returns:
            List[str]: A list of paths to the log files.
        """
        log_files = []
        try:
            for filename in os.listdir(self.log_directory):
                if filename.endswith(".log") or filename.endswith(".json"):  # Support .log and .json
                    log_files.append(os.path.join(self.log_directory, filename))
        except FileNotFoundError:
            print(f"Error: Log directory not found: {self.log_directory}")
            return []
        except Exception as e:
            print(f"Error discovering log files: {e}")
            return []
        return log_files

    def read_log_file(self, log_file_path: str) -> List[Dict[str, Any]]:
        """
        Reads a log file and parses its contents into a list of dictionaries.
        Supports both .log (line-by-line) and .json (JSON array) formats.

        Args:
            log_file_path (str): The path to the log file.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing log entries.
        """
        log_entries = []
        try:
            if log_file_path.endswith(".json"):
                with open(log_file_path, 'r') as f:
                    log_entries = json.load(f)
            else:  # Assume .log format
                with open(log_file_path, 'r') as f:
                    for line in f:
                        try:
                            # Attempt to parse as JSON, if it fails, treat as a simple string
                            log_entry = json.loads(line.strip())
                            log_entries.append(log_entry)
                        except json.JSONDecodeError:
                            log_entries.append({"message": line.strip()})  # Simple string entry
        except FileNotFoundError:
            print(f"Error: Log file not found: {log_file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {log_file_path}: {e}")
        except Exception as e:
            print(f"Error reading log file {log_file_path}: {e}")
        return log_entries

    def measure_log_state(self, log_entries: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Performs measurements on the log entries to extract statistical information.
        Introduces randomness to simulate quantum-like measurement uncertainty.

        Args:
            log_entries (List[Dict[str, Any]]): A list of log entry dictionaries.

        Returns:
            Dict[str, float]: A dictionary containing statistical measurements.
        """
        if not log_entries:
            return {}

        num_entries = len(log_entries)
        error_count = 0
        warning_count = 0
        info_count = 0
        message_lengths = []

        for entry in log_entries:
            message = entry.get("message", "").lower()  # Handle missing 'message' key
            if "error" in message:
                error_count += 1
            elif "warning" in message:
                warning_count += 1
            elif "info" in message:
                info_count += 1
            message_lengths.append(len(message))

        # Introduce "quantum" uncertainty
        error_count += int(random.gauss(0, self.quantum_constant * num_entries))
        warning_count += int(random.gauss(0, self.quantum_constant * num_entries))
        info_count += int(random.gauss(0, self.quantum_constant * num_entries))

        avg_message_length = sum(message_lengths) / num_entries if num_entries > 0 else 0
        avg_message_length += random.uniform(-self.quantum_constant, self.quantum_constant) #Quantum fluctuation

        return {
            "total_entries": float(num_entries),
            "error_count": float(max(0, error_count)),  # Ensure non-negative
            "warning_count": float(max(0, warning_count)), # Ensure non-negative
            "info_count": float(max(0, info_count)), # Ensure non-negative
            "average_message_length": float(avg_message_length)
        }

    def alter_past_event(self, log_entries: List[Dict[str, Any]], index: int, new_message: str) -> List[Dict[str, Any]]:
        """
        Alters a specific log entry in the past.  This simulates the observer effect.
        Uses a cryptographic hash to ensure some level of immutability tracking.

        Args:
            log_entries (List[Dict[str, Any]]): The list of log entries.
            index (int): The index of the log entry to alter.
            new_message (str): The new message to replace the old one.

        Returns:
            List[Dict[str, Any]]: The modified list of log entries.
        """
        if 0 <= index < len(log_entries):
            original_entry = log_entries[index]
            original_message = original_entry.get("message", "")
            original_hash = hashlib.sha256(original_message.encode()).hexdigest()

            log_entries[index]["message"] = new_message
            log_entries[index]["original_message_hash"] = original_hash
            log_entries[index]["altered"] = True #Flag that it has been altered

        return log_entries

    def analyze_log_states(self) -> List[Tuple[str, Dict[str, float]]]:
        """
        Analyzes all log files in the directory and returns a list of measurements.

        Returns:
            List[Tuple[str, Dict[str, float]]]: A list of tuples, where each tuple contains
            the log file path and the corresponding log state measurements.
        """
        results = []
        for log_file in self.log_files:
            log_entries = self.read_log_file(log_file)
            measurements = self.measure_log_state(log_entries)
            results.append((log_file, measurements))
        return results

    def get_log_files(self) -> List[str]:
        """
        Returns the list of log files being analyzed.

        Returns:
            List[str]: The list of log file paths.
        """
        return self.log_files

if __name__ == '__main__':
    # Example usage:
    log_dir = "logs"  # Replace with your log directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a dummy log file
    with open(os.path.join(log_dir, "example.log"), "w") as f:
        f.write('{"timestamp": "2023-10-27 10:00:00", "message": "Info: System started"}\n')
        f.write('{"timestamp": "2023-10-27 10:00:05", "message": "Warning: Low disk space"}\n')
        f.write('{"timestamp": "2023-10-27 10:00:10", "message": "Error: Connection timeout"}\n')

    reader = LogStateReader(log_dir)
    analysis_results = reader.analyze_log_states()

    for log_file, measurements in analysis_results:
        print(f"Log File: {log_file}")
        print(f"Measurements: {measurements}")

    # Example of altering a past event
    log_entries = reader.read_log_file(os.path.join(log_dir, "example.log"))
    altered_entries = reader.alter_past_event(log_entries, 0, "Info: System initialized successfully")

    print("\nAltered Log Entries:")
    print(json.dumps(altered_entries, indent=2))