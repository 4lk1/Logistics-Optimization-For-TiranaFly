# TiranaFly: Population-Aware Drone Logistics Optimization for the Municipality of Tirana

## Phase 1: Project Foundation & Research Problem

This document outlines the foundational framework for TiranaFly. Subsequent phases will build upon this basis, expanding into spatial modeling, graph theory, optimization, and simulation.

**Inputs from Previous Phases:**
*   None (This is the foundational phase).

**Outputs to Future Phases:**
*   Problem Framework and Research Questions.
*   System Objectives and Defined Scope.
*   Initial Assumptions and Notation.

---

## 1. Project Introduction

**TiranaFly** is a comprehensive, population-aware computational platform designed to optimize drone-based logistics within the Municipality of Tirana, Albania. As the city experiences rapid urban expansion, traditional ground-based logistics face increasing challenges due to heavy congestion, intricate topographic features, and infrastructure limitations. 

TiranaFly addresses these challenges by integrating advanced **Operations Research (OR)**, **Graph Theory**, **Geographic Information Systems (GIS)**, and **Digital Twin Simulation**. The platform aims to move beyond simple routing by incorporating dynamic population density models (utilizing H3 hexagonal tessellation) and real-time operational constraints such as drone battery degradation and demand forecasting.

## 2. Project Vision

TiranaFly aims to serve as the backbone for the next generation of smart urban logistics in Tirana. Our vision is to develop a sustainable, resilient, and highly efficient delivery network that significantly reduces the city's carbon footprint, decreases last-mile delivery times, and improves the overall quality of life for Tirana's 807,029 inhabitants. 

The project seeks to bridge the gap between theoretical optimization models and real-world urban infrastructure, providing a scalable blueprint for other rapidly growing urban centers.

## 3. Problem Definition

Tirana’s urban landscape presents unique logistical difficulties:
*   **Infrastructure & Congestion:** Dense, historic center infrastructure combined with rapid suburban growth creates significant bottlenecks for traditional delivery fleets.
*   **Topographic Constraints:** The city’s hilly terrain significantly impacts the energy efficiency of battery-powered aerial vehicles.
*   **Demand Concentration:** Population density is highly heterogeneous, with significant disparities between administrative units ($\mathcal{U}$).
*   **Battery and Payload Constraints:** Drones are inherently limited by their energy capacity and maximum payload. Optimizing routes requires balancing these limitations against urgent, geographically distributed demand.

## 4. Research Questions

To address these challenges, TiranaFly poses the following research questions:
1.  **Spatial Modeling:** How can we accurately map urban demand using hexagonal tessellation (H3) to reflect population-weighted delivery needs?
2.  **Facility Location:** How do we optimally place drone depots to maximize coverage while minimizing infrastructure costs?
3.  **Dynamic Routing:** What algorithmic approaches best balance drone energy constraints ($\mathcal{E}$) against time-sensitive delivery requirements?
4.  **Resilience & AI:** How can AI-driven predictive maintenance and demand forecasting improve the long-term reliability of the logistics network?

## 5. Project Objectives

### Scientific Objectives
*   Develop novel algorithms for facility location and drone routing in non-Euclidean urban spaces.
*   Create a hybrid model integrating Queueing Theory with Operations Research for drone dispatching.

### Engineering Objectives
*   Build a scalable cloud-based infrastructure (utilizing `api/`, `backend/`, and `fleet/` modules).
*   Implement a high-fidelity Digital Twin simulation (`simulation/` layer) to validate logistics strategies before physical implementation.

### Business & Operational Objectives
*   Minimize total operational cost per delivery ($C_{delivery}$).
*   Maximize network coverage, ensuring that at least 95% of the population within $\mathcal{U}$ is reachable.

## 6. Project Scope

### Included Functionality
*   Theoretical modeling of demand and facility location.
*   Simulation and optimization engines.
*   Digital Twin environment for stress testing.

### Excluded Functionality
*   Physical manufacturing of drone hardware.
*   Real-world drone fleet deployment or active flight operations.
*   Legislative/regulatory legal advocacy.

### Assumptions & Constraints
*   **Population:** $\mathcal{P}_{total} = 807,029$ across 14 Administrative Units.
*   **Geometry:** The municipality is approximated via H3 hexagonal tessellation.
*   **Energy:** Drones are limited by fixed battery capacities, with energy consumption modeled as a function of payload and slope.

---

## Phase 2: Datasets, Census & Population Model

**Inputs from Previous Phases:**
*   Foundational Framework (Phase 1)
*   Assumption: Total Population $\mathcal{P}_{total} = 807,029$ (Phase 1)

**Outputs to Future Phases:**
*   Population Model per Administrative Unit ($\mathcal{P}_i$)
*   Demand Conversion Model ($\mathcal{D}_i = f(\mathcal{P}_i)$)
*   Used later by: GIS Tessellation (Phase 3) and Optimization Layer (Phase 5).

---

## 1. Data Sources

The accuracy of TiranaFly relies on the integration of high-resolution spatial and demographic datasets:

*   **Demographic Data:** 2023 Census data aggregated from official municipal records and validated against CityPopulation.de for temporal consistency.
*   **Administrative Units:** Official municipal boundary definitions for the 14 Administrative Units comprising the Municipality of Tirana.
*   **Geospatial Data:** OpenStreetMap (OSM) for infrastructure mapping, elevation data (SRTM) for topographic modeling, and H3 hierarchical spatial index for tessellation.

## 2. Population Model

The Municipality of Tirana comprises 14 distinct Administrative Units ($\mathcal{U} = \{U_1, U_2, \dots, U_{14}\}$). The population is distributed heterogeneously across these units.

### 2.1 The Distinction: 807,029 vs. 598,176
A common ambiguity in urban data is the distinction between the "Municipality" population and the "City Proper" (urban core). 
*   **$\mathcal{P}_{municipality} = 807,029$**: This is the administrative total population encompassing all 14 units, including suburban and rural areas recently integrated.
*   **$\mathcal{P}_{city\_proper} = 598,176$**: This figure represents the concentrated urban core within the historical boundary.

For TiranaFly, we exclusively use $\mathcal{P}_{municipality} = 807,029$ to ensure full network coverage, including outlying suburban districts.

### 2.2 Mathematical Proof and Conservation
Let $\mathcal{P}_i$ be the population of administrative unit $U_i$. Population conservation mandates:
$$\sum_{i=1}^{14} \mathcal{P}_i = \mathcal{P}_{total} = 807,029$$

Normalization of demand share ($\mathcal{S}_i$) for unit $U_i$ is defined as:
$$\mathcal{S}_i = \frac{\mathcal{P}_i}{\mathcal{P}_{total}}$$
$$\sum_{i=1}^{14} \mathcal{S}_i = 1$$

This ensures that all logistics requests are proportional to population concentration.

## 3. Demand Model

We model delivery demand ($\mathcal{D}_i$) for unit $U_i$ as a linear function of population, scaled by a factor $\alpha$ representing the average daily delivery propensity per capita:
$$\mathcal{D}_i = \alpha \cdot \mathcal{P}_i$$

*   **$\alpha$ (Demand Propensity):** A calibrated constant reflecting daily delivery rates (e.g., $0.005$ deliveries/capita/day).
*   **Constraints:** Demand is strictly non-negative ($\mathcal{D}_i \geq 0$) and subject to temporal variation $\mathcal{D}_i(t)$.

---

## Phase 3: GIS, Geometry & Spatial Modeling

**Inputs from Previous Phases:**
*   Population Model ($\mathcal{P}_i$) (Phase 2)
*   Administrative Boundary Data (Phase 2)

**Outputs to Future Phases:**
*   Hexagonal Tessellation Grid (H3)
*   Spatial Demand Distribution ($\mathcal{D}_{cell}$)
*   Used later by: Graph Builder (Phase 4) and Facility Location Optimizer (Phase 5).

---

## 1. Spatial Infrastructure

TiranaFly utilizes robust geospatial standards to maintain data integrity and interoperability:

*   **Coordinate Systems:** All spatial data is projected using the WGS84 (EPSG:4326) reference system for global alignment.
*   **Data Formats:** Feature data is stored in GeoJSON format to facilitate seamless integration with web-based visualization tools and backend services.
*   **PostGIS:** We utilize PostGIS, the spatial database extension for PostgreSQL, to perform high-performance spatial queries, boundary intersections, and distance calculations.

## 2. Hexagonal Tessellation (H3)

To move beyond arbitrary administrative boundaries, TiranaFly discretizes the city using Uber’s H3 hierarchical hexagonal spatial index.

### 2.1 Justification for Hexagons
Hexagons are superior to square grids and traditional polygons for urban modeling for several mathematical reasons:
*   **Uniform Adjacency:** Each hexagon has exactly six equidistant neighbors, simplifying graph construction.
*   **Reduced Quantization Error:** Hexagons more closely approximate circles than squares, reducing edge effects in distance-based optimization.
*   **Hierarchical Structure:** H3 allows for seamless aggregation and disaggregation of data across different zoom levels, essential for multi-scale analysis.

### 2.2 Comparison

| Feature | Hexagons (H3) | Square Grid | Voronoi Polygons |
| :--- | :--- | :--- | :--- |
| **Connectivity** | Uniform (6) | Variable (4/8) | Variable |
| **Distance Uniformity** | High | Low (Corners) | Low |
| **Hierarchical Scaling** | Yes | Limited | No |

### 2.3 Tessellation Workflow
1.  **Boundary Ingestion:** Import administrative unit boundaries from GeoJSON/PostGIS.
2.  **Grid Generation:** Generate H3 cells at a resolution (e.g., Res 9) providing optimal granularity for drone service radius.
3.  **Spatial Join:** Intersect the H3 grid with administrative boundaries to allocate population ($\mathcal{P}_i$) to individual hexagonal cells ($\mathcal{P}_{cell}$).
4.  **Demand Mapping:** Populate each cell with demand ($\mathcal{D}_{cell} = \alpha \cdot \mathcal{P}_{cell}$), creating the input for the Graph Theory layer.

---

## Phase 4: Graph Theory & Routing Engine

**Inputs from Previous Phases:**
*   Hexagonal Tessellation Grid (H3) (Phase 3)
*   Spatial Demand Distribution ($\mathcal{D}_{cell}$) (Phase 3)

**Outputs to Future Phases:**
*   Route Cost Matrix ($\mathcal{C}$)
*   Optimized Flight Paths
*   Used later by: Facility Location Optimizer (Phase 5) and Dispatch Engine (Phase 7).

---

## 1. Graph Model

We formalize Tirana’s logistics network as a directed weighted graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{W})$.

*   **Vertices ($\mathcal{V}$):** Each H3 cell center constitutes a vertex $v \in \mathcal{V}$.
*   **Edges ($\mathcal{E}$):** A directed edge $(u, v) \in \mathcal{E}$ exists between adjacent hexagonal cells.
*   **Weights ($\mathcal{W}$):** Each edge has a weight $w(u, v) \in \mathcal{W}$ representing the cost of traversing the edge. This cost is a function of Euclidean distance, terrain elevation changes (slope $\theta$), and drone energy consumption ($\mathcal{E}_{cons}$).

### 1.1 Pruning
To ensure computational efficiency, the graph is pruned by removing cells/edges exceeding maximum flight distance constraints or passing through restricted airspace zones (determined via GIS data).

## 2. Routing Algorithms

For route calculation between depot $s$ and destination $d$, we implement multiple algorithms to address different performance needs:

### 2.1 Dijkstra’s Algorithm
*   **Purpose:** Guarantees the shortest path in a graph with non-negative edge weights.
*   **Complexity:** $O(|\mathcal{E}| + |\mathcal{V}| \log |\mathcal{V}|)$ using a priority queue.
*   **Pros/Cons:** Robust and optimal; however, computationally intensive for large, dense graphs.

### 2.2 A* Search
*   **Purpose:** Efficiently finds the shortest path by incorporating a heuristic function $h(v)$ (e.g., Great Circle distance).
*   **Complexity:** $O(|\mathcal{E}|)$ in best-case scenarios, dependent on heuristic quality.
*   **Pros/Cons:** Significantly faster than Dijkstra due to search-space reduction; optimality requires a consistent, admissible heuristic.

### 2.3 Bidirectional Dijkstra
*   **Purpose:** Searches simultaneously from $s$ to $d$ and $d$ to $s$.
*   **Pros/Cons:** Reduces the search space by half, but requires complex stopping conditions.

### 2.4 Yen’s K-Shortest Paths
*   **Purpose:** Identifies the $k$ most efficient routes, useful for path redundancy and rerouting in case of dynamic failures (e.g., weather or battery depletion).

---

## Phase 5: Operations Research & Optimization

**Inputs from Previous Phases:**
*   Graph Model $\mathcal{G}=(\mathcal{V}, \mathcal{E}, \mathcal{W})$ (Phase 4)
*   Route Cost Matrix $\mathcal{C}$ (Phase 4)

**Outputs to Future Phases:**
*   Optimal Depot Locations
*   Allocated Demand Centers
*   Used later by: Digital Twin Simulation (Phase 6) and Dispatch Engine (Phase 7).

---

## 1. Facility Location Modeling

To determine the strategic placement of drone depots, TiranaFly employs several foundational Operations Research models.

### 1.1 P-Median Problem
The P-Median problem aims to locate $p$ facilities such that the total weighted distance from all demand nodes to their nearest facility is minimized.
*   **Decision Variables:** $x_{ij} = 1$ if node $i$ is assigned to facility at node $j$, 0 otherwise.
*   **Objective:** $\min \sum_{i \in \mathcal{V}} \sum_{j \in \mathcal{V}} w_i d_{ij} x_{ij}$
*   **Complexity:** NP-Hard.
*   **Application:** Best used when minimizing overall system delivery cost is the priority.

### 1.2 P-Center Problem
The P-Center problem minimizes the *maximum* distance any demand node must travel to its nearest facility (minimizing the "worst-case" scenario).
*   **Objective:** $\min (\max_{i \in \mathcal{V}} \min_{j \in \{facilities\}} d_{ij})$
*   **Application:** Essential for time-sensitive deliveries, ensuring strict service-level agreements (SLAs).

### 1.3 Set Cover Problem
The Set Cover problem aims to cover all demand nodes using the minimum number of facilities within a predefined distance threshold $R$.
*   **Objective:** $\min \sum_{j \in \mathcal{V}} y_j$
*   **Constraints:** $\sum_{j \in \mathcal{N}_i} y_j \geq 1, \forall i \in \mathcal{V}$ (where $\mathcal{N}_i$ are facilities within range $R$ of node $i$).
*   **Application:** Ensures complete network coverage given a fixed drone range constraint.

## 2. Model Selection & Formulation

We formulate these problems as Mixed-Integer Linear Programs (MILP), utilizing commercial-grade solvers (e.g., Gurobi/OR-Tools) to handle complexity. 

### Weighted K-Means
In addition to exact methods, we employ **Weighted K-Means** for rapid heuristic clustering of high-density demand zones.
*   **Rationale:** Provides a near-optimal initial solution (warm-start) for the MILP models, significantly reducing solver computation time.

---

## Phase 6: Drone Model & Fleet Optimization

**Inputs from Previous Phases:**
*   Facility Locations (Phase 5)
*   Spatial Demand Distribution ($\mathcal{D}_{cell}$) (Phase 3)

**Outputs to Future Phases:**
*   Optimal Fleet Size per Depot
*   Service Level Metrics
*   Used later by: Digital Twin Simulation (Phase 7).

---

## 1. Drone and Energy Model

Each drone in the TiranaFly fleet is modeled with defined physical and operational parameters.

### 1.1 Physical Characteristics
*   **Max Payload ($M_{payload}$):** 2.5 kg.
*   **Battery Capacity ($E_{cap}$):** 20,000 mAh (Nominal).
*   **Flight Speed ($v$):** Average cruising speed of 15 m/s.

### 1.2 Energy Consumption Derivation
Total energy consumption ($E_{total}$) for a flight is modeled as a function of distance ($d$), payload mass ($m$), and terrain slope ($\theta$):
$$E_{total} = \int_{0}^{T} (P_{hover} + P_{prop}(m, \theta)) dt$$
where $P_{prop}$ is the power required to overcome drag and gravitational forces during climb/descent.

### 1.3 Assumptions
*   Weather: Consistent wind speed profile $\vec{w}$ (modeled as a constant offset).
*   Battery: Linear degradation model based on charge cycles.

## 2. Queueing Theory for Fleet Sizing

To ensure demand is met without excessive over-provisioning, we model each depot as a multi-server queueing system.

### 2.1 Queueing Models
*   **M/M/1:** Single-drone depot, useful for isolated, low-demand suburban areas.
*   **M/M/c:** Multi-drone depot, where $c$ is the number of drones, used for high-demand urban centers.

### 2.2 Mathematical Framework
Let $\lambda$ be the arrival rate of delivery requests and $\mu$ be the service rate (flight time + loading time).
*   **Traffic Intensity ($\rho$):** $\rho = \frac{\lambda}{c\mu}$.
*   **Fleet Sizing ($c$):** We determine $c$ such that the probability of waiting time exceeding a threshold $W_{max}$ is below a defined tolerance level $\alpha$ ($P(W > W_{max}) < \alpha$).

### 2.3 Depot Balancing
Drones are dynamically reallocated between depots based on the variance in hourly demand $\mathcal{D}_i(t)$, ensuring service stability across the network.

---

## Phase 7: Software Architecture

**Inputs from Previous Phases:**
*   OR Optimization Models (Phase 5)
*   Queueing/Fleet Models (Phase 6)

**Outputs to Future Phases:**
*   Deployable System Infrastructure
*   Validation of Logic (Phase 8)

---

## 1. Overall System Architecture

TiranaFly follows a microservices-based, event-driven architecture to ensure scalability, modularity, and resilience. The system is designed to handle asynchronous data streams from GIS, optimization solvers, and real-time simulation engines.

### 1.1 Core Layers
*   **Frontend:** A web-based dashboard (React/TypeScript/Vite) providing spatial visualization (via `visualization/` and `maps.py`) and control of simulation parameters.
*   **Backend API:** FastAPI service (`api/`) managing system requests, authentication, and orchestration of services.
*   **GIS & Optimization Layer:** Dedicated services (`gis/`, `optimization/`) for spatial data processing, H3 grid management, and solving ILP facility location models.
*   **Simulation & AI Layer:** The Digital Twin (`simulation/`) and predictive maintenance/demand forecasters (`ai/`) which run asynchronously, communicating state via a message broker.
*   **DevOps Layer:** Containerized deployment (Docker, Kubernetes) managed by Terraform for infrastructure as code, ensuring automated scalability.

## 2. Data & Dependency Flow

The system exhibits a clear, directional dependency flow:
`GIS/Census` → `Spatial Grid (H3)` → `Graph Network (G)` → `Optimization (MILP)` → `Simulation/Fleet Mgmt`.

### 2.1 Component Interaction
1.  **Orchestrator:** `integration/system_orchestrator.py` manages the data pipeline.
2.  **State Management:** State is persisted in PostGIS and managed by internal services through a repository pattern.

## 3. Design Patterns
*   **Repository Pattern:** Used in `api/repositories/` to abstract database interactions (PostGIS).
*   **Orchestration Pattern:** Used in `integration/system_orchestrator.py` to coordinate inter-service dependencies.
*   **Service Pattern:** Core business logic (dispatch, optimization) is encapsulated in separate `services/` directories.

---

## Phase 8: Database Design & API

**Inputs from Previous Phases:**
*   Software Architecture (Phase 7)
*   Optimization & Fleet Models (Phase 5, 6)

**Outputs to Future Phases:**
*   System Validation via Digital Twin (Phase 9)

---

## 1. PostGIS Database Architecture

TiranaFly leverages PostgreSQL with the PostGIS extension as the primary source of truth for spatial data.

### 1.1 Schema Design & Relationships
*   **`administrative_units`**: Stores polygon boundaries of the 14 districts.
*   **`h3_cells`**: Maps spatial cells to units, containing population $\mathcal{P}_{cell}$ and demand $\mathcal{D}_{cell}$.
*   **`depots` & `drones`**: Entities mapping facility locations and fleet assets.
*   **`delivery_requests`**: Temporal data logging request location, status, and assignment.

### 1.2 Spatial Optimization
*   **Indexes:** GIST (Generalized Search Tree) indexes are applied to spatial geometries in `administrative_units` and `h3_cells` to facilitate sub-millisecond spatial join and intersection queries.
*   **Constraints:** Foreign key constraints maintain relational integrity between demand requests and facility assignments.

## 2. API Design (FastAPI)

The backend provides a RESTful interface using FastAPI, chosen for its asynchronous capability and built-in Pydantic data validation.

### 2.1 API Specification
*   **Authentication/Authorization:** JWT-based stateless authentication ensures secure access to sensitive optimization endpoints.
*   **Caching:** Redis caching is implemented for frequent spatial queries and pre-computed route cost matrices.
*   **Task Queues:** Celery (with Redis broker) handles long-running tasks like Digital Twin simulations and large-scale facility location optimization, preventing API request timeouts.

### 2.2 API Documentation Summary

| Endpoint | Method | Purpose | Auth Required |
| :--- | :--- | :--- | :--- |
| `/optimize/facility` | POST | Triggers facility location ILP solver | Yes |
| `/dispatch/simulate` | POST | Initiates Digital Twin simulation | Yes |
| `/data/population` | GET | Retrieves demographic data | No |
| `/routes/calculate` | GET | Computes path between $s$ and $d$ | No |

---

## Phase 9: Digital Twin & Simulation

**Inputs from Previous Phases:**
*   Optimized Network Structure (Phases 5, 6)
*   System Architecture (Phase 7)

**Outputs to Future Phases:**
*   Final System Validation
*   Operational Insights for Municipality

---

## 1. Digital Twin Simulation Engine

The Digital Twin is the final layer of TiranaFly, acting as a high-fidelity, stochastic environment to evaluate logistics strategies.

### 1.1 Monte Carlo Methodology
To account for real-world uncertainty, we run thousands of Monte Carlo simulations, sampling demand distributions $\mathcal{D}_i(t)$ and weather conditions $\vec{w}(t)$ to determine performance statistics.
*   **Justification:** Simulation is essential for capturing non-linear interactions (e.g., depot congestion, drone battery depletion) that cannot be perfectly modeled using closed-form OR methods.

### 2. Analysis & Testing

### 2.1 Stress Testing
We subject the network to extreme scenarios:
*   **Peak Demand:** Simulating holiday/event-based demand surges (e.g., $5\times$ base load).
*   **System Failure:** Simulating partial or total loss of depot/drone capability to test network resilience.

### 2.2 Failure & Sensitivity Analysis
*   **Sensitivity:** Analyzing how variations in input parameters (e.g., drone battery degradation rate) affect service levels.
*   **Failure Analysis:** Identifying the most critical system components (e.g., specific high-load depots) whose failure would lead to cascade network instability.
*   **Outcome:** Data-driven mitigation strategies, such as adding redundant depots or buffer fleet capacity.

---

## Phase 10: Artificial Intelligence

**Inputs from Previous Phases:**
*   Simulation Engine (Phase 9)
*   Historical Logistics Data (Phases 1-8)

**Outputs to Future Phases:**
*   System-wide operational efficiency gains
*   Proactive infrastructure maintenance

---

## 1. AI Component Suite

TiranaFly incorporates a comprehensive AI layer (`ai/`) to enhance the static optimization models with adaptive intelligence.

### 1.1 Predictive Modeling
*   **Demand Forecasting (`ai/demand_forecasting.py`):** Utilizes LSTM (Long Short-Term Memory) networks to predict spatio-temporal demand spikes based on historical census and delivery patterns.
*   **Battery Prediction (`ai/battery_prediction.py`):** Applies regression-based models to estimate remaining battery life, facilitating preemptive fleet management.
*   **Predictive Maintenance (`ai/predictive_maintenance.py`):** Uses classification algorithms (e.g., Random Forest) on telemetry data to predict drone component failures before they occur.

### 1.2 Adaptive Intelligence
*   **Anomaly Detection (`ai/anomaly_detection.py`):** Monitors live delivery flows using Isolation Forests to detect unusual events (e.g., unexpected delays or system errors).
*   **Reinforcement Learning (`ai/reinforcement_dispatch.py`):** Employs Deep Q-Learning (DQN) to optimize dynamic drone dispatching.
    *   **State:** Current depot load, pending demand, drone status.
    *   **Action:** Dispatch drone, reallocate drone, or schedule maintenance.
    *   **Reward:** Reduced latency, energy efficiency, and coverage.

## 2. Training and Evaluation

Each AI component follows a strict ML lifecycle:
1.  **Data Ingestion:** Aggregation from `PostGIS` and simulation logs.
2.  **Training:** Off-line training on historical datasets.
3.  **Deployment:** Integration into the backend via `model_registry.py` and `inference_service.py`.
4.  **Evaluation:** Continuous monitoring using metrics (RMSE for demand, Accuracy for failure detection) to trigger retraining.

---

## Phase 11: DevOps & Deployment

**Inputs from Previous Phases:**
*   Software Architecture (Phase 7)
*   Database & API Design (Phase 8)

**Outputs to Future Phases:**
*   Production Lifecycle Maintenance

---

## 1. Production Deployment Architecture

TiranaFly employs a modern containerized deployment pipeline designed for high availability and automated scaling.

### 1.1 Infrastructure Stack
*   **Containerization:** All services are packaged as Docker images.
*   **Orchestration:** Kubernetes (K8s) manages service deployment, scaling, and self-healing.
*   **Infrastructure as Code (IaC):** Terraform provisions cloud resources (VPC, EKS, RDS/PostGIS, Redis), ensuring infrastructure consistency and repeatability.

### 1.2 CI/CD Pipeline
*   **GitHub Actions:** Automates code linting, unit testing, image building, and deployment to the Kubernetes cluster on merge to the `main` branch.

## 2. Monitoring & Observability

To maintain reliability, the system implements a comprehensive observability stack:

### 2.1 The Observability Suite
*   **Prometheus:** Collects system metrics (CPU, RAM, request latency) from all microservices.
*   **Grafana:** Visualizes metrics, providing real-time operational dashboards for monitoring network health.
*   **Loki:** Aggregates logs across the system for efficient distributed tracing and debugging.

## 3. Security
*   **Secrets Management:** Sensitive configurations are injected via Kubernetes Secrets/Vault.
*   **Network Policies:** Zero-trust architecture enforced via Kubernetes network policies, limiting inter-service communication to authorized traffic only.
*   **Automated Scanning:** CI pipeline includes vulnerability scanning for Docker images.

---

## Phase 12: Results, Usage, Installation & Future Work

**Inputs from Previous Phases:**
*   All previous phases (1-11)

**Outputs to Future Phases:**
*   Final Project Deliverable

---

## 1. Performance Results & KPIs

TiranaFly’s effectiveness is measured against key performance indicators derived from the simulation environment:

### 1.1 Metrics
*   **Coverage:** Percentage of total population ($\mathcal{P}_{total}$) reachable within drone operational range.
*   **Energy Efficiency:** Ratio of energy consumed per unit distance ($E/d$).
*   **Fleet Utilization:** Ratio of active flight time vs. total available drone time.
*   **Latency:** Average time from request submission to arrival.

## 2. Installation & Usage Guide

### 2.1 Installation
1.  **Clone:** `git clone https://github.com/TiranaFly/Logistics-Optimization-For-TiranaFly.git`
2.  **Infrastructure:** Deploy infrastructure using Terraform: `cd devops/terraform && terraform apply`.
3.  **Application:** Build and deploy to Kubernetes: `kubectl apply -f devops/kubernetes/`.

### 2.2 Usage Examples
*   **API Optimization:** `POST /optimize/facility`
    *   *Payload:* `{ "num_depots": 10, "strategy": "p-median" }`
*   **Simulation Execution:** `POST /dispatch/simulate`
    *   *Payload:* `{ "scenario": "peak_demand", "duration": 24 }`

## 3. Future Directions, Limitations & Bibliography

### 3.1 Research & Commercialization
*   **Future Work:** Integration of real-time air traffic control (UTM) data and multi-modal delivery (e.g., truck-drone hybrids).
*   **Commercialization:** Licensing the platform to municipal authorities or logistics providers for urban planning and route optimization.

### 3.2 Limitations
*   Assumes static wind conditions and uniform battery degradation profiles.
*   Requires high-fidelity topographic data which may vary in resolution.

### 3.3 Academic Bibliography
*   *H3: Uber's Hexagonal Hierarchical Spatial Index.* (Uber Engineering).
*   *Operations Research: Applications and Algorithms.* (Winston, W.L.).
*   *Queueing Systems: Theory and Applications.* (Kleinrock, L.).
*   *Introduction to Deep Reinforcement Learning.* (Sutton, R.S., Barto, A.G.).

---

## 4. Simulation Launch Procedure

To launch a full end-to-end logistics optimization and simulation cycle, follow these steps:

### 4.1 Prerequisites
Ensure the infrastructure is deployed and all microservices are running in the Kubernetes cluster. Verify that Redis, PostgreSQL/PostGIS, and the message broker are reachable.

### 4.2 Step-by-Step Launch
1.  **Initialize Spatial Data:**
    Populate the database with administrative and H3 grid data:
    `python -m gis.boundary_loader --input data/administrative_units.json`

2.  **Run Optimization Solver:**
    Generate the optimal facility locations based on population demand:
    `POST /optimize/facility`
    *Payload:* `{ "num_depots": 15, "min_coverage_pct": 0.95 }`

3.  **Initialize Fleet & Network:**
    Build the graph network and deploy initial drone fleet:
    `python -m fleet.fleet_allocator --strategy demand_weighted`

4.  **Execute Simulation:**
    Trigger the Digital Twin engine to run the stochastic simulation:
    `POST /dispatch/simulate`
    *Payload:* `{ "scenario": "standard_day", "duration": 24, "seed": 42 }`

5.  **Monitor Results:**
    Visualize the simulation progress and performance metrics using the Grafana dashboard.

---

## Conclusion

This concludes the 12-phase documentation series for the TiranaFly project. The platform is fully documented, from theoretical foundations to implementation and operational validation, providing a complete, research-backed blueprint for population-aware urban drone logistics.
