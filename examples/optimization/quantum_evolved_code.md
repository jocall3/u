# Quantum-Evolved Code Optimization: A Particle Swarm Approach

## Introduction to Quantum-Inspired Optimization

This document explores the fascinating intersection of quantum computing principles and evolutionary optimization techniques, specifically focusing on particle swarm optimization (PSO). We will delve into how quantum mechanics can inspire novel approaches to enhance the performance and efficiency of PSO algorithms.

### The Quantum Realm: A Source of Inspiration

Quantum mechanics offers concepts like superposition, entanglement, and quantum tunneling, which can be leveraged to improve the exploration and exploitation capabilities of optimization algorithms.

### Particle Swarm Optimization: A Primer

PSO is a population-based optimization technique inspired by the social behavior of bird flocking or fish schooling. A swarm of particles searches the solution space, adjusting their positions based on their own experience and the experience of their neighbors.

## Quantum-Enhanced Particle Swarm Optimization (QPSO)

QPSO introduces quantum mechanical principles into the standard PSO algorithm. Instead of tracking velocity and position directly, QPSO particles exist in a quantum state, described by a wave function.

### Key Concepts in QPSO

*   **Wave Function:** Represents the probability of finding a particle at a particular location.
*   **Potential Well:** Confines the particle's movement within a certain region.
*   **Monte Carlo Simulation:** Used to sample the particle's position from its probability distribution.

### QPSO Algorithm Steps

1.  **Initialization:** Initialize a population of particles with random positions within the search space.
2.  **Fitness Evaluation:** Evaluate the fitness of each particle based on the objective function.
3.  **Update Personal Best (pbest):** For each particle, update its pbest if its current fitness is better than its previous pbest.
4.  **Update Global Best (gbest):** Update the gbest with the best pbest found so far.
5.  **Calculate Mean Best Position (mbest):** Calculate the average of all pbest positions.
6.  **Update Particle Position:** Update each particle's position using a quantum-inspired update rule, typically involving the mbest, pbest, and a random number.
7.  **Repeat:** Repeat steps 2-6 until a stopping criterion is met (e.g., maximum number of iterations or desired fitness level).

## Code Examples: Evolving Towards Optimal Solutions

The following examples demonstrate how QPSO can be implemented and applied to various optimization problems.

### Example 1: Minimizing a Simple Function (Sphere Function)

```python
import numpy as np
import random

def sphere_function(x):
    """
    The Sphere function is a simple unimodal function.
    """
    return np.sum(x**2)

def qpso(objective_function, bounds, n_particles, n_iterations):
    """
    Quantum Particle Swarm Optimization algorithm.

    Args:
        objective_function: The function to be minimized.
        bounds: A list of tuples, where each tuple represents the lower and upper bounds for a dimension.
        n_particles: The number of particles in the swarm.
        n_iterations: The number of iterations to run the algorithm.

    Returns:
        A tuple containing the best position and the best fitness value found.
    """

    n_dimensions = len(bounds)
    particles = np.random.uniform(low=[b[0] for b in bounds], high=[b[1] for b in bounds], size=(n_particles, n_dimensions))
    pbest_positions = particles.copy()
    pbest_fitnesses = np.array([objective_function(p) for p in particles])
    gbest_index = np.argmin(pbest_fitnesses)
    gbest_position = pbest_positions[gbest_index].copy()

    for iteration in range(n_iterations):
        mbest = np.mean(pbest_positions, axis=0)

        for i in range(n_particles):
            phi = random.uniform(0, 1)
            p = phi * pbest_positions[i] + (1 - phi) * gbest_position
            u = np.random.uniform(0, 1, n_dimensions)
            beta = 0.5  # Contraction-expansion coefficient
            new_position = p + beta * np.abs(particles[i] - mbest) * np.log(1/u)

            # Clip the position to stay within the bounds
            for d in range(n_dimensions):
                new_position[d] = np.clip(new_position[d], bounds[d][0], bounds[d][1])

            fitness = objective_function(new_position)

            if fitness < pbest_fitnesses[i]:
                pbest_fitnesses[i] = fitness
                pbest_positions[i] = new_position.copy()

                if fitness < objective_function(gbest_position):
                    gbest_position = new_position.copy()

            particles[i] = new_position.copy()

    return gbest_position, objective_function(gbest_position)


# Example usage
bounds = [(-10, 10), (-10, 10)]  # Define the bounds for each dimension
n_particles = 30
n_iterations = 100

best_position, best_fitness = qpso(sphere_function, bounds, n_particles, n_iterations)

print("Best position:", best_position)
print("Best fitness:", best_fitness)
```

### Example 2: Optimizing a Neural Network's Weights

```python
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_regression

# Generate a synthetic dataset
X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


def neural_network_fitness(weights, input_shape, hidden_layer_sizes, X_train, y_train, X_test, y_test):
    """
    Evaluates the fitness of a neural network based on its weights.

    Args:
        weights: A 1D array of weights for the neural network.
        input_shape: The number of input features.
        hidden_layer_sizes: A tuple specifying the size of each hidden layer.
        X_train: Training data features.
        y_train: Training data labels.
        X_test: Testing data features.
        y_test: Testing data labels.

    Returns:
        The negative mean squared error (MSE) on the test set.  We use negative MSE because QPSO minimizes.
    """

    # Create the neural network model
    model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, activation='relu', solver='adam', random_state=42, max_iter=200)

    # Set the weights of the model
    start = 0
    for i, layer in enumerate(model.coefs_):
        end = start + layer.size
        model.coefs_[i] = weights[start:end].reshape(layer.shape)
        start = end

    start = 0
    for i, bias in enumerate(model.intercepts_):
        end = start + bias.size
        model.intercepts_[i] = weights[start:end].reshape(bias.shape)
        start = end

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model on the test set
    mse = np.mean((model.predict(X_test) - y_test)**2)

    return -mse  # Return negative MSE for minimization


def qpso_nn(X_train, y_train, X_test, y_test, hidden_layer_sizes=(10,), n_particles=20, n_iterations=50):
    """
    Optimizes the weights of a neural network using Quantum Particle Swarm Optimization.

    Args:
        X_train: Training data features.
        y_train: Training data labels.
        X_test: Testing data features.
        y_test: Testing data labels.
        hidden_layer_sizes: A tuple specifying the size of each hidden layer.
        n_particles: The number of particles in the swarm.
        n_iterations: The number of iterations to run the algorithm.

    Returns:
        A tuple containing the best weights and the best fitness value found.
    """

    input_shape = X_train.shape[1]
    # Calculate the total number of weights and biases in the neural network
    n_weights = 0
    model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, activation='relu', solver='adam', random_state=42, max_iter=200)
    model.fit(X_train, y_train) # Fit to get the shapes of the weights and biases
    for layer in model.coefs_:
        n_weights += layer.size
    for bias in model.intercepts_:
        n_weights += bias.size

    # Define the bounds for the weights (you might need to adjust these)
    bounds = [(-1, 1)] * n_weights

    # Define a wrapper function for the fitness function to pass additional arguments
    def fitness_wrapper(weights):
        return neural_network_fitness(weights, input_shape, hidden_layer_sizes, X_train, y_train, X_test, y_test)

    # Run QPSO
    best_weights, best_fitness = qpso(fitness_wrapper, bounds, n_particles, n_iterations)

    return best_weights, best_fitness


# Example usage
hidden_layer_sizes = (20, 10)  # Example hidden layer sizes
n_particles = 20
n_iterations = 50

best_weights, best_fitness = qpso_nn(X_train, y_train, X_test, y_test, hidden_layer_sizes, n_particles, n_iterations)

print("Best weights:", best_weights)
print("Best fitness (negative MSE):", best_fitness)

# Evaluate the optimized neural network
model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, activation='relu', solver='adam', random_state=42, max_iter=200)

# Set the weights of the model
start = 0
for i, layer in enumerate(model.coefs_):
    end = start + layer.size
    model.coefs_[i] = best_weights[start:end].reshape(layer.shape)
    start = end

start = 0
for i, bias in enumerate(model.intercepts_):
    end = start + bias.size
    model.intercepts_[i] = best_weights[start:end].reshape(bias.shape)
    start = end

model.fit(X_train, y_train)
mse = np.mean((model.predict(X_test) - y_test)**2)
print("MSE on test set with optimized weights:", mse)
```

### Example 3: Feature Selection with QPSO

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Generate a synthetic dataset with many features
X, y = make_classification(n_samples=100, n_features=20, n_informative=10, n_redundant=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


def feature_selection_fitness(mask, X_train, y_train, X_test, y_test):
    """
    Evaluates the fitness of a feature subset based on classification accuracy.

    Args:
        mask: A boolean array indicating which features to select (True) and which to discard (False).
        X_train: Training data features.
        y_train: Training data labels.
        X_test: Testing data features.
        y_test: Testing data labels.

    Returns:
        The classification accuracy on the test set.
    """

    # Select the features based on the mask
    selected_features = np.where(mask)[0]
    if len(selected_features) == 0:
        return 0  # Return a low score if no features are selected

    X_train_selected = X_train[:, selected_features]
    X_test_selected = X_test[:, selected_features]

    # Train a logistic regression model
    model = LogisticRegression(solver='liblinear', random_state=42)
    model.fit(X_train_selected, y_train)

    # Predict on the test set
    y_pred = model.predict(X_test_selected)

    # Calculate the accuracy
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy


def qpso_feature_selection(X_train, y_train, X_test, y_test, n_particles=20, n_iterations=50):
    """
    Performs feature selection using Quantum Particle Swarm Optimization.

    Args:
        X_train: Training data features.
        y_train: Training data labels.
        X_test: Testing data features.
        y_test: Testing data labels.
        n_particles: The number of particles in the swarm.
        n_iterations: The number of iterations to run the algorithm.

    Returns:
        A tuple containing the best feature mask and the best fitness value (accuracy).
    """

    n_features = X_train.shape[1]

    # Define the bounds for the particle positions (0 or 1 for each feature)
    bounds = [(0, 1)] * n_features

    # Define a wrapper function for the fitness function
    def fitness_wrapper(position):
        # Convert the continuous position to a boolean mask
        mask = position > 0.5  # Threshold at 0.5
        return feature_selection_fitness(mask, X_train, y_train, X_test, y_test)

    # Run QPSO
    best_position, best_fitness = qpso(fitness_wrapper, bounds, n_particles, n_iterations)

    # Convert the best position to a boolean mask
    best_mask = np.array(best_position) > 0.5

    return best_mask, best_fitness


# Example usage
n_particles = 20
n_iterations = 50

best_mask, best_accuracy = qpso_feature_selection(X_train, y_train, X_test, y_test, n_particles, n_iterations)

print("Best feature mask:", best_mask)
print("Best accuracy:", best_accuracy)

# Evaluate the model with the selected features
selected_features = np.where(best_mask)[0]
X_train_selected = X_train[:, selected_features]
X_test_selected = X_test[:, selected_features]

model = LogisticRegression(solver='liblinear', random_state=42)
model.fit(X_train_selected, y_train)
y_pred = model.predict(X_test_selected)
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy with selected features:", accuracy)
```

## Advanced Concepts and Considerations

### Hybrid QPSO Algorithms

Combining QPSO with other optimization techniques, such as genetic algorithms or simulated annealing, can further enhance its performance.

### Parameter Tuning

The performance of QPSO is sensitive to the choice of parameters, such as the contraction-expansion coefficient (beta) and the number of particles. Careful tuning is crucial for achieving optimal results.

### Applications of QPSO

QPSO has been successfully applied to a wide range of optimization problems, including:

*   **Engineering Design:** Optimizing the design of structures, circuits, and other engineering systems.
*   **Machine Learning:** Training neural networks, feature selection, and hyperparameter optimization.
*   **Finance:** Portfolio optimization and risk management.
*   **Logistics:** Routing and scheduling problems.

## Conclusion

Quantum-enhanced particle swarm optimization offers a powerful and versatile approach to solving complex optimization problems. By incorporating principles from quantum mechanics, QPSO can achieve better performance and efficiency compared to traditional PSO algorithms. The examples provided illustrate how QPSO can be implemented and applied to various domains, demonstrating its potential for real-world applications. Further research and development in this area will undoubtedly lead to even more innovative and effective optimization techniques.