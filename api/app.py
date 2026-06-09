import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import route modules
from api.routes import population, depots, routes, simulate, coverage
from backend.api.routes import gis, fleet, optimization as optimization_backend

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("Initializing system resources...")
    yield
    # Shutdown: Cleanup resources
    print("Shutting down...")

app = FastAPI(
    title="TiranaFly Fleet Optimization and Routing Logistics API Engine",
    description="Production Operations Research & Optimization API for Tirana Municipality Drone Logistics System.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}

# Include Routers with /api/v1 prefix
app.include_router(population.router, prefix="/api/v1/population", tags=["Population"])
app.include_router(depots.router, prefix="/api/v1/depots", tags=["Depots"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["Routes"])
app.include_router(simulate.router, prefix="/api/v1/simulate", tags=["Simulation"])
app.include_router(coverage.router, prefix="/api/v1/coverage", tags=["Coverage"])

# Include Backend Routers
app.include_router(gis.router, prefix="/api/v1/gis", tags=["GIS"])
app.include_router(fleet.router, prefix="/api/v1/fleet", tags=["Fleet"])
app.include_router(optimization_backend.router, prefix="/api/v1/optimization", tags=["Optimization"])

@app.get("/", tags=["API Base Layer"])
async def root():
    return {
        "project": "TiranaFly",
        "status": "ONLINE",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
