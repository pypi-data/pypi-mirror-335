# Dynamic Hierarchical Cooperative Swarm Algorithm (DHCS)

## Overview

The **Dynamic Hierarchical Cooperative Swarm Algorithm (DHCS)** is a novel optimization technique inspired by swarm intelligence. The algorithm involves agents that adapt their roles dynamically to balance exploration and exploitation in high-dimensional optimization landscapes. The agents cooperate by forming clusters, sharing solutions, and periodically synchronizing to avoid stagnation.

This approach is particularly effective for solving complex optimization problems such as the **Ackley function**.

- Refer [DOMCUMENT](DOCUMENT.md) to know more.

## Features

- **Dynamic Agent Roles**: Agents take on different roles such as explorers, refiners, and leaders based on their performance.
- **Memory Sharing**: Agents maintain and share high-quality solutions to improve convergence.
- **Dynamic Clustering**: Agents form clusters based on proximity and fitness, with cluster leaders guiding others.
- **Synchronization**: Periodic synchronization of agents’ positions and velocities to prevent divergence.

## Algorithm Details

1. **Agent Behavior**: Agents explore, exploit, and lead other agents to find optimal solutions.
2. **Memory and Role Adaptation**: Agents store their best-found solutions and adapt their roles based on fitness improvement.
3. **Cluster Formation**: Agents are grouped based on proximity and fitness, with the best agent becoming a leader.
4. **Synchronization**: Agents are synchronized if no significant improvement occurs for a set number of iterations.

## Requirements

To run this algorithm, the following Python packages are required:

- `numpy` (for numerical operations)
- `matplotlib` (for plotting the convergence history)
- `random` (for generating random values)
- `time` (for measuring execution time)

You can install the necessary dependencies using `pip`:

```bash
pip install numpy matplotlib
```

## Usage

1. Install via pip:

```python
pip install dhcs_algorithm
```

## License Terms

MIT License

Copyright (c) [2025] [Krishna Bajpai]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Usage

Until permission is granted, this software should not be used, distributed, or modified.


### Terms of Use:
- The use of this algorithm is restricted to specific permissions granted by the owner.
- Any usage outside of these permissions is prohibited.

For permission to use or modify this algorithm, please contact bajpaikrishna715@gmail.com.

## Acknowledgements

This work is based on ideas from swarm intelligence and optimization techniques. Special thanks to the community for contributing to the development of optimization algorithms and mathematical models.

## Contact

For any inquiries or further information, please contact the author at bajpaikrishna715@gmail.com.

