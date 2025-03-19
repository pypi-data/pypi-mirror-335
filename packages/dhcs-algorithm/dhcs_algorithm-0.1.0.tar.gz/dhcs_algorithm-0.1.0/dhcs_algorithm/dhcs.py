import numpy as np
import random
import time

# Define the Ackley Function (benchmark problem)
def ackley_function(x):
    n = len(x)
    term1 = -20 * np.exp(-0.2 * np.sqrt(np.sum(x**2) / n))
    term2 = -np.exp(np.sum(np.cos(2 * np.pi * x)) / n)
    return term1 + term2 + 20 + np.exp(1)

# Define the Agent class
class Agent:
    def __init__(self, dim, role="explorer"):
        self.position = np.random.uniform(-5, 5, dim)  # Initial position
        self.velocity = np.zeros(dim)  # Initial velocity
        self.best_position = np.copy(self.position)  # Best position found by the agent
        self.best_fitness = ackley_function(self.position)  # Best fitness found by the agent
        self.memory = []  # Shared memory of solutions
        self.role = role  # Role: explorer, refiner, leader, communicator
        self.fitness = self.best_fitness  # Current fitness of the agent
    
    def evaluate(self):
        # Evaluate the fitness of the agent
        self.fitness = ackley_function(self.position)
        if self.fitness < self.best_fitness:
            self.best_fitness = self.fitness
            self.best_position = np.copy(self.position)
    
    def update_position(self):
        # Update the agent's position based on its velocity
        self.position += self.velocity
    
    def update_velocity(self, global_best_position, inertia_weight=0.5, cognitive_weight=1.5, social_weight=1.5):
        # Update velocity based on its own best position and the global best position
        self.velocity = (inertia_weight * self.velocity + 
                         cognitive_weight * np.random.random() * (self.best_position - self.position) + 
                         social_weight * np.random.random() * (global_best_position - self.position))
    
    def update_memory(self):
        # Store the agent's best position in memory
        self.memory.append(self.best_position)
        if len(self.memory) > 10:  # Limit memory size
            self.memory.pop(0)
    
    def adapt_role(self, fitness_threshold=1.2):
        # Adapt role based on fitness improvement and thresholds
        if self.fitness < self.best_fitness * fitness_threshold:
            self.role = "refiner"
        elif self.fitness > self.best_fitness * 2:
            self.role = "explorer"

# Define the DHCS Algorithm
class DynamicHierarchicalCooperativeSwarm:
    def __init__(self, num_agents, dim, max_iterations):
        self.num_agents = num_agents
        self.dim = dim
        self.max_iterations = max_iterations
        self.agents = [Agent(dim) for _ in range(num_agents)]
        self.global_best_position = None
        self.global_best_fitness = float("inf")
        self.cluster_leaders = []  # List of leader agents

    def form_clusters(self):
        # Calculate distances between agents and group them based on fitness and position similarity
        self.cluster_leaders = []
        cluster_threshold = 2.0  # Adjust the threshold for clustering

        for agent in self.agents:
            # Add agent to cluster based on fitness and proximity
            close_agents = [a for a in self.agents if np.linalg.norm(agent.position - a.position) < cluster_threshold]
            if len(close_agents) > 1:
                # If an agent is close to others and has good fitness, it can become a leader
                best_agent = min(close_agents, key=lambda a: a.best_fitness)
                if best_agent.fitness < self.global_best_fitness * 1.5:
                    self.cluster_leaders.append(best_agent)

    def synchronize_agents(self):
        # Synchronize all agents periodically to avoid divergence
        for agent in self.agents:
            agent.position = np.mean([a.position for a in self.agents], axis=0)  # Simple synchronization (average positions)
            agent.velocity = np.mean([a.velocity for a in self.agents], axis=0)  # Synchronize velocities

    def run(self):
        history = []
        last_improvement_iter = 0  # To track the number of iterations since the last improvement
        for iteration in range(self.max_iterations):
            # Evaluate and adapt agents' roles
            for agent in self.agents:
                agent.evaluate()
                agent.update_memory()
                agent.adapt_role()

                # Update global best
                if agent.fitness < self.global_best_fitness:
                    self.global_best_fitness = agent.fitness
                    self.global_best_position = np.copy(agent.position)
                    last_improvement_iter = iteration  # Reset counter on improvement
            
            # Form clusters dynamically (ensure there are leaders)
            self.form_clusters()

            # Synchronize agents only if there's no improvement in the last 10 iterations
            if iteration - last_improvement_iter > 10:  # If no improvement in 10 iterations
                self.synchronize_agents()

            # Update each agent's velocity and position
            for agent in self.agents:
                if agent.role == "leader" and self.cluster_leaders:
                    leader_position = random.choice(self.cluster_leaders).best_position
                else:
                    leader_position = self.global_best_position
                agent.update_velocity(leader_position)
                agent.update_position()

            # Periodically adjust exploration vs exploitation
            if iteration % 10 == 0:
                self.adjust_exploration_exploitation()

            history.append(self.global_best_fitness)
            print(f"Iteration {iteration + 1}: Global Best Fitness = {self.global_best_fitness}")

        return history

    def adjust_exploration_exploitation(self):
        # Adjust exploration/exploitation strategy based on the fitness landscape
        if self.global_best_fitness > 50:
            for agent in self.agents:
                agent.role = "explorer"
        else:
            for agent in self.agents:
                agent.role = "refiner"

def run_dhcs(objective_function, num_agents=50, dim=10, max_iterations=100):
    """
    Run the Dynamic Hierarchical Cooperative Swarm Optimization algorithm.

    Parameters:
        objective_function (callable): The function to optimize.
        num_agents (int, optional): Number of agents (default: 50).
        dim (int, optional): Number of dimensions (default: 10).
        max_iterations (int, optional): Maximum iterations (default: 100).

    Returns:
        dict: Optimization results with best position, best fitness, and runtime.
    """
    if not callable(objective_function):
        raise ValueError("You must provide a valid objective function.")

    swarm = DynamicHierarchicalCooperativeSwarm(num_agents, dim, objective_function, max_iterations)
    start_time = time.time()
    history = swarm.run()
    end_time = time.time()

    return {
        "best_position": swarm.global_best_position,
        "best_fitness": swarm.global_best_fitness,
        "time_taken": end_time - start_time,
        "history": history
    }
