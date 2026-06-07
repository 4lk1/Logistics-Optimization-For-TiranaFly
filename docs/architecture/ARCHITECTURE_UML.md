# TiranaFly: System Architecture & UML

## 1. System Context Diagram (C1)
```mermaid
graph TD
    User((City Administrator))
    TF[TiranaFly Platform]
    GIS[(Tirana GIS Data)]
    Drone[Drone Fleet]
    
    User -- Manages --> TF
    TF -- Queries --> GIS
    TF -- Dispatches --> Drone
    Drone -- Telemetry --> TF
```

## 2. Container Diagram (C2)
```mermaid
graph LR
    subgraph "TiranaFly Platform"
        FE[Frontend Dashboard - React]
        BE[Backend API - FastAPI]
        DB[(PostGIS Database)]
        Worker[Celery Worker]
        Redis[Redis Task Queue]
    end
    
    FE -- HTTPS --> BE
    BE -- SQL --> DB
    BE -- Tasks --> Redis
    Redis -- Consumes --> Worker
    Worker -- Optimization/Simulation --> DB
```

## 3. Class Diagram - Core Optimization Engine
```mermaid
classDiagram
    class DepotSelector {
        +select_best_strategy(h3_gdf, candidate_gdf) OptimizationResult
    }
    class WeightedKMeansOptimizer {
        +optimize(coords, populations)
        +get_results() OptimizationResult
    }
    class PMedianOptimizer {
        +optimize(demand, candidate, pop) OptimizationResult
    }
    class OptimizationResult {
        +List depots
        +List assignments
        +float total_population_served
    }
    
    DepotSelector --> WeightedKMeansOptimizer
    DepotSelector --> PMedianOptimizer
    DepotSelector --> OptimizationResult
```

## 4. Sequence Diagram - Mission Dispatch
```mermaid
sequenceDiagram
    participant U as Administrator
    participant BE as Backend API
    participant W as Worker
    participant FE as Fleet Engine
    participant D as Drone
    
    U->>BE: POST /dispatch (Mission)
    BE->>W: Queue Dispatch Task
    W->>FE: Calculate Optimal Path
    FE->>D: Transmit Waypoints
    D->>FE: Mission Started
    FE->>BE: Update Mission Status
    BE->>U: Mission Active
```
