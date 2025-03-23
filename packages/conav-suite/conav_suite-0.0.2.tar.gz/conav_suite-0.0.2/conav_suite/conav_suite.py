import random
import numpy as np
import matplotlib.path as mpath

from functools import partial
from .utils.scenario import BaseScenario
from .utils.simple_env import SimpleEnv, make_env
from .utils.core import Agent, Goal, Obstacle, World
from .utils.problems import get_problem_list, get_problem_instance

from gymnasium.utils import EzPickle

random.seed(42)

class raw_env(SimpleEnv, EzPickle):
    def __init__(
        self, 
        num_agents=1, 
        num_large_obstacles=4, 
        large_obstacle_radius=0.05,
        num_small_obstacles=10, 
        small_obstacle_radius=0.02,
        render_mode=None,
        max_cycles=100,
        ):
        
        if num_large_obstacles > 10:
            raise ValueError("conav_suite has a maximum of 10 large obstacles.")
        
        scenario = Scenario()
        world = scenario.make_world(num_agents, num_large_obstacles, large_obstacle_radius, num_small_obstacles, small_obstacle_radius)
        
        super().__init__(
            scenario=scenario, 
            world=world, 
            render_mode=render_mode,
            max_cycles=max_cycles, 
        )
        
env = make_env(raw_env)

class Scenario(BaseScenario):
    def make_world(self, num_agents, num_large_obstacles, large_obstacle_radius, num_small_obstacles, small_obstacle_radius):
        world = World(large_obstacle_radius, small_obstacle_radius)
        world.problem_list = get_problem_list()

        for i in range(num_agents):
            agent = Agent()
            agent.name = f"agent_{i}"
            agent.collide = True
            agent.color = np.array([1, 0.95, 0.8])
            world.agents.append(agent)
        
            goal = Goal()
            goal.name = f"goal_{i}"
            goal.collide = False
            goal.color = np.array([0.835, 0.90, 0.831])
            world.goals.append(goal)
        
        # Large obstacles can only be observed by aerial agent
        for i in range(num_large_obstacles):
            obstacle = Obstacle(radius=large_obstacle_radius)
            obstacle.name = f"obs_{i}"
            obstacle.color = np.array([0.97, 0.801, 0.8])
            world.large_obstacles.append(obstacle)
        
        # Small obstacles can only be observed by ground agent(s)
        for i in range(num_small_obstacles):
            obstacle = Obstacle(radius=small_obstacle_radius)
            obstacle.name = f"obs_{i}"
            obstacle.color = np.array([0.97, 0.801, 0.8])
            world.small_obstacles.append(obstacle)    
        
        world.buffer_dist = world.agents[0].radius + world.large_obstacles[0].radius
        return world
    
    def add_large_obstacles(self, world, num_obstacles):
        for i in range(num_obstacles):
            obstacle = Obstacle(radius=world.large_obstacle_radius)
            obstacle.name = f"obs_{i}"
            obstacle.color = np.array([0.97, 0.801, 0.8])
            world.large_obstacles.append(obstacle)
    
    # Get constraints on entities given problem instance name
    def _set_problem_instance(self, world, instance_name):
        instance_constr = get_problem_instance(instance_name)
        world.problem_instance = instance_name
        world.instance_constr = instance_constr
    
    # Generate valid points according to some condition
    def _generate_position(self, np_random, condition):
        while True:
            point = np_random.uniform(-1, +1, 2)
            if condition(point):
                break
        return point
    
    # Check if point is outside of circular obstacle regions
    def _outside_circles(self, point, centers_radii, epsilon):
        return not any(np.linalg.norm(point - center) <= radius + epsilon for center, radius in centers_radii)
    
    # Check if point is outside of rectangular obstacle regions
    def _outside_rectangle(self, point, x_constraints, y_constraints, epsilon):
        within_constraints = any(
            (low_x - epsilon <= point[0] <= high_x + epsilon) and (low_y - epsilon <= point[1] <= high_y + epsilon)
            for (low_x, high_x), (low_y, high_y) in zip(x_constraints, y_constraints)
        )
        return not within_constraints

    # Reset agents and goals to their initial positions
    def _reset_agents_and_goals(self, world, np_random):
        epsilon = world.agents[0].radius
        
        if world.problem_instance in ['bisect', 'cross', 'staggered', 'quarters']:
            # Used for problem instances composed of rectangles
            x_constraints = [constr[0] for constr in world.instance_constr]
            y_constraints = [constr[1] for constr in world.instance_constr]

        for i, agent in enumerate(world.agents):
            agent.goal = world.goals[i]

            agent.state.p_vel = np.zeros(world.dim_p)
            agent.goal.state.p_vel = np.zeros(world.dim_p)

            if world.problem_instance in ['circle', 'corners', 'scatter', 'stellaris']:
                condition = partial(
                    self._outside_circles,
                    centers_radii=world.instance_constr,
                    epsilon=epsilon,
                    )
            else:
                condition = partial(
                    self._outside_rectangle, 
                    x_constraints=x_constraints, 
                    y_constraints=y_constraints,
                    epsilon=epsilon, 
                    )

            agent.state.p_pos = self._generate_position(np_random, condition)
            agent.goal.state.p_pos = self._generate_position(np_random, condition)
    
    # Reset all large obstacles to a position that does not intersect with the agents and is within its shape
    def _reset_large_obstacles(self, world, np_random, paths, num_obstacles=None):
        def inside_shape_condition(point):
            return any(path.contains_points(point[None, :]) for path in paths)    
        
        occupied = set()
        num_shapes = len(world.instance_constr)
        
        self.add_large_obstacles(world, num_obstacles)
        
        large_obstacles = world.large_obstacles[:]
        random.shuffle(large_obstacles)

        for i, large_obstacle in enumerate(large_obstacles):            
            large_obstacle.state.p_vel = np.zeros(world.dim_p)
            
            while True:
                pos = self._generate_position(np_random, inside_shape_condition)
                shape_idx = next((i for i, path in enumerate(paths) if path.contains_points(pos[None, :])), None)
                
                if i % num_shapes == 0:
                    occupied.clear()
                
                if shape_idx not in occupied:
                    large_obstacle.state.p_pos = pos
                    occupied.add(shape_idx)
                    break
    
    def _reset_small_obstacles(self, world, np_random):
        epsilon = world.small_obstacles[0].radius

        agent_positions = [agent.state.p_pos for agent in world.agents]
        goal_positions = [goal.state.p_pos for goal in world.goals]
        large_obstacle_positions = [obstacle.state.p_pos for obstacle in world.large_obstacles]

        def safe_position(point):
            outside_entity_positions = not any(np.linalg.norm(point - pos) <= epsilon for pos in agent_positions + goal_positions + large_obstacle_positions)

            if world.problem_instance in ['circle', 'corners', 'scatter', 'stellaris']:
                outside_obstacle_constraints = self._outside_circles(point, world.instance_constr, epsilon) 
            else:
                x_constraints = [constr[0] for constr in world.instance_constr]
                y_constraints = [constr[1] for constr in world.instance_constr]
                outside_obstacle_constraints = self._outside_rectangle(point, x_constraints, y_constraints, epsilon)

            return outside_entity_positions and outside_obstacle_constraints

        for small_obstacle in world.small_obstacles:
            small_obstacle.state.p_vel = np.zeros(world.dim_p)
            small_obstacle.state.p_pos = self._generate_position(np_random, safe_position)

    def reset_world(self, world, np_random, problem_instance, add_large_obstacles=0):        
        def make_circle_points(center, radius_and_epsilon, num_points=100):
            t = np.linspace(0, 2*np.pi, num_points)
            x = center[0] + radius_and_epsilon * np.cos(t)
            y = center[1] + radius_and_epsilon * np.sin(t)
            points = np.column_stack([x, y])
            return points
        
        def make_rectangle_points(bounds, epsilon):
            min_x, max_x = bounds[0]
            min_y, max_y = bounds[1]
            return [
                (min_x + epsilon, min_y + epsilon),
                (max_x - epsilon, min_y + epsilon),
                (max_x - epsilon, max_y - epsilon),
                (min_x + epsilon, max_y - epsilon),
            ]

        epsilon = world.large_obstacles[0].radius
        self._set_problem_instance(world, problem_instance)
        
        if world.problem_instance in ['circle', 'corners', 'scatter', 'stellaris']:
            paths = [mpath.Path(make_circle_points(center, radius - epsilon)) for center, radius in world.instance_constr]
        else:
            paths = [mpath.Path(make_rectangle_points(bounds, epsilon)) for bounds in world.instance_constr]

        self._reset_agents_and_goals(world, np_random)
        self._reset_large_obstacles(world, np_random, paths, add_large_obstacles)
        self._reset_small_obstacles(world, np_random)
    
    # Ground agents can only observe the positions of other agents, goals, and small obstacles
    def observation(self, agent, world):
        agent_pos = agent.state.p_pos
        
        num_agents = len(world.agents)
        num_small_obstacles = len(world.small_obstacles)
        
        other_agents = [np.zeros_like(agent_pos) for _ in range(num_agents - 1)]
        obstacles = [np.zeros_like(agent_pos) for _ in range(num_small_obstacles)]
        
        idx = 0
        for other_agent in world.agents:
            if agent.name == other_agent.name:
                continue
            else:
                other_agents[idx] = other_agent.state.p_pos
                idx += 1
        
        for i, small_obstacle in enumerate(world.small_obstacles):
            obstacles[i] = small_obstacle.state.p_pos
                
        goal_pos = agent.goal.state.p_pos
        
        return np.concatenate((agent_pos, goal_pos, other_agents, np.concatenate(obstacles, axis=0)))
        
    # Reward given by agents to agents for reaching their respective goals
    def reward(self, agent, world):
        return 0