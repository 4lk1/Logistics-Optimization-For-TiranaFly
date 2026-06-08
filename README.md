# README.md

#  TiranaFly: Autonomous Urban Drone Logistics Optimization

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![GIS](https://img.shields.io/badge/GIS-H3%20%7C%20PostGIS-orange.svg)](https://h3geo.org/)
[![Optimization](https://img.shields.io/badge/Optimization-OR--Tools%20%7C%20NetworkX-green.svg)](https://developers.google.com/optimization)

**TiranaFly** is a production-grade research and optimization platform designed to orchestrate an autonomous multi-depot drone delivery network for the Municipality of Tirana, Albania. Developed as a Master’s thesis project, it integrates 2023 Census data with high-resolution hexagonal tessellation (H3) to solve complex facility location problems, optimize flight paths, and simulate network resilience.

---

##  Table of Contents

- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Requirements](#-requirements)
- [Installation Guide](#-installation-guide)
- [Execution & Reproducibility](#-execution--reproducibility)
- [Dataset Documentation](#-dataset-documentation)
- [Project Workflow](#-project-workflow)
- [Technical Structure](#-technical-structure)
- [Future Roadmap](#-future-roadmap)

---

##  Project Overview

As urban congestion in Tirana increases, traditional ground-based delivery models face diminishing returns. TiranaFly proposes a digital twin and logistics orchestrator that:
- **Spatial Intelligence**: Maps 807,029 residents into ~5,000 H3 hexagonal cells.
- **Infrastructure Optimization**: Uses Mixed-Integer Programming (CFLP) and Weighted K-Means to minimize flight distances.
- **Resilience Modeling**: Simulates battery failures, weather disruptions, and demand spikes using Monte Carlo methods.

---

##  System Architecture

The system follows a modular, decoupled architecture:

1.  **Core Optimization Engine**: Solves P-Median, P-Center, and Capacitated Facility Location Problems (CFLP).
2.  **GIS & Spatial Layer**: Handles WGS84 coordinate transformations, H3 indexing, and administrative boundary mapping.
3.  **Fleet & Dispatch Engine**: Manages drone allocation via M/M/s queueing models and calculates optimal energy-aware routes.
4.  **AI Layer**: Provides predictive maintenance, demand forecasting, and reinforcement learning for real-time dispatch.
5.  **Simulation Engine**: A stochastic environment for validating network KPIs under stress.
6.  **Full-Stack Interface**: FastAPI backend with PostGIS storage and a React/Deck.gl frontend for 3D spatial visualization.

---

##  Key Features

- **Population-Aware Modeling**: Automatically distributes census data to hexagonal grids based on geographic density.
- **Multi-Depot Routing**: NetworkX-powered Dijkstra pathfinding across spherical coordinate systems.
- **Energy Models**: Real-world flight power consumption calculations (Wh/km) based on drone mass and air density.
- **Automated Visualization**: Generates thematic choropleth maps and active flight path overlays.
- **Predictive Analytics**: Anomaly detection and battery degradation tracking for fleet longevity.

---

##  Requirements

### Backend & Optimization
- **Python 3.11+**
- **Poetry** (Recommended) or standard `pip`
- **System Dependencies**: `GDAL`, `PROJ`, `libgeos` (for GeoPandas/Shapely)
- **Primary Libraries**: `fastapi`, `numpy`, `scikit-learn`, `ortools`, `networkx`, `h3`, `geopandas`, `matplotlib`, `sqlalchemy`.

### Frontend
- **Node.js 18+**
- **Vite**, **React 19**, **TailwindCSS**, **Deck.gl**

---

##  Installation Guide

### 1. Clone & Environment Setup
```bash
git clone https://github.com/thearchitect/Logistics-Optimization-For-TiranaFly.git
cd Logistics-Optimization-For-TiranaFly
```

### 2. Backend Installation (Poetry)
```bash
# Install dependencies via Poetry
poetry install
poetry shell
```
*Alternatively, using pip:*
```bash
pip install -r backend/requirements.txt
```

### 3. Frontend Installation
```bash
cd frontend
npm install
```

### 4. Database (Optional - Docker)
```bash
# Start PostGIS, Redis, and API stack
docker-compose -f backend/docker-compose.yml up -d
```

---

##  How to Run the Project

### 1. Execute Production Pipeline
The primary entry point that runs the full GIS $\rightarrow$ Optimization $\rightarrow$ Simulation workflow:
```bash
python main.py
```
This script validates census invariants, optimizes 3 hub locations, builds the topology, and runs a 250-iteration stochastic simulation.

### 2. Run Automated Spatial Infrastructure (Map Gen)
To generate the thematic administrative maps and test routing:
```bash
python MainMap.py
```

### 3. Run FastAPI Backend
```bash
uvicorn api.app:app --reload
```

### 4. Run Frontend Dashboard
```bash
cd frontend
npm run dev
```

---

##  Dataset Documentation

### Official Population Baseline (Census 2023)
The system is hardcoded with mandatory population data for Tirana's 14 administrative units to ensure normalization consistency:

| Administrative Unit | Population |
| :--- | :--- |
| **Tiranë** | 598,176 |
| **Kashar** | 89,395 |
| **Dajt** | 35,170 |
| **Farkë** | 36,266 |
| **Petrelë** | 5,723 |
| **Vaqarr** | 9,221 |
| **Pezë** | 5,704 |
| **Ndroq** | 4,169 |
| **Baldushk** | 3,879 |
| **Bërzhitë** | 4,291 |
| **Krrabë** | 2,023 |
| **Zall Bastar** | 2,813 |
| **Zall Herr** | 8,822 |
| **Shëngjergj** | 1,377 |
| **TOTAL** | **807,029** |

---

##  Project Workflow

1.  **Ingestion**: `DemographicsEngine` loads official census records.
2.  **Tessellation**: `HexSpatialEngine` generates a WGS84 grid centered on administrative centroids.
3.  **Weighting**: `PopulationMapper` distributes the 807k residents across H3 cells.
4.  **Optimization**: `FacilityLocationOptimizer` solves the CFLP using Google OR-Tools to select depot sites.
5.  **Graph Construction**: `FlightGraphBuilder` creates a DiGraph of all valid flight corridors.
6.  **Simulation**: `TiranaFlyStochasticSimulationEngine` executes mission sorties, logging success rates and wait times.
7.  **Visualization**: `LogisticsMapVisualizer` exports PNG maps and the React dashboard renders real-time telemetry.

---

##  Project Structure

```text
├── main.py                 # Core production pipeline
├── MainMap.py              # Spatial infrastructure & Map engine
├── ai/                     # ML models (Demand, Battery, Maintenance)
├── api/                    # FastAPI routes & PostGIS repositories
├── backend/                # Docker, Requirements, Core logic
├── data/                   # Raw census data (CSV)
├── docs/                   # Thesis, Math, Architecture (UML)
├── fleet/                  # Queueing models & Battery management
├── gis/                    # H3 grid, population mapping, geometry
├── graph/                  # NetworkX topology & Routing
├── optimization/           # Facility Location (CFLP, p-Median)
├── simulation/             # Stochastic & Monte Carlo engines
├── visualization/          # Matplotlib maps & Recharts dashboards
└── frontend/               # Vite/React/Deck.gl dashboard
```

---

##  Reproducibility

To reproduce the thesis results exactly:
1.  **Deterministic Seed**: All scripts use `RANDOM_SEED = 42`. Ensure this is set in your environment.
2.  **H3 Resolution**: Use Resolution 8 for urban core analysis.
3.  **UAV Constraints**: Default range is set to **18.0 km** with an energy coefficient of **45.0 Wh/km**.

---

##  Common Issues & Debugging

- **GDAL/Fiona Install Failures**: Ensure system headers are installed (`sudo apt install libgdal-dev`).
- **OR-Tools Solver Error**: Ensure you have `ortools` installed via pip. The CFLP model requires the `SCIP` solver (included in standard binary).
- **Empty Map Output**: Verify that `matplotlib` has a valid backend (TkAgg or Agg for headless).

---

##  Future Improvements

- **Dynamic Weather Integration**: Real-time API hooks for wind speed impact on battery range.
- **Dynamic Pricing**: Implementing fleet utilization-based delivery pricing.
- **Multi-Agent RL**: Replacing Dijkstra with a learned dispatch agent for high-density congestion.

---

##  Academic Note
This project was developed as part of a Master's Project on Urban Logistics.
**Citation Expectation**: Please cite as "TiranaFly: Autonomous Urban Drone Logistics Optimization Platform (2026)".

# README.md
