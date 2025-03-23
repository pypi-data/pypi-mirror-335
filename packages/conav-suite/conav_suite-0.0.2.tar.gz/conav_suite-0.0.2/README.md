# Cooperative Navigation Suite: A Testbed for Emergent Communication in Asymmetric Multi-Agent Systems

## Overview

**conav_suite** is a research platform for studying emergent communication protocols in cooperative multi-agent systems. Built as an extension of the [Multi-Agent Particle Environment (MPE)](https://pettingzoo.farama.org/environments/mpe/) from the [Farama Foundation](https://farama.org/), conav_suite provides a flexible testbed for developing and evaluating communication strategies between agents with asymmetric information.

### Key Features:

* **Asymmetric Information** : Aerial agents with global vision and ground agents with local perception
* **Diverse Scenarios** : Eight unique problem configurations with varying obstacle arrangements
* **Dynamic Environments** : Configurable obstacle placements and agent/goal positions
* **Communication Challenge** : No predefined communication protocol—agents must develop their own language
* **PettingZoo Compatible** : Follows the [PettingZoo](https://pettingzoo.farama.org/) API for easy integration

## Environment Description

In conav_suite, agents must navigate to goal positions while avoiding obstacles. The core challenge emerges from the asymmetric information structure:

* **Aerial Agent** : Has global visibility of all obstacles (both large and small)
* **Ground Agent** : Can only perceive small obstacles in its vicinity

Large obstacles are constrained to specific regions defined by each problem instance, while small obstacles can appear anywhere in the environment. Start and goal positions are placed outside the large obstacle regions.

The aerial agent must develop effective communication strategies to guide the ground agent safely to its goal, without a pre-defined communication protocol.

## Research Motivation

conav_suite draws inspiration from the  **Lewis Signaling Game** , a game-theoretic framework for studying the emergence of communication. The environment serves as a testbed for several open research questions:

* How do agents develop communication protocols without pre-defined structures?
* What makes communication efficient in asymmetric information settings?
* How do different environmental configurations affect emergent communication?
* Can agents develop context-dependent language and high-level directives?

These questions have applications in robotics, autonomous systems coordination, human-AI interaction, and fundamental understanding of communication emergence.

## Installation

### From PyPI

```bash
pip install conav-suite
```

### From Source

```bash
git clone https://github.com/ethanmclark1/conav_suite.git
cd conav_suite
pip install -e .
```

### Dependencies

Required packages are automatically installed with the above methods, but can also be installed manually:

```bash
conda env create -f environment.yml
```

## Usage

### Basic Example

```python
import conav_suite

# Create environment
env = conav_suite.env()

# Reset environment with a specific problem instance
env.reset(options={'problem_instance': 'bisect'})

# Get initial observation
observation, reward, termination, truncation, info = env.last()

# Take a step in the environment
action = env.action_space(env.agent_selection).sample()  # Replace with your agent's policy
env.step(action)

# Close environment when done
env.close()
```

### Problem Instances

conav_suite offers eight distinct problem configurations that define constraint regions for large obstacle placement:

| Problem Instance |                 Visualization                 |
| :--------------: | :--------------------------------------------: |
|    ``bisect``    | ![1691433763627](image/README/1691433763627.png) |
|    ``circle``    | ![1691433778699](image/README/1691433778699.png) |
|  ``corners``   | ![1691433832902](image/README/1691433832902.png) |
|    ``cross``    | ![1691433961564](image/README/1691433961564.png) |
|  ``staggered``  | ![1691433856331](image/README/1691433856331.png) |
|   ``quarters``   | ![1691433864962](image/README/1691433864962.png) |
|  ``stellaris``  | ![1691433878432](image/README/1691433878432.png) |
|   ``scatter``   | ![1691433899914](image/README/1691433899914.png) |

******Note:****** The red regions in these visualizations represent areas where large obstacles can appear. Agents, goals, and small obstacles can be placed in any non-red area. This creates distinct navigational challenges across different problem instances, as the aerial agent must effectively communicate the locations of large obstacles (which only it can see) to the ground agent.

## API Reference

conav_suite follows the [PettingZoo](https://pettingzoo.farama.org/content/basic_usage/) API. Here are the key components:

### Environment Creation

```python
env = conav_suite.env()
```

### Environment Configuration Options

```python
env = conav_suite.env(
    num_agents=1,                  # Number of ground agents
    num_large_obstacles=4,         # Number of large obstacles
    large_obstacle_radius=0.05,    # Size of large obstacles
    num_small_obstacles=10,        # Number of small obstacles
    small_obstacle_radius=0.02,    # Size of small obstacles
    render_mode=None,              # None, "human", or "rgb_array"
    max_cycles=100                 # Maximum steps per episode
)
```

### Agent Observations

* **Ground Agent** : Position (2), goal position (2), other agent positions (2 × num_agents-1), small obstacle positions (2 × num_small_obstacles)
* **Aerial Agent** : Full state observation of all entities

For more details, refer to the [PettingZoo API documentation](https://pettingzoo.farama.org/content/basic_usage/).

## Contributing

We welcome contributions to conav_suite! You can contribute in several ways:

* **Bug Reports** : If you discover a bug, please submit a report via the issues tab with a detailed description and, if possible, a code sample.
* **Feature Requests** : Have ideas to improve conav_suite? Post your suggestions in the issues tab with a detailed explanation.
* **Pull Requests** : Made enhancements? Submit a pull request! We appreciate all help to make conav_suite better.

## Support

If you encounter issues or have questions, please:

1. Create an issue in the [GitHub repository](https://github.com/ethanmclark1/conav_suite/issues)
2. Contact me directly at [eclark715@gmail.com](mailto:eclark715@gmail.com)

## License

conav_suite is open-source software licensed under the [MIT license](https://claude.ai/chat/LICENSE).

### Related Work

Our environment builds upon these foundational works:

```bibtex
@article{lowe2017multi,
  title={Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments},
  author={Lowe, Ryan and Wu, Yi and Tamar, Aviv and Harb, Jean and Abbeel, Pieter and Mordatch, Igor},
  journal={Neural Information Processing Systems (NIPS)},
  year={2017}
}

@article{mordatch2017emergence,
  title={Emergence of Grounded Compositional Language in Multi-Agent Populations},
  author={Mordatch, Igor and Abbeel, Pieter},
  journal={arXiv preprint arXiv:1703.04908},
  year={2017}
}
```
