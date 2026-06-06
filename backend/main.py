from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import gis, optimization, fleet
from backend.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gis.router, prefix=f"{settings.API_V1_STR}/gis", tags=["GIS"])
app.include_router(optimization.router, prefix=f"{settings.API_V1_STR}/optimization", tags=["Optimization"])
app.include_router(fleet.router, prefix=f"{settings.API_V1_STR}/fleet", tags=["Fleet"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
