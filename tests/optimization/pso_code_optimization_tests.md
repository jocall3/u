# Particle Swarm Optimization Code Optimization Tests

This document outlines test cases designed to verify the effectiveness and convergence of Particle Swarm Optimization (PSO) algorithms when applied to code optimization problems. The tests cover various aspects, including basic functionality, convergence speed, robustness to different problem landscapes, and scalability.

## Test Case 1: Basic Functionality - Minimizing a Simple Function

**Objective:** Verify that the PSO algorithm can successfully minimize a simple, well-defined function.

**Function:**  `f(x) = x^2`

**Search Space:**  `-10 <= x <= 10`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 100

**Expected Outcome:** The PSO algorithm should converge to a solution close to `x = 0` with a function value close to `0`.

**Metrics:**

*   Best function value found.
*   Number of iterations to convergence (defined as reaching a function value below a threshold, e.g., 0.001).
*   Standard deviation of particle positions at the final iteration.

## Test Case 2: Convergence Speed - Comparing Different Parameter Settings

**Objective:**  Evaluate the impact of different PSO parameter settings on the convergence speed.

**Function:**  `f(x, y) = x^2 + y^2`

**Search Space:**  `-10 <= x <= 10`, `-10 <= y <= 10`

**PSO Parameters:**

*   Number of particles: 30
*   Maximum iterations: 100

**Parameter Variations:**

*   **Scenario 1:** w = 0.7, c1 = 1.5, c2 = 1.5
*   **Scenario 2:** w = 0.4, c1 = 2.0, c2 = 2.0
*   **Scenario 3:** w = 0.9, c1 = 1.0, c2 = 1.0

**Expected Outcome:**  Different parameter settings will result in varying convergence speeds.  Analyze which settings lead to faster convergence.

**Metrics:**

*   Average function value over multiple runs (e.g., 10 runs) for each scenario at different iteration points (e.g., iterations 10, 20, 50, 100).
*   Time taken to reach a specific function value threshold.

## Test Case 3: Robustness - Noisy Function

**Objective:**  Assess the robustness of the PSO algorithm in the presence of noise.

**Function:**  `f(x) = x^2 + noise(x)` where `noise(x)` is a random value drawn from a normal distribution with mean 0 and standard deviation 1.

**Search Space:**  `-10 <= x <= 10`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 100

**Expected Outcome:**  The PSO algorithm should still converge towards the minimum, but the convergence will be slower and the final solution may not be as precise as in the noiseless case.

**Metrics:**

*   Best function value found.
*   Number of iterations to convergence (defined as reaching a function value below a threshold).
*   Compare the performance with the noiseless version of the same function.

## Test Case 4: Scalability - High-Dimensional Function

**Objective:**  Evaluate the performance of the PSO algorithm as the dimensionality of the problem increases.

**Function:**  `f(x1, x2, ..., xn) = sum(xi^2)` for `i = 1 to n`

**Search Space:**  `-10 <= xi <= 10` for all `i`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 100

**Dimensionality Variations:**

*   n = 2
*   n = 10
*   n = 50

**Expected Outcome:**  The convergence speed and the quality of the solution will likely decrease as the dimensionality increases.

**Metrics:**

*   Best function value found for each dimensionality.
*   Number of iterations to convergence for each dimensionality.
*   Computational time for each dimensionality.

## Test Case 5: Constrained Optimization - Linear Constraints

**Objective:**  Test the PSO algorithm's ability to handle linear constraints.

**Function:**  `f(x, y) = x^2 + y^2`

**Search Space:**

*   `-10 <= x <= 10`
*   `-10 <= y <= 10`
*   Constraint: `x + y <= 5`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 100
*   Constraint handling method:  (e.g., penalty function, feasibility rules)

**Expected Outcome:**  The PSO algorithm should converge to a solution that satisfies the constraint `x + y <= 5` and minimizes the function `f(x, y)`.

**Metrics:**

*   Best function value found.
*   Percentage of particles that satisfy the constraint at the final iteration.
*   Number of iterations to convergence.

## Test Case 6: Discrete Optimization - Feature Selection

**Objective:**  Evaluate the PSO algorithm's performance in a discrete optimization problem, specifically feature selection.

**Problem:**  Given a dataset with `n` features, select a subset of `k` features that maximizes the classification accuracy of a machine learning model (e.g., a Support Vector Machine).

**Search Space:**  Each particle represents a binary vector of length `n`, where a `1` indicates that the corresponding feature is selected and a `0` indicates that it is not.  The constraint is that the number of selected features must be equal to `k`.

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 50
*   Velocity update rule:  (e.g., sigmoid function to map velocities to probabilities of selecting a feature)

**Fitness Function:**  Classification accuracy of the machine learning model using the selected features.

**Expected Outcome:**  The PSO algorithm should identify a subset of `k` features that achieves a high classification accuracy.

**Metrics:**

*   Best classification accuracy achieved.
*   Selected features.
*   Comparison with other feature selection methods (e.g., greedy search).

## Test Case 7: Code Optimization - Reducing Execution Time

**Objective:**  Apply PSO to optimize a piece of code to reduce its execution time.

**Code Snippet:**  A computationally intensive function (e.g., matrix multiplication, image processing algorithm).

**Optimization Parameters:**  Parameters that can be adjusted to affect the code's performance (e.g., loop unrolling factor, block size for matrix multiplication, compiler optimization flags).

**Search Space:**  The range of possible values for each optimization parameter.

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 50

**Fitness Function:**  Negative of the execution time of the code snippet.

**Expected Outcome:**  The PSO algorithm should find a set of optimization parameter values that significantly reduces the execution time of the code snippet.

**Metrics:**

*   Execution time before optimization.
*   Execution time after optimization.
*   Percentage reduction in execution time.
*   Optimal parameter values found.

## Test Case 8: Hybrid Optimization - PSO with Local Search

**Objective:**  Investigate the benefits of combining PSO with a local search algorithm.

**Function:**  A complex, multimodal function (e.g., Rastrigin function).

**Search Space:**  `-5.12 <= x <= 5.12`, `-5.12 <= y <= 5.12`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 50

**Local Search Algorithm:**  (e.g., Hill Climbing, Simulated Annealing)

**Hybrid Approach:**  After each iteration of the PSO algorithm, apply the local search algorithm to the best particle found so far.

**Expected Outcome:**  The hybrid approach should converge to a better solution than PSO alone, especially for multimodal functions.

**Metrics:**

*   Best function value found by PSO alone.
*   Best function value found by the hybrid approach.
*   Number of iterations to convergence for both approaches.

## Test Case 9: Dynamic Optimization - Time-Varying Function

**Objective:**  Evaluate the PSO algorithm's ability to track the optimum of a time-varying function.

**Function:**  `f(x, t) = (x - shift(t))^2` where `shift(t)` is a function that changes the location of the minimum over time.  For example, `shift(t) = sin(t)`.

**Search Space:**  `-10 <= x <= 10`

**PSO Parameters:**

*   Number of particles: 30
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 100

**Expected Outcome:**  The PSO algorithm should continuously adapt its search to track the moving optimum.

**Metrics:**

*   Average distance between the best particle's position and the true optimum at each time step.
*   Tracking error over time.

## Test Case 10: Parallel PSO - Performance Improvement

**Objective:**  Measure the performance improvement achieved by parallelizing the PSO algorithm.

**Function:**  `f(x1, x2, ..., xn) = sum(xi^2)` for `i = 1 to n` (High-dimensional function)

**Search Space:**  `-10 <= xi <= 10` for all `i`

**PSO Parameters:**

*   Number of particles: 100
*   Inertia weight (w): 0.7
*   Cognitive coefficient (c1): 1.5
*   Social coefficient (c2): 1.5
*   Maximum iterations: 50

**Parallelization:**  Implement the PSO algorithm using a parallel computing framework (e.g., MPI, OpenMP).

**Expected Outcome:**  The parallel implementation should significantly reduce the execution time compared to the sequential implementation, especially for high-dimensional problems.

**Metrics:**

*   Execution time of the sequential implementation.
*   Execution time of the parallel implementation with different numbers of processors.
*   Speedup (ratio of sequential execution time to parallel execution time).
*   Efficiency (speedup divided by the number of processors).