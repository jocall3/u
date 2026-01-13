import unittest
import numpy as np
from src.optimization.pso import ParticleSwarmOptimizer

class PSOCodeSearchingTests(unittest.TestCase):

    def setUp(self):
        """Setup for tests."""
        self.optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )

    def test_initialization(self):
        """Test particle initialization."""
        self.assertEqual(len(self.optimizer.particles), 20)
        self.assertEqual(self.optimizer.particles[0].position.shape, (2,))
        self.assertEqual(self.optimizer.particles[0].velocity.shape, (2,))

    def test_fitness_evaluation(self):
        """Test fitness evaluation with a simple function."""
        def sphere_function(x):
            return np.sum(x**2)

        self.optimizer.set_fitness_function(sphere_function)
        self.optimizer.initialize_particles()
        for particle in self.optimizer.particles:
            particle.fitness = sphere_function(particle.position)
        self.assertIsNotNone(self.optimizer.particles[0].fitness)

    def test_update_velocity(self):
        """Test velocity update mechanism."""
        self.optimizer.initialize_particles()
        initial_velocity = self.optimizer.particles[0].velocity.copy()
        self.optimizer.update_velocity(self.optimizer.particles[0])
        self.assertFalse(np.array_equal(initial_velocity, self.optimizer.particles[0].velocity))

    def test_update_position(self):
        """Test position update mechanism."""
        self.optimizer.initialize_particles()
        initial_position = self.optimizer.particles[0].position.copy()
        self.optimizer.update_position(self.optimizer.particles[0])
        self.assertFalse(np.array_equal(initial_position, self.optimizer.particles[0].position))

    def test_global_best_update(self):
        """Test global best update."""
        def sphere_function(x):
            return np.sum(x**2)

        self.optimizer.set_fitness_function(sphere_function)
        self.optimizer.initialize_particles()
        self.optimizer.update_global_best()
        self.assertIsNotNone(self.optimizer.global_best_position)
        self.assertIsNotNone(self.optimizer.global_best_fitness)

    def test_optimization_convergence(self):
        """Test optimization convergence with a simple function."""
        def sphere_function(x):
            return np.sum(x**2)

        self.optimizer.set_fitness_function(sphere_function)
        self.optimizer.optimize(max_iterations=50)
        self.assertLess(self.optimizer.global_best_fitness, 1.0) # Check for convergence

    def test_bounds_handling(self):
        """Test bounds handling during position updates."""
        def sphere_function(x):
            return np.sum(x**2)

        self.optimizer.set_fitness_function(sphere_function)
        self.optimizer.initialize_particles()
        for _ in range(50):
            self.optimizer.update_position(self.optimizer.particles[0])
            for i in range(self.optimizer.dimensions):
                self.assertGreaterEqual(self.optimizer.particles[0].position[i], self.optimizer.bounds[i][0])
                self.assertLessEqual(self.optimizer.particles[0].position[i], self.optimizer.bounds[i][1])

    def test_different_dimensions(self):
        """Test with different number of dimensions."""
        optimizer = ParticleSwarmOptimizer(
            num_particles=10,
            dimensions=5,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5)] * 5
        )
        def sphere_function(x):
            return np.sum(x**2)
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=20)
        self.assertIsNotNone(optimizer.global_best_position)

    def test_random_initialization(self):
        """Test random initialization of particles."""
        optimizer1 = ParticleSwarmOptimizer(
            num_particles=5,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer2 = ParticleSwarmOptimizer(
            num_particles=5,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer1.initialize_particles()
        optimizer2.initialize_particles()
        self.assertFalse(np.array_equal(optimizer1.particles[0].position, optimizer2.particles[0].position))

    def test_particle_best_update(self):
        """Test particle's personal best update."""
        def sphere_function(x):
            return np.sum(x**2)

        self.optimizer.set_fitness_function(sphere_function)
        self.optimizer.initialize_particles()
        initial_fitness = self.optimizer.particles[0].fitness
        self.optimizer.update_particle_best(self.optimizer.particles[0])
        self.assertIsNotNone(self.optimizer.particles[0].personal_best_position)
        self.assertIsNotNone(self.optimizer.particles[0].personal_best_fitness)
        self.assertEqual(self.optimizer.particles[0].personal_best_fitness, initial_fitness)

    def test_optimization_with_different_weights(self):
        """Test optimization with different weights."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.9,
            cognitive_weight=1.0,
            social_weight=1.0,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_bounds(self):
        """Test optimization with different bounds."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-10, 10), (-10, 10)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_high_inertia(self):
        """Test optimization with high inertia weight."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.9,
            cognitive_weight=1.0,
            social_weight=1.0,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_low_inertia(self):
        """Test optimization with low inertia weight."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.1,
            cognitive_weight=1.0,
            social_weight=1.0,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_cognitive_weight(self):
        """Test optimization with different cognitive weight."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=2.0,
            social_weight=1.0,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_social_weight(self):
        """Test optimization with different social weight."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.0,
            social_weight=2.0,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_number_of_particles(self):
        """Test optimization with different number of particles."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=50,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_max_iterations(self):
        """Test optimization with different max iterations."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=100)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_fitness_function(self):
        """Test optimization with a different fitness function (Rosenbrock)."""
        def rosenbrock_function(x):
            return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-2, 2), (-2, 2)]
        )
        optimizer.set_fitness_function(rosenbrock_function)
        optimizer.optimize(max_iterations=100)
        self.assertLess(optimizer.global_best_fitness, 10.0)

    def test_optimization_with_high_dimensional_space(self):
        """Test optimization in a higher dimensional space."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=10,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5)] * 10
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 10.0)

    def test_optimization_with_non_symmetric_bounds(self):
        """Test optimization with non-symmetric bounds."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-1, 5), (-2, 3)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_large_bounds(self):
        """Test optimization with large bounds."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-100, 100), (-100, 100)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 100.0)

    def test_optimization_with_negative_bounds(self):
        """Test optimization with negative bounds."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, -1), (-5, -1)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 25.0)

    def test_optimization_with_zero_bounds(self):
        """Test optimization with zero bounds."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(0, 0), (0, 0)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertEqual(optimizer.global_best_fitness, 0.0)

    def test_optimization_with_different_initial_positions(self):
        """Test optimization with different initial positions."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer1 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer2 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer1.set_fitness_function(sphere_function)
        optimizer2.set_fitness_function(sphere_function)
        optimizer1.initialize_particles()
        optimizer2.initialize_particles()
        optimizer1.optimize(max_iterations=50)
        optimizer2.optimize(max_iterations=50)
        self.assertNotEqual(optimizer1.global_best_position[0], optimizer2.global_best_position[0])
        self.assertNotEqual(optimizer1.global_best_position[1], optimizer2.global_best_position[1])

    def test_optimization_with_constant_fitness(self):
        """Test optimization with a constant fitness function."""
        def constant_function(x):
            return 1.0

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(constant_function)
        optimizer.optimize(max_iterations=50)
        self.assertEqual(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_unbounded_function(self):
        """Test optimization with an unbounded function (e.g., a line)."""
        def linear_function(x):
            return x[0] + x[1]

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(linear_function)
        optimizer.optimize(max_iterations=50)
        self.assertIsNotNone(optimizer.global_best_fitness)

    def test_optimization_with_noisy_fitness(self):
        """Test optimization with a noisy fitness function."""
        def noisy_sphere_function(x):
            return np.sum(x**2) + np.random.normal(0, 0.1)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(noisy_sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_non_convex_function(self):
        """Test optimization with a non-convex function (e.g., a saddle)."""
        def saddle_function(x):
            return x[0]**2 - x[1]**2

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(saddle_function)
        optimizer.optimize(max_iterations=50)
        self.assertIsNotNone(optimizer.global_best_fitness)

    def test_optimization_with_multiple_local_minima(self):
        """Test optimization with a function with multiple local minima."""
        def multiple_minima_function(x):
            return np.sin(x[0]) * np.cos(x[1])

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer.set_fitness_function(multiple_minima_function)
        optimizer.optimize(max_iterations=50)
        self.assertIsNotNone(optimizer.global_best_fitness)

    def test_optimization_with_a_complex_function(self):
        """Test optimization with a more complex function."""
        def complex_function(x):
            return np.sum(np.sin(x) * np.exp(-x**2))

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=5,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5)] * 5
        )
        optimizer.set_fitness_function(complex_function)
        optimizer.optimize(max_iterations=50)
        self.assertIsNotNone(optimizer.global_best_fitness)

    def test_optimization_with_a_very_high_dimensional_space(self):
        """Test optimization in a very high dimensional space."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=50,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5)] * 50
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=20)
        self.assertLess(optimizer.global_best_fitness, 200.0)

    def test_optimization_with_different_initial_velocities(self):
        """Test optimization with different initial velocities."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer1 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer2 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer1.set_fitness_function(sphere_function)
        optimizer2.set_fitness_function(sphere_function)
        optimizer1.initialize_particles()
        optimizer2.initialize_particles()
        for particle in optimizer1.particles:
            particle.velocity = np.random.rand(2) * 2 - 1
        for particle in optimizer2.particles:
            particle.velocity = np.random.rand(2) * 2 - 1
        optimizer1.optimize(max_iterations=50)
        optimizer2.optimize(max_iterations=50)
        self.assertNotEqual(optimizer1.global_best_position[0], optimizer2.global_best_position[0])
        self.assertNotEqual(optimizer1.global_best_position[1], optimizer2.global_best_position[1])

    def test_optimization_with_large_velocity_range(self):
        """Test optimization with a large velocity range."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)],
            velocity_bounds=[(-10, 10), (-10, 10)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_small_velocity_range(self):
        """Test optimization with a small velocity range."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)],
            velocity_bounds=[(-0.1, 0.1), (-0.1, 0.1)]
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_adaptive_inertia_weight(self):
        """Test optimization with an adaptive inertia weight."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.9,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)],
            adaptive_inertia=True,
            inertia_weight_range=(0.4, 0.9)
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_adaptive_weights(self):
        """Test optimization with adaptive cognitive and social weights."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)],
            adaptive_weights=True,
            cognitive_weight_range=(0.5, 2.5),
            social_weight_range=(0.5, 2.5)
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_constriction_coefficient(self):
        """Test optimization with constriction coefficient."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)],
            constriction_coefficient=True
        )
        optimizer.set_fitness_function(sphere_function)
        optimizer.optimize(max_iterations=50)
        self.assertLess(optimizer.global_best_fitness, 1.0)

    def test_optimization_with_different_initial_particle_positions(self):
        """Test optimization with different initial particle positions."""
        def sphere_function(x):
            return np.sum(x**2)

        optimizer1 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer2 = ParticleSwarmOptimizer(
            num_particles=20,
            dimensions=2,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4,
            bounds=[(-5, 5), (-5, 5)]
        )
        optimizer1.set_fitness_function(sphere_function)
        optimizer2.set_fitness_function(sphere_function)
        optimizer1.initialize_particles()
        optimizer2.initialize_particles()
        optimizer1.particles[0].position = np.array([1,1])
        optimizer2.particles[0].position = np.array([-1,-1])
        optimizer1.optimize(max_iterations=50)
        optimizer2.optimize(max_iterations=50)
        self.assertNotEqual(optimizer1.global_best_position[0], optimizer2.global_best_position[0])
        self.assertNotEqual(optimizer1.global_best_position[1], optimizer2.global_best_position[1])