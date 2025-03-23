import gymnasium
import numpy as np
import pygame
from gymnasium import spaces
from gymnasium.utils import seeding

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

def make_env(raw_env):
    def env(**kwargs):
        env = raw_env(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env


class SimpleEnv(AECEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "is_parallelizable": True,
        "render_fps": 10,
    }

    def __init__(
        self,
        scenario,
        world,
        max_cycles,
        render_mode=None,
        local_ratio=None,
    ):
        super().__init__()

        self.render_mode = render_mode
        pygame.init()
        self.viewer = None
        self.width = 700
        self.height = 700
        self.screen = pygame.Surface([self.width, self.height])
        self.max_size = 1
        self.game_font = pygame.freetype.Font(None, 20)

        self.renderOn = False
        self.seed()
        self._reset_called = False

        self.max_cycles = max_cycles
        self.scenario = scenario
        self.world = world
        self.local_ratio = local_ratio

        self.scenario.reset_world(self.world, self.np_random, 'bisect')
        self.agents = [agent.name for agent in self.world.agents]
        self.possible_agents = self.agents[:]
        self._index_map = {agent.name: idx for idx, agent in enumerate(self.world.agents)}

        self._agent_selector = agent_selector(self.agents)

        # set spaces
        self.action_spaces = dict()
        self.observation_spaces = dict()
        
        for agent in self.world.agents:
            space_dim = self.world.dim_p * 2 + 1
            self.action_spaces[agent.name] = spaces.Discrete(space_dim)
            obs_dim = len(self.scenario.observation(agent, self.world))
            self.observation_spaces[agent.name] = spaces.Box(
                low=-np.float32(1),
                high=+np.float32(1),
                shape=(obs_dim,),
                dtype=np.float32,
            )
        
        # state space is used by aerial agent; it encodes the positions of all agents, obstacles, and goals
        state_dim = len(world.agents) * 2 + len(world.large_obstacles) * 2 + len(world.agents) * 2
        self.state_space = spaces.Box(
            low=-np.float32(1),
            high=+np.float32(1),
            shape=(state_dim,),
            dtype=np.float32,
        )
        self.steps = 0
        self.current_actions = [None] * self.num_agents

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    def observe(self, agent):
        return self.scenario.observation(
            self.world.agents[self._index_map[agent]], self.world
        ).astype(np.float32)
        
    def state(self):
        if self.steps > 0:
            raise Exception('The state of the system can only be retrieved at the start of an episode before any steps have been taken.')
        
        state = np.zeros(self.state_space.shape)
        
        for i, agent in enumerate(self.world.agents):
            state[2*i : 2*i+2] = agent.state.p_pos

        start_idx = 2 * len(self.world.agents)
        for i, agent in enumerate(self.world.agents):
            state[start_idx + 2*i : start_idx + 2*i+2] = agent.goal.state.p_pos
        
        start_idx = 4 * len(self.world.agents)
        for i, obstacle in enumerate(self.world.large_obstacles):
            state[start_idx + 2*i : start_idx + 2*i+2] = obstacle.state.p_pos
             
        return np.concatenate(state, axis=None)

    def reset(self, seed=None, return_info=False, options=None):        
        if seed is not None:
            self.seed(seed=seed)
            
        if 'problem_instance' not in options:
            raise ValueError("Must provide a problem_instance to reset the environment with.")
        
        problem_instance = options['problem_instance']
        if problem_instance not in self.world.problem_list:
            raise ValueError("problem_instance must be in the problem_list.")
        
        self.scenario.reset_world(self.world, self.np_random, problem_instance)

        self.agents = self.possible_agents[:]
        # PettingZoo Gymansium requires rewards to be set even if not used
        self.rewards = {name: 0.0 for name in self.agents}
        self._cumulative_rewards = {name: 0.0 for name in self.agents}
        self.terminations = {name: False for name in self.agents}
        self.truncations = {name: False for name in self.agents}
        self.infos = {name: {} for name in self.agents}
        
        self._reset_called = True
        self.agent_selection = self._agent_selector.reset()
        self.steps = 0

        self.current_actions = [None] * len(self.world.agents)
        
    def _execute_world_step(self):
        # set action for each agent
        for i, agent in enumerate(self.world.agents):
            action = self.current_actions[i]
            scenario_action = []
            if agent.movable:
                mdim = self.world.dim_p * 2 + 1
                scenario_action.append(action % mdim)
                action //= mdim
            self._set_action(scenario_action, agent)

        self.world.step()

        # PettingZoo Gymansium requires rewards to be set
        # even if they are not used
        global_reward = 0.0
        if self.local_ratio is not None:
            global_reward = float(self.scenario.global_reward(self.world))

        for agent in self.world.agents:
            agent_reward = float(self.scenario.reward(agent, self.world))
            if self.local_ratio is not None:
                reward = (
                    global_reward * (1 - self.local_ratio)
                    + agent_reward * self.local_ratio
                )
            else:
                reward = agent_reward

            self.rewards[agent.name] = reward

    # set env action for a particular agent
    def _set_action(self, action, agent):
        if agent.movable:
            # physical action
            agent.action = np.zeros(self.world.dim_p)
            if action[0] == 1:
                agent.action[0] = -1.0
            elif action[0] == 2:
                agent.action[0] = +1.0
            elif action[0] == 3:
                agent.action[1] = -1.0
            elif action[0] == 4:
                agent.action[1] = +1.0
            sensitivity = 2.0
            agent.action *= sensitivity
            action = action[1:]
        # make sure we used all elements of action
        assert len(action) == 0
    
    # Check if episode is terminated or truncated
    def _episode_status(self):    
        goal_dist_threshold = self.world.agents[0].radius + self.world.agents[0].goal.radius
        small_obs_threshold = self.world.agents[0].radius + self.world.small_obstacles[0].radius
        large_obs_threshold = self.world.agents[0].radius + self.world.large_obstacles[0].radius
        
        small_obstacles = [obs for obs in self.world.small_obstacles]
        large_obstacles = [obs for obs in self.world.large_obstacles]    

        goal_dist = [np.linalg.norm(agent.state.p_pos - agent.goal.state.p_pos) for agent in self.world.agents]
        small_obs_dist = [min(np.linalg.norm(agent.state.p_pos - obs.state.p_pos) for obs in small_obstacles)
                          for agent in self.world.agents]
        large_obs_dist = [min(np.linalg.norm(agent.state.p_pos - obs.state.p_pos) for obs in large_obstacles)
                          for agent in self.world.agents]

        crossed_threshold_small = [dist <= small_obs_threshold for dist in small_obs_dist]
        crossed_threshold_large = [dist <= large_obs_threshold for dist in large_obs_dist]
        
        truncations = [(crossed_small or crossed_large) for crossed_small, crossed_large in zip(crossed_threshold_small, crossed_threshold_large)]
        truncations = [True] * self.num_agents if self.steps >= self.max_cycles else truncations

        terminations = [False] * self.num_agents
        for i, dist in enumerate(goal_dist):
            if dist <= goal_dist_threshold:
                terminations[i] = True

        return {'terminations': terminations, 'truncations': truncations}

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        current_idx = self._index_map[self.agent_selection]
        next_idx = (current_idx + 1) % self.num_agents
        self.agent_selection = self._agent_selector.next()
        self.current_actions[current_idx] = action

        if next_idx == 0:
            self.steps += 1
            self._execute_world_step()
            status = self._episode_status()
            for idx, agent in enumerate(self._index_map.keys()):
                self.terminations[agent] = status['terminations'][idx]
                self.truncations[agent] = status['truncations'][idx]  

        if self.render_mode == "human":
            self.render()

    def enable_render(self, mode="human"):
        if not self.renderOn and mode == "human":
            self.screen = pygame.display.set_mode(self.screen.get_size())
            self.renderOn = True

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        self.enable_render(self.render_mode)

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if self.render_mode == "human":
            self.draw()
            pygame.display.flip()
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def draw(self):
        # clear screen
        self.screen.fill((255, 255, 255))

        # update bounds to center around agent
        all_poses = [entity.state.p_pos for entity in self.world.entities]
        cam_range = np.max(np.abs(np.array(all_poses)))

        # update geometry and text positions
        text_line = 0
        for e, entity in enumerate(self.world.entities):
            # geometry
            x, y = entity.state.p_pos
            y *= (
                -1
            )  # this makes the display mimic the old pyglet setup (ie. flips image)
            x = (
                (x / cam_range) * self.width // 2 * 0.9
            )  # the .9 is just to keep entities from appearing "too" out-of-bounds
            y = (y / cam_range) * self.height // 2 * 0.9
            x += self.width // 2
            y += self.height // 2
            pygame.draw.circle(
                self.screen, entity.color * 200, (x, y), entity.radius * 350
            )  # 350 is an arbitrary scale factor to get pygame to render similar sizes as pyglet
            pygame.draw.circle(
                self.screen, (0, 0, 0), (x, y), entity.radius * 350, 1
            )  # borders
            assert (
                0 < x < self.width and 0 < y < self.height
            ), f"Coordinates {(x, y)} are out of bounds."

    def close(self):
        if self.renderOn:
            pygame.event.pump()
            pygame.display.quit()
            self.renderOn = False