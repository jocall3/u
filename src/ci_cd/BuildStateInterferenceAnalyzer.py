import hashlib
import os
import random
import time
from typing import Dict, List, Optional, Tuple

class BuildStateInterferenceAnalyzer:
    """
    Analyzes build states to detect destructive interference, identifying
    conditions where concurrent or sequential builds negatively impact each other.
    """

    def __init__(self, build_log_directory: str, state_persistence_directory: str):
        """
        Initializes the analyzer with directories for build logs and state persistence.

        Args:
            build_log_directory: Path to the directory containing build logs.
            state_persistence_directory: Path to the directory for persisting build states.
        """
        self.build_log_directory = build_log_directory
        self.state_persistence_directory = state_persistence_directory
        self.build_states: Dict[str, Dict] = {}  # Build ID -> State
        self.interference_patterns: List[Dict] = []

    def load_build_logs(self) -> None:
        """
        Loads build logs from the specified directory and parses them to extract build states.
        """
        for filename in os.listdir(self.build_log_directory):
            if filename.endswith(".log"):
                filepath = os.path.join(self.build_log_directory, filename)
                try:
                    with open(filepath, "r") as f:
                        log_content = f.read()
                        build_id = self._extract_build_id(filename)
                        build_state = self._parse_build_log(log_content)
                        if build_id and build_state:
                            self.build_states[build_id] = build_state
                except Exception as e:
                    print(f"Error processing log file {filename}: {e}")

    def _extract_build_id(self, filename: str) -> Optional[str]:
        """
        Extracts the build ID from the filename.  Assumes a simple naming convention.

        Args:
            filename: The name of the log file.

        Returns:
            The build ID, or None if it cannot be extracted.
        """
        try:
            return filename.split(".")[0]  # e.g., "build_123.log" -> "build_123"
        except:
            return None

    def _parse_build_log(self, log_content: str) -> Dict:
        """
        Parses the build log content to extract relevant build state information.
        This is a placeholder; a real implementation would involve more sophisticated parsing.

        Args:
            log_content: The content of the build log.

        Returns:
            A dictionary representing the build state.
        """
        # Simulate parsing - extract some random data
        state = {}
        lines = log_content.splitlines()
        state["start_time"] = self._extract_timestamp(lines, "start")
        state["end_time"] = self._extract_timestamp(lines, "end")
        state["success"] = random.random() > 0.1  # Simulate success/failure
        state["warnings"] = random.randint(0, 10)
        state["errors"] = random.randint(0, 3)
        state["dependencies"] = self._extract_dependencies(lines)
        return state

    def _extract_timestamp(self, lines: List[str], type: str) -> Optional[float]:
        """Simulates extracting a timestamp from the log lines."""
        for line in lines:
            if type == "start" and "Build started" in line:
                return time.time() - random.randint(10, 100)
            elif type == "end" and "Build finished" in line:
                return time.time()
        return None

    def _extract_dependencies(self, lines: List[str]) -> List[str]:
        """Simulates extracting dependencies from the log lines."""
        dependencies = []
        for line in lines:
            if "Dependency" in line:
                dependencies.append(hashlib.md5(line.encode()).hexdigest()[:8]) # Simulate dependency name
        return dependencies

    def analyze_interference(self) -> None:
        """
        Analyzes the loaded build states to detect potential interference patterns.
        """
        build_ids = list(self.build_states.keys())
        for i in range(len(build_ids)):
            for j in range(i + 1, len(build_ids)):
                build_id1 = build_ids[i]
                build_id2 = build_ids[j]
                state1 = self.build_states[build_id1]
                state2 = self.build_states[build_id2]

                if self._detect_destructive_interference(state1, state2):
                    self.interference_patterns.append({
                        "build_id1": build_id1,
                        "build_id2": build_id2,
                        "reason": "Potential destructive interference detected."
                    })

    def _detect_destructive_interference(self, state1: Dict, state2: Dict) -> bool:
        """
        Detects destructive interference between two build states.
        This is a placeholder; a real implementation would involve more sophisticated analysis.

        Args:
            state1: The build state of the first build.
            state2: The build state of the second build.

        Returns:
            True if destructive interference is detected, False otherwise.
        """
        # Simulate interference detection based on time overlap and dependency conflicts
        if not state1["start_time"] or not state1["end_time"] or not state2["start_time"] or not state2["end_time"]:
            return False

        overlap = (state1["start_time"] < state2["end_time"]) and (state2["start_time"] < state1["end_time"])
        dependency_conflict = any(dep in state2["dependencies"] for dep in state1["dependencies"])

        return overlap and dependency_conflict and (state1["errors"] > 0 or state2["errors"] > 0)

    def persist_interference_patterns(self) -> None:
        """
        Persists the detected interference patterns to a file in the state persistence directory.
        """
        filepath = os.path.join(self.state_persistence_directory, "interference_patterns.txt")
        try:
            with open(filepath, "w") as f:
                for pattern in self.interference_patterns:
                    f.write(str(pattern) + "\n")
        except Exception as e:
            print(f"Error persisting interference patterns: {e}")

    def run_analysis(self) -> None:
        """
        Runs the complete analysis pipeline: loading logs, analyzing interference, and persisting results.
        """
        self.load_build_logs()
        self.analyze_interference()
        self.persist_interference_patterns()

if __name__ == '__main__':
    # Example Usage (requires dummy log files)
    build_log_dir = "build_logs"  # Create this directory and add dummy .log files
    state_dir = "build_states"  # Create this directory

    # Create dummy directories if they don't exist
    if not os.path.exists(build_log_dir):
        os.makedirs(build_log_dir)
        # Create some dummy log files
        for i in range(3):
            with open(os.path.join(build_log_dir, f"build_{i}.log"), "w") as f:
                f.write(f"Build started at {time.time()}\n")
                f.write(f"Dependency: lib{i}.so\n")
                f.write(f"Build finished at {time.time() + random.randint(1,5)}\n")

    if not os.path.exists(state_dir):
        os.makedirs(state_dir)

    analyzer = BuildStateInterferenceAnalyzer(build_log_dir, state_dir)
    analyzer.run_analysis()
    print("Analysis complete. Interference patterns (if any) saved to build_states/interference_patterns.txt")