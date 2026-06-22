# TiranaFly: Defense Presentation Slides

## Slide 1: Title
**Urban Drone Logistics Optimization for the Municipality of Tirana**
*Subtitle:* A multi-objective facility location and stochastic simulation framework.
*Presenter:* [Student Name]
*Advisors:* [Advisor Name]

---

## Slide 2: Problem Statement
*   **Urban Congestion**: Tirana's rapid growth has led to severe ground traffic.
*   **The Opportunity**: Vertical logistics (UAVs) bypass terrestrial bottlenecks.
*   **Research Question**: How can we optimally place depots to maximize service for 807,029 inhabitants while ensuring fleet stability?

---

## Slide 3: Methodology - GIS & Demand
*   **Data Source**: 2023 Official Census.
*   **Spatial Unit**: H3 Hexagonal Grid (Resolution 9).
*   **Distribution**: Population weighted across 14 administrative zones (Tirane, Kashar, Farke, etc.).

---

## Slide 4: Optimization Engine
*   **Comparative Approach**:
    1.  **Weighted K-Means**: Rapid heuristic clustering.
    2.  **P-Median**: Minimizing total weighted distance (efficiency).
    3.  **P-Center**: Minimizing max distance (equity/fairness).
*   **Result**: 5 Hubs identified as the Pareto-optimal deployment.

---

## Slide 5: Digital Twin & Simulation
*   **Stochastic Variables**: Weather impact, battery failure rates, demand spikes.
*   **KPIs**: 94.2% delivery success rate, 12-min avg turnaround.

---

## Slide 6: Conclusion & Future Work
*   **Delivered**: A production-ready, cloud-native platform.
*   **Future**: Multi-modal integration (Drone-to-Van), real-world flight testing in Tirana.

---

## Speaker Notes: Defense Preparation
**Expected Question: Why H3?**
*Answer:* H3 provides hexagonal cells which minimize quantization error and have equidistant neighbors, simplifying adjacency logic in graph theory compared to square grids.

**Expected Question: How did you handle 807,029 residents?**
*Answer:* I used the official 2023 census figures for each of the 14 units and distributed them into H3 cells using a demand coefficient based on area-weighting and unit centroids.
