# Article Idea: Deep Reinforcement Learning for Routing and Spectrum Allocation in Elastic Optical Networks (EON)

## Important note about reproducibility in this environment
The requested upstream code repository (`assantos/eon_simulator`) could not be downloaded from this execution environment due to network restrictions (HTTP 403 on GitHub access). Therefore, the figures in this folder are **illustrative placeholders** built from synthetic-but-realistic values, intended to help you structure the paper quickly. Replace the CSV data with real simulation outputs from `eon_simulator` once run in your environment.

## Proposed title
**Learning to Route in Elastic Optical Networks: A Deep Reinforcement Learning Benchmark Against Heuristic Baselines**

## Research objective
Design and evaluate DRL-based RSA (Routing and Spectrum Allocation) policies for EONs and compare them to classical heuristics (e.g., First-Fit / shortest-path variants) across increasing traffic loads.

## Candidate contributions
1. A DRL formulation of dynamic RSA in EON under realistic arrival/departure traffic.
2. A unified benchmark protocol with common topology, traffic matrix, and load sweep.
3. Comparative analysis of DQN and PPO against deterministic heuristics.
4. Discussion of operational trade-offs: lower blocking vs. higher utilization and policy complexity.

## Suggested experimental setup
- **Environment**: EON simulator with k-shortest paths and contiguous spectrum slot constraints.
- **State**: link occupancy map, candidate path lengths, slot fragmentation indicators, request bitrate/class.
- **Action**: select (path, slot block) assignment or reject.
- **Reward**:
  - `+1` accepted request,
  - `-1` blocked request,
  - small penalty for long paths and fragmentation.
- **Methods compared**:
  - DQN-EON,
  - PPO-EON,
  - Heuristic-FF baseline.
- **Load sweep**: 80 to 160 Erlangs.

## Result figures included (illustrative)
Core performance:
1. **Blocking Probability vs. Traffic Load**  
   `figures/blocking_probability_vs_load.svg`
2. **Spectrum Utilization vs. Traffic Load**  
   `figures/spectrum_utilization_vs_load.svg`
3. **Service Acceptance vs. Traffic Load**  
   `figures/service_acceptance_vs_load.svg`
4. **Average Reward vs. Traffic Load**  
   `figures/avg_reward_vs_load.svg`

Comparative/diagnostic:
5. **Blocking Reduction over Heuristic-FF (%)**  
   `figures/blocking_improvement_over_heuristic.svg`
6. **Service Acceptance at Peak Load (bar chart)**  
   `figures/acceptance_at_peak_load.svg`
7. **Blocking Probability Heatmap (Method × Load)**  
   `figures/blocking_heatmap.svg`

Learning dynamics:
8. **Training Convergence (Reward vs. Episode)**  
   `figures/training_convergence.svg`
9. **Smoothed Training Convergence (window=3)**  
   `figures/training_convergence_smoothed.svg`

## How to replace with real simulator outputs
1. Run `eon_simulator` experiments for each method and load value.
2. Export metrics to CSV with the same columns as `data/illustrative_results.csv`.
3. Export training rewards with same columns as `data/illustrative_training_curve.csv`.
4. Re-run:

```bash
python3 article_idea/generate_graphs.py
```

## Suggested article outline
1. **Introduction**: Motivation for DRL in EON control loops.
2. **Related Work**: Heuristic RSA and ML-based network control.
3. **Problem Formulation**: MDP for dynamic RSA.
4. **Methodology**: Architectures, hyperparameters, reward shaping.
5. **Experimental Protocol**: Topology, traffic generation, evaluation metrics.
6. **Results and Discussion**: Blocking, utilization, convergence, generalization.
7. **Ablation Study**: reward terms, state encoding, action masking.
8. **Conclusion and Future Work**: transfer learning across topologies, online adaptation.

## Draft abstract (starter)
Elastic Optical Networks (EONs) require fast and adaptive Routing and Spectrum Allocation (RSA) under dynamic traffic and strict spectrum continuity/contiguity constraints. This paper investigates deep reinforcement learning (DRL) as a policy-learning paradigm for online RSA and benchmarks two families of agents, DQN and PPO, against heuristic baselines. We formulate dynamic RSA as a Markov Decision Process with a state representation that captures spectrum occupancy, fragmentation, and request-level traffic features. Experiments across increasing offered load show that DRL policies reduce blocking probability and sustain higher acceptance rates than classical heuristics while maintaining competitive spectrum utilization. We analyze training convergence, discuss computational overheads, and identify operating regions where learned policies provide the strongest gains. The findings suggest DRL is a practical direction for autonomous EON control when combined with constrained action spaces and robust offline training.
