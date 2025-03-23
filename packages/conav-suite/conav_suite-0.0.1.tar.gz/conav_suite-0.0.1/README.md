# An Extension of Multi-Agent Particle Environment

conav_suite is an enhancement on top of the Simple environment, originally developed by the [Farama Foundation](https://farama.org/) as part of their [Multi-Agent Particle Environment (MPE)](https://pettingzoo.farama.org/environments/mpe/).

# conav_suite

conav_suite is an open-source research project aimed at advancing the development of communication strategies in multi-agent systems. The project proposes a unique environment that emphasizes the principles of the Lewis signaling game. This distinct setting serves as a testing ground for advancing robot-to-robot communication protocols.

Each problem set within conav_suite introduces different constraints on entity positioning such as start points, goals, and obstacles. This dynamic aspect encourages the investigation of communication strategies in diverse settings, enhancing the environment's adaptability and realism.

A notable characteristic of conav_suite is its incorporation of asymmetric information, whereby two types of agents – an 'eye in the sky' agent with global information and ground agents with only local information – operate simultaneously. This asymmetry replicates real-world situations, presenting challenges for the development of efficient communication strategies. It also provides intriguing prospects for the generation of context-dependent language and high-level directives.

For additional information on utilizing the environment API, please refer to the [PettingZoo API documentation](https://pettingzoo.farama.org/content/basic_usage/).

## Installation

```
git clone https://github.com/ethanmclark1/conav_suite.git
cd conav_suite
pip install -r requirements.txt
pip install -e .
```

## Usage

```
import conav_suite

env = conav_suite.env()
env.reset(options={'problem_instance': 'bisect'}))
observation, _, terminations, truncations, _ = env.last()
env.step(action)
env.close()
```

## List of Problem Instances

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

The red zones denote regions where large obstacles can be spawned, while the remaining space designates areas eligible for agent deployment, goal placement, and generation of small obstacles.

## Contributing

We welcome contributions to conav_suite! If you're interested in contributing, you can do so in the following ways:

* **Bug Reports** : If you discover a bug when using conav_suite, please submit a report via the issues tab. When submitting an issue, please do your best to include a detailed description of the problem and a code sample, if applicable.
* **Feature Requests** : If you have a great idea that you think would improve conav_suite, don't hesitate to post your suggestions in the issues tab. Please be as detailed as possible in your explanation.
* **Pull Requests** : If you have made enhancements to conav_suite, please feel free to submit a pull request. We appreciate all the help we can get to make conav_suite better!

## Support

If you encounter any issues or have questions about conav_suite, please feel free to contact us. You can either create an issue in the GitHub repository or reach out to us directly at [eclark715@gmail.com](mailto:eclark715@gmail.com).

## License

conav_suite is open-source software licensed under the [MIT license](https://chat.openai.com/LINK_TO_YOUR_LICENSE).

## Paper Citation

If you used this environment for your experiments or found it helpful, consider citing the following papers:

Environments in this repo:

<pre>
@article{lowe2017multi,
  title={Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments},
  author={Lowe, Ryan and Wu, Yi and Tamar, Aviv and Harb, Jean and Abbeel, Pieter and Mordatch, Igor},
  journal={Neural Information Processing Systems (NIPS)},
  year={2017}
}
</pre>

Original particle world environment:

<pre>
@article{mordatch2017emergence,
  title={Emergence of Grounded Compositional Language in Multi-Agent Populations},
  author={Mordatch, Igor and Abbeel, Pieter},
  journal={arXiv preprint arXiv:1703.04908},
  year={2017}
}
</pre>
