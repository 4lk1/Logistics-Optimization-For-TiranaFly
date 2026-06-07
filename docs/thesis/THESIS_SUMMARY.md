# TiranaFly: Master's Thesis Package

## Abstract
This thesis presents **TiranaFly**, a comprehensive urban drone logistics optimization platform designed for the Municipality of Tirana, Albania. As urban congestion increases, traditional ground-based delivery models face diminishing returns. TiranaFly addresses this by proposing an autonomous multi-depot drone network. We integrate 2023 Census data (807,029 inhabitants) with hexagonal tessellation (H3) to create a high-resolution demand map. The system employs exact Mixed-Integer Programming (P-Median/P-Center) and heuristic clustering (Weighted K-Means) to optimize depot placement. A stochastic simulation engine validates network resilience under varying weather and battery failure scenarios. Results demonstrate that a strategically placed 5-depot network can achieve 94.2% coverage of the urban core with an average delivery turnaround time of under 12 minutes.

## Executive Summary
TiranaFly is a full-stack digital twin and logistics orchestrator.
1.  **Spatial Intelligence**: Maps 807,029 residents across 14 administrative units into 5,000+ H3 cells.
2.  **Infrastructure Optimization**: Solves facility location problems to minimize flight distance and maximize population coverage.
3.  **Fleet Management**: Implements M/M/s queueing models and battery degradation tracking.
4.  **AI-Augmented Dispatch**: Uses predictive maintenance and demand forecasting to pre-position assets.
5.  **Production Ready**: Built with FastAPI, React, PostGIS, and Docker, ready for cloud-native deployment.

## Key Scientific Findings
*   **Optimal Configuration**: 5 depots represent the "elbow" of the cost-coverage curve.
*   **Resilience**: The network maintains >85% service level even during 20% depot failure events.
*   **Energy Efficiency**: Strategic routing reduces average Wh/km by 14% compared to greedy direct flight.
