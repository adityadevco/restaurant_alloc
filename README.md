# Metrius Eats — Reinforcement Learning Restaurant Simulator

An interactive desktop simulation that demonstrates reinforcement-learning agents managing a restaurant environment. The simulator visualizes restaurant tables, customers, kitchen activity, agent behaviour, and learning results.

## Algorithms included

- Q-Learning (default)
- Expected SARSA
- Actor-Critic
- Deep Q-Network (DQN)
- N-step Tree Backup

## Run locally

This is a **Pygame desktop application**. It needs Python 3.10+ and a graphical desktop session.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Project structure

| Path | Purpose |
| --- | --- |
| `main.py` | Starts the Pygame simulation |
| `agent.py` | Restaurant agent and algorithm selection |
| `expected_sarsa.py`, `actor_critic.py`, `dqn.py`, `n_step_tree_backup.py` | Reinforcement-learning implementations |
| `assets/` | Graphics used by the simulator |
| `pdf_report.py` | Exports simulation reports |

## Browser demo

The `web/` directory contains a no-install browser edition of the restaurant-allocation simulator. It is built with plain HTML, CSS, and JavaScript and is ready for Vercel deployment. It provides interactive group arrivals, selectable allocation policies, a live dining-floor view, and service metrics.

**Live demo:** https://restaurant-alloc-web.vercel.app

The original `main.py` Pygame application remains the full desktop version.

## Generated files

Python bytecode, local virtual environments, and generated PDF reports are deliberately excluded from version control. In particular, `assets/agent/.venv/` is a 785 MB local Windows environment and is not part of the project source.
