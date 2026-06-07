from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import gis, optimization, fleet
from backend.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register production routers with standardized prefixes
app.include_router(gis.router, prefix=f"{settings.API_V1_STR}/gis", tags=["GIS Foundation"])
app.include_router(optimization.router, prefix=f"{settings.API_V1_STR}/optimization", tags=["Optimization Engine"])
app.include_router(fleet.router, prefix=f"{settings.API_V1_STR}/fleet", tags=["Fleet Operations"])

# Legacy support for frontend calling /api directly
app.include_router(gis.router, prefix="/api/gis", tags=["GIS Legacy"])
app.include_router(optimization.router, prefix="/api/optimization", tags=["Optimization Legacy"])
app.include_router(fleet.router, prefix="/api/fleet", tags=["Fleet Legacy"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "ONLINE",
        "api_docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
