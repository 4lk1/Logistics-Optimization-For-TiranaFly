# filename: api/app.py
import sys
import os

# Ensure project root is in sys.path to allow correct imports when running the API
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
import uvicorn

# Import route modules
from api.routes import population, depots, optimize, routes, simulate, coverage

app = FastAPI(
    title="TiranaFly Fleet Optimization and Routing Logistics API Engine",
    description="Production Operations Research & Optimization API for Tirana Municipality Drone Logistics System.",
    version="1.0.0"
)

# Register routers
app.include_router(population.router)
app.include_router(depots.router)
app.include_router(optimize.router)
app.include_router(routes.router)
app.include_router(simulate.router)
app.include_router(coverage.router)

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