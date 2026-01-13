import unittest
from unittest.mock import patch, MagicMock
import random
import numpy as np

# Assuming the qubit allocation logic is in a file named 'qubit_allocation.py'
# and the environment model is in 'environment_model.py'
from src import qubit_allocation
from src import environment_model

class TestEnvironmentAwareQubitAllocation(unittest.TestCase):

    def setUp(self):
        """Setup for the tests.  Initialize a mock environment model."""
        self.mock_env_model = MagicMock(spec=environment_model.EnvironmentModel)
        self.allocator = qubit_allocation.EnvironmentAwareAllocator(self.mock_env_model)

    def test_allocate_qubits_no_noise(self):
        """Test qubit allocation when the environment is ideal (no noise)."""
        self.mock_env_model.get_noise_profile.return_value = {'T1': float('inf'), 'T2': float('inf')}
        num_qubits = 5
        allocated_qubits = self.allocator.allocate_qubits(num_qubits)
        self.assertEqual(len(allocated_qubits), num_qubits)
        # In an ideal environment, any qubits should be acceptable.
        self.assertTrue(all(isinstance(q, int) for q in allocated_qubits))

    def test_allocate_qubits_with_noise(self):
        """Test qubit allocation when the environment has noise."""
        # Simulate a noisy environment with short T1 and T2 times.
        self.mock_env_model.get_noise_profile.return_value = {'T1': 10e-6, 'T2': 5e-6}  # 10us and 5us
        num_qubits = 3
        allocated_qubits = self.allocator.allocate_qubits(num_qubits)
        self.assertEqual(len(allocated_qubits), num_qubits)
        self.assertTrue(all(isinstance(q, int) for q in allocated_qubits))

    def test_allocate_qubits_with_filtering(self):
        """Test qubit allocation with filtering based on noise thresholds."""
        # Simulate an environment where some qubits are better than others.
        qubit_noise_profiles = {
            0: {'T1': 10e-6, 'T2': 5e-6},
            1: {'T1': 20e-6, 'T2': 10e-6},
            2: {'T1': 5e-6, 'T2': 2.5e-6},
            3: {'T1': 30e-6, 'T2': 15e-6},
            4: {'T1': 1e-6, 'T2': 0.5e-6}
        }
        self.mock_env_model.get_noise_profile.side_effect = lambda qubit_id: qubit_noise_profiles[qubit_id]
        num_qubits = 3
        allocated_qubits = self.allocator.allocate_qubits(num_qubits, t1_threshold=15e-6, t2_threshold=7e-6)
        self.assertEqual(len(allocated_qubits), num_qubits)
        # Check that the allocated qubits meet the T1 and T2 thresholds.
        for qubit_id in allocated_qubits:
            self.assertTrue(qubit_noise_profiles[qubit_id]['T1'] >= 15e-6)
            self.assertTrue(qubit_noise_profiles[qubit_id]['T2'] >= 7e-6)

    def test_allocate_qubits_insufficient_qubits(self):
        """Test qubit allocation when not enough qubits meet the noise criteria."""
        # Simulate a very noisy environment where only one qubit is acceptable.
        qubit_noise_profiles = {
            0: {'T1': 10e-6, 'T2': 5e-6},
            1: {'T1': 20e-6, 'T2': 10e-6},
            2: {'T1': 5e-6, 'T2': 2.5e-6},
            3: {'T1': 30e-6, 'T2': 15e-6},
            4: {'T1': 1e-6, 'T2': 0.5e-6}
        }
        self.mock_env_model.get_noise_profile.side_effect = lambda qubit_id: qubit_noise_profiles[qubit_id]
        num_qubits = 3
        # Set high thresholds so that only one qubit (qubit 3) meets the criteria.
        with self.assertRaises(ValueError):
            self.allocator.allocate_qubits(num_qubits, t1_threshold=25e-6, t2_threshold=12e-6)

    def test_allocate_qubits_zero_qubits_requested(self):
        """Test qubit allocation when zero qubits are requested."""
        allocated_qubits = self.allocator.allocate_qubits(0)
        self.assertEqual(len(allocated_qubits), 0)

    def test_allocate_qubits_large_number_of_qubits(self):
        """Test allocating a large number of qubits."""
        self.mock_env_model.get_noise_profile.return_value = {'T1': float('inf'), 'T2': float('inf')}
        num_qubits = 100
        allocated_qubits = self.allocator.allocate_qubits(num_qubits)
        self.assertEqual(len(allocated_qubits), num_qubits)
        self.assertTrue(all(isinstance(q, int) for q in allocated_qubits))

    def test_allocate_qubits_random_noise_profiles(self):
        """Test with randomly generated noise profiles."""
        num_qubits = 5
        random_profiles = {}
        for i in range(num_qubits):
            random_profiles[i] = {'T1': random.uniform(1e-6, 50e-6), 'T2': random.uniform(1e-6, 50e-6)}

        self.mock_env_model.get_noise_profile.side_effect = lambda qubit_id: random_profiles[qubit_id]
        allocated_qubits = self.allocator.allocate_qubits(num_qubits, t1_threshold=10e-6, t2_threshold=5e-6)
        self.assertEqual(len(allocated_qubits), num_qubits)
        for qubit_id in allocated_qubits:
            self.assertTrue(random_profiles[qubit_id]['T1'] >= 10e-6)
            self.assertTrue(random_profiles[qubit_id]['T2'] >= 5e-6)

    def test_allocate_qubits_all_qubits_bad(self):
        """Test when all qubits are below the threshold."""
        num_qubits = 5
        bad_profiles = {}
        for i in range(num_qubits):
            bad_profiles[i] = {'T1': random.uniform(1e-7, 5e-7), 'T2': random.uniform(1e-7, 5e-7)}

        self.mock_env_model.get_noise_profile.side_effect = lambda qubit_id: bad_profiles[qubit_id]
        with self.assertRaises(ValueError):
            self.allocator.allocate_qubits(num_qubits, t1_threshold=10e-6, t2_threshold=5e-6)

if __name__ == '__main__':
    unittest.main()