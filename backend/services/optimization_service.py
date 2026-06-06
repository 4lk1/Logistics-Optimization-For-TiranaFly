from sqlalchemy.orm import Session
from backend.db.models.spatial import OptimizationResultModel, HexCell, Depot
from optimization.depot_selector import DepotSelector
from optimization.models import OptimizationConfig
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
import geopandas as gpd
from dataclasses import asdict

class OptimizationService:
    @staticmethod
    def run_full_optimization(db: Session, max_depots: int = 10):
        """Runs the Depot Selection Engine and saves the best strategy."""
        # 1. Fetch H3 cells from DB
        cells = db.query(HexCell).all()
        h3_gdf = gpd.GeoDataFrame([
            {'h3_id': c.h3_index, 'population': c.population, 'geometry': to_shape(c.geom)}
            for c in cells
        ], crs="EPSG:4326")
        
        # 2. Define Candidate Locations (e.g., existing city properties or random sampling)
        # For simplicity, we sample from H3 centroids
        candidates_gdf = h3_gdf.sample(min(20, len(h3_gdf))).copy()
        candidates_gdf['id'] = [f"cand_{i}" for i in range(len(candidates_gdf))]
        
        # 3. Run Optimization
        config = OptimizationConfig(max_depots=max_depots)
        selector = DepotSelector(config)
        best_result = selector.select_best_strategy(h3_gdf, candidates_gdf)
        
        # 4. Save to DB
        db_res = OptimizationResultModel(
            method=best_result.method_name,
            data=asdict(best_result)
        )
        db.add(db_res)
        
        # 5. Materialize Depots
        for d in best_result.depots:
            depot = Depot(
                id=d.id,
                name=f"Depot {d.id}",
                capacity=d.capacity,
                geom=from_shape(Point(d.lng, d.lat), srid=4326)
            )
            db.merge(depot)
            
        db.commit()
        return best_result

    @staticmethod
    def get_latest_result(db: Session):
        return db.query(OptimizationResultModel).order_by(OptimizationResultModel.timestamp.desc()).first()
