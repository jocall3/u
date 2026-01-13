import random

class Particle:
    def __init__(self, code_representation, fitness_function, bounds):
        self.position = code_representation  # The current code construct
        self.velocity = self.initialize_velocity(code_representation)  # How the code is changing
        self.personal_best_position = code_representation.copy()
        self.personal_best_fitness = fitness_function(code_representation)
        self.fitness_function = fitness_function
        self.bounds = bounds

    def initialize_velocity(self, code_representation):
        # Initialize velocity based on the structure of the code representation
        velocity = {}
        for key, value in code_representation.items():
            if isinstance(value, list):
                velocity[key] = [random.uniform(-1, 1) for _ in value]  # Random changes for list elements
            elif isinstance(value, (int, float)):
                velocity[key] = random.uniform(-1, 1)  # Random change for numerical values
            elif isinstance(value, str):
                velocity[key] = random.choice(['add', 'remove', 'replace']) # Random string operations
            else:
                velocity[key] = 0  # No change for other types
        return velocity

    def update_velocity(self, global_best_position, inertia_weight, cognitive_coefficient, social_coefficient):
        for key in self.position:
            if isinstance(self.velocity[key], list):
                for i in range(len(self.velocity[key])):
                    cognitive_component = cognitive_coefficient * random.random() * (self.personal_best_position[key][i] - self.position[key][i])
                    social_component = social_coefficient * random.random() * (global_best_position[key][i] - self.position[key][i])
                    self.velocity[key][i] = inertia_weight * self.velocity[key][i] + cognitive_component + social_component
            elif isinstance(self.velocity[key], (int, float)):
                cognitive_component = cognitive_coefficient * random.random() * (self.personal_best_position[key] - self.position[key])
                social_component = social_coefficient * random.random() * (global_best_position[key] - self.position[key])
                self.velocity[key] = inertia_weight * self.velocity[key] + cognitive_component + social_component
            elif isinstance(self.velocity[key], str):
                # String operations are discrete, so we choose one based on probabilities
                options = ['add', 'remove', 'replace']
                probabilities = [inertia_weight, cognitive_coefficient, social_coefficient]
                self.velocity[key] = random.choices(options, probabilities)[0]

    def update_position(self):
        for key in self.position:
            if isinstance(self.position[key], list):
                for i in range(len(self.position[key])):
                    self.position[key][i] += self.velocity[key][i]
                    # Apply bounds if necessary
                    if self.bounds and key in self.bounds and i < len(self.bounds[key]):
                        lower_bound, upper_bound = self.bounds[key][i]
                        self.position[key][i] = max(min(self.position[key][i], upper_bound), lower_bound)
            elif isinstance(self.position[key], (int, float)):
                self.position[key] += self.velocity[key]
                # Apply bounds if necessary
                if self.bounds and key in self.bounds:
                    lower_bound, upper_bound = self.bounds[key]
                    self.position[key] = max(min(self.position[key], upper_bound), lower_bound)
            elif isinstance(self.position[key], str):
                # Apply string operations based on velocity
                if self.velocity[key] == 'add':
                    self.position[key] += random.choice(['a', 'b', 'c']) # Example: add a random character
                elif self.velocity[key] == 'remove':
                    if self.position[key]:
                        self.position[key] = self.position[key][:-1] # Remove last character
                elif self.velocity[key] == 'replace':
                    if self.position[key]:
                        index_to_replace = random.randint(0, len(self.position[key]) - 1)
                        self.position[key] = self.position[key][:index_to_replace] + random.choice(['x', 'y', 'z']) + self.position[key][index_to_replace+1:]

    def evaluate_fitness(self):
        fitness = self.fitness_function(self.position)
        if fitness < self.personal_best_fitness:
            self.personal_best_fitness = fitness
            self.personal_best_position = self.position.copy()
        return fitness

def particle_swarm_optimization(
    initial_code_representation,
    fitness_function,
    bounds,
    num_particles=30,
    inertia_weight=0.7,
    cognitive_coefficient=1.4,
    social_coefficient=1.4,
    max_iterations=100
):
    """
    Optimizes code constructs using Particle Swarm Optimization.

    Args:
        initial_code_representation (dict): A dictionary representing the initial code state.
                                            Keys are code elements, values are their initial settings.
        fitness_function (callable): A function that takes a code representation (dict) and returns a fitness score.
                                      Lower scores indicate better fitness.
        bounds (dict): A dictionary defining the bounds for each code element.
                       Keys are code element names, values are tuples (lower_bound, upper_bound).
        num_particles (int): The number of particles in the swarm.
        inertia_weight (float): The inertia weight.
        cognitive_coefficient (float): The cognitive coefficient.
        social_coefficient (float): The social coefficient.
        max_iterations (int): The maximum number of iterations.

    Returns:
        dict: The optimized code representation.
    """

    particles = [Particle(initial_code_representation.copy(), fitness_function, bounds) for _ in range(num_particles)]

    global_best_position = initial_code_representation.copy()
    global_best_fitness = fitness_function(initial_code_representation)

    for particle in particles:
        if particle.personal_best_fitness < global_best_fitness:
            global_best_fitness = particle.personal_best_fitness
            global_best_position = particle.personal_best_position.copy()

    for iteration in range(max_iterations):
        for particle in particles:
            particle.update_velocity(global_best_position, inertia_weight, cognitive_coefficient, social_coefficient)
            particle.update_position()
            fitness = particle.evaluate_fitness()

            if fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_position = particle.position.copy()

        # Optional: Adjust PSO parameters dynamically (e.g., decrease inertia weight)
        inertia_weight *= 0.99

        # Optional: Print progress
        print(f"Iteration {iteration+1}: Best Fitness = {global_best_fitness}")

    return global_best_position