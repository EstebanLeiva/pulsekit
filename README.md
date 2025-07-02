<p align="center">
  <img src="docs/assets/logo.png" alt="pulsekit logo" width="250"/>
</p>

<h1 align="center">pulsekit</h1>
<p align="center">
  <em>Solve deterministic and stochastic shortest paths using the Pulse algorithm.</em>
</p>

<p align="center">
  <!-- Update badges once the repo is public / CI is set up -->
  <img alt="PyPI" src="https://img.shields.io/pypi/v/pulse-kit?style=flat-square">
  <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/your-username/pulsekit/ci.yml?style=flat-square">
  <img alt="License" src="https://img.shields.io/github/license/your-username/pulsekit?style=flat-square">
</p>

---

## Why Pulse?

Classical shortest path algorithms struggle with **multiple constraints** or **stochastic arc costs**.  
The Pulse algorithm tackles these challenges by combining:

* **Depth-first search** over a **label-pruned space**  
* **Dominance rules** and **bounds** to discard infeasible paths early  
* Flexibility to support **multi-objective**, **resource-constrained**, and **stochastic** variants

With **pulsekit** you can:

* Solve deterministic and stochastic shortest path problems.
* Handle time windows, risk constraints, and multi-resource bounds.
* Extend and adapt the pulse strategy for your own use cases.

---

## Installation

```bash
pip install pulsekit            # from PyPI (coming soon)
# or, for development:
git clone https://github.com/your-username/pulsekit
cd pulsekit
pip install -e .
