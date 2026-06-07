# TiranaFly: Mathematical Appendix

## 1. Population & GIS Model
### 1.1 Hexagonal Tessellation (H3)
The study area $\Omega \subset \mathbb{R}^2$ (Tirana Municipality) is partitioned into a set of hexagonal cells $\mathcal{H} = \{h_1, h_2, \dots, h_n\}$ using the H3 discrete global grid system at resolution $r$.

### 1.2 Population Distribution
Let $P_{unit}$ be the total population of an administrative unit $U$. The local demand coefficient $\delta_i$ for a cell $h_i \in U$ is distributed such that:
$$\sum_{h_i \in U} \delta_i = 1$$
The absolute population of cell $h_i$ is $p_i = \delta_i \cdot P_{total}$, where $P_{total} = 807,029$.

## 2. Optimization Models
### 2.1 P-Median Problem (Minisum)
Objective: Minimize the total weighted distance between demand cells and the nearest open depot.
$$\text{minimize } Z = \sum_{i \in \mathcal{H}} \sum_{j \in \mathcal{J}} p_i \cdot d_{ij} \cdot x_{ij}$$
Subject to:
1. $\sum_{j \in \mathcal{J}} x_{ij} = 1 \quad \forall i \in \mathcal{H}$ (Each cell assigned to one depot)
2. $x_{ij} \leq y_j \quad \forall i \in \mathcal{H}, j \in \mathcal{J}$ (Assignment only to open depots)
3. $\sum_{j \in \mathcal{J}} y_j = p$ (Exactly $p$ depots opened)
4. $x_{ij}, y_j \in \{0, 1\}$

### 2.2 P-Center Problem (Minimax)
Objective: Minimize the maximum distance between any demand cell and its assigned depot.
$$\text{minimize } Z = \max_{i \in \mathcal{H}} \{ d_{i, \text{assigned}(i)} \}$$

## 3. Fleet & Queueing Model
### 3.1 M/M/s Queueing System
Each depot $j$ is modeled as an $M/M/s$ queue where:
*   $\lambda_j$: Arrival rate of delivery requests (Poisson process).
*   $\mu_j$: Service rate per drone (Exponential distribution).
*   $s_j$: Number of drones allocated to depot $j$.

The utilization factor $\rho_j = \frac{\lambda_j}{s_j \mu_j}$ must satisfy $\rho_j < 1$ for system stability.

## 4. Energy Model
The power $P$ required for a drone of mass $m$ to maintain steady level flight at speed $v$ is:
$$P(v) = \frac{1}{2} \rho v^3 S C_D + \frac{(mg)^2}{\rho v b^2 e \pi}$$
where $\rho$ is air density, $S$ is wing area, $C_D$ is drag coefficient, and $b$ is wingspan.
Total energy consumed for a path of distance $D$ is $E = P(v) \cdot \frac{D}{v}$.
