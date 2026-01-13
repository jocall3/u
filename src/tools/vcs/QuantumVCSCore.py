import hashlib
import os
import random
import time
import uuid

class QuantumState:
    """
    Represents a snapshot of the codebase at a specific point in spacetime.
    """

    def __init__(self, data, timestamp=None, parent_hash=None, metadata=None):
        self.data = data  # Content of the files in the codebase (dictionary: filename -> content)
        self.timestamp = timestamp or time.time()  # Time of the snapshot
        self.parent_hash = parent_hash  # Hash of the previous state (if any)
        self.metadata = metadata or {}  # Additional information about the state (e.g., commit message)
        self.hash = self._calculate_hash()  # Unique identifier for the state

    def _calculate_hash(self):
        """
        Calculates the SHA-256 hash of the state based on its data, timestamp, parent hash, and metadata.
        """
        data_str = str(self.data).encode('utf-8')
        timestamp_str = str(self.timestamp).encode('utf-8')
        parent_hash_str = str(self.parent_hash).encode('utf-8') if self.parent_hash else b''
        metadata_str = str(self.metadata).encode('utf-8')

        combined_data = data_str + timestamp_str + parent_hash_str + metadata_str
        return hashlib.sha256(combined_data).hexdigest()

    def __repr__(self):
        return f"QuantumState(hash={self.hash[:8]}, timestamp={self.timestamp})"


class QuantumVCSCore:
    """
    Core class for managing code states, checkouts, and merges using quantum-inspired principles.
    """

    def __init__(self, repository_path):
        self.repository_path = repository_path
        self.current_state = None  # The current state of the codebase
        self.history = {}  # Dictionary to store all states (hash -> QuantumState)
        self._initialize_repository()

    def _initialize_repository(self):
        """
        Initializes the repository directory if it doesn't exist.
        """
        if not os.path.exists(self.repository_path):
            os.makedirs(self.repository_path)
            print(f"Repository initialized at: {self.repository_path}")

    def create_state(self, data, metadata=None):
        """
        Creates a new QuantumState based on the provided data and metadata.
        """
        parent_hash = self.current_state.hash if self.current_state else None
        new_state = QuantumState(data, parent_hash=parent_hash, metadata=metadata)
        self.history[new_state.hash] = new_state
        self.current_state = new_state
        return new_state

    def get_current_state(self):
        """
        Returns the current QuantumState.
        """
        return self.current_state

    def checkout(self, state_hash):
        """
        Checks out a specific QuantumState based on its hash.
        """
        if state_hash in self.history:
            self.current_state = self.history[state_hash]
            print(f"Checked out state: {state_hash[:8]}")
        else:
            print(f"State not found: {state_hash}")

    def merge(self, state_hash):
        """
        Merges a specific QuantumState into the current state.  A very basic merge.
        """
        if state_hash not in self.history:
            print(f"State not found: {state_hash}")
            return None

        merge_state = self.history[state_hash]
        if self.current_state is None:
            self.current_state = merge_state
            self.history[merge_state.hash] = merge_state
            return merge_state

        # Very basic merge:  If a file exists in both, the merge_state wins.
        merged_data = self.current_state.data.copy()
        merged_data.update(merge_state.data)

        metadata = {
            "merge_base": self.current_state.hash,
            "merge_target": state_hash
        }

        new_state = self.create_state(merged_data, metadata=metadata)
        print(f"Merged state {state_hash[:8]} into current state. New state: {new_state.hash[:8]}")
        return new_state

    def get_history(self):
        """
        Returns the entire history of QuantumStates.
        """
        return self.history

    def save_state_to_disk(self, state_hash, directory=None):
        """
        Saves a specific QuantumState to disk.
        """
        if state_hash not in self.history:
            print(f"State not found: {state_hash}")
            return

        state = self.history[state_hash]
        target_directory = directory or os.path.join(self.repository_path, "states", state_hash[:8])
        os.makedirs(target_directory, exist_ok=True)

        for filename, content in state.data.items():
            filepath = os.path.join(target_directory, filename)
            with open(filepath, "w") as f:
                f.write(content)
        print(f"State {state_hash[:8]} saved to {target_directory}")

    def load_state_from_disk(self, state_hash, directory=None):
        """
        Loads a QuantumState from disk and sets it as the current state.
        """
        target_directory = directory or os.path.join(self.repository_path, "states", state_hash[:8])

        if not os.path.exists(target_directory):
            print(f"Directory not found: {target_directory}")
            return

        data = {}
        for filename in os.listdir(target_directory):
            filepath = os.path.join(target_directory, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    data[filename] = f.read()

        # Create a dummy state object.  The timestamp and parent_hash will be lost.
        new_state = QuantumState(data)
        new_state.hash = state_hash # Override the hash with the one from the directory name.
        self.history[new_state.hash] = new_state
        self.current_state = new_state

        print(f"State {state_hash[:8]} loaded from {target_directory}")

    def create_branch(self, branch_name, state_hash=None):
        """
        Creates a new branch at a specific state.
        """
        if state_hash is None:
            if self.current_state is None:
                print("No current state to branch from.")
                return None
            state_hash = self.current_state.hash

        if state_hash not in self.history:
            print(f"State not found: {state_hash}")
            return None

        branch_path = os.path.join(self.repository_path, "branches", branch_name)
        if os.path.exists(branch_path):
            print(f"Branch already exists: {branch_name}")
            return None

        # Create a symbolic link to the state's directory.
        state_directory = os.path.join(self.repository_path, "states", state_hash[:8])
        os.makedirs(os.path.dirname(branch_path), exist_ok=True)
        os.symlink(os.path.abspath(state_directory), branch_path)

        print(f"Branch '{branch_name}' created at state {state_hash[:8]}")
        return branch_name

    def switch_branch(self, branch_name):
        """
        Switches to a specific branch.
        """
        branch_path = os.path.join(self.repository_path, "branches", branch_name)
        if not os.path.exists(branch_path):
            print(f"Branch not found: {branch_name}")
            return

        # Resolve the symbolic link to get the state directory.
        state_directory = os.readlink(branch_path)
        state_hash = os.path.basename(state_directory) # Get the last part of the path (the hash)

        self.load_state_from_disk(state_hash)
        print(f"Switched to branch '{branch_name}' (state {state_hash[:8]})")

    def list_branches(self):
        """
        Lists all existing branches.
        """
        branches_path = os.path.join(self.repository_path, "branches")
        if not os.path.exists(branches_path):
            return []

        branches = [f for f in os.listdir(branches_path) if os.path.islink(os.path.join(branches_path, f))]
        return branches

if __name__ == '__main__':
    # Example Usage
    repo_path = "test_repo"
    vcs = QuantumVCSCore(repo_path)

    # Initial state
    data1 = {"file1.txt": "This is the first version of file1.", "file2.txt": "Initial content of file2."}
    state1 = vcs.create_state(data1, metadata={"commit_message": "Initial commit"})
    print(f"State 1: {state1}")

    # Second state
    data2 = {"file1.txt": "This is the second version of file1.", "file3.txt": "New file added."}
    state2 = vcs.create_state(data2, metadata={"commit_message": "Added file3 and updated file1"})
    print(f"State 2: {state2}")

    # Checkout the first state
    vcs.checkout(state1.hash)
    print(f"Current state after checkout: {vcs.get_current_state()}")

    # Merge the second state into the first
    vcs.merge(state2.hash)
    print(f"Current state after merge: {vcs.get_current_state()}")

    # Save the current state to disk
    vcs.save_state_to_disk(vcs.get_current_state().hash)

    # Create a branch
    vcs.create_branch("feature_branch", state1.hash)

    # List branches
    print(f"Branches: {vcs.list_branches()}")

    # Switch to the branch
    vcs.switch_branch("feature_branch")

    # Load a state from disk
    loaded_state_hash = vcs.get_current_state().hash
    vcs.load_state_from_disk(loaded_state_hash)