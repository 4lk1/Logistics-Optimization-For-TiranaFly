from sqlalchemy.orm import Session
from backend.db.models.spatial import AdministrativeUnit, HexCell
from gis.boundary_loader import BoundaryLoader
from gis.population_mapper import PopulationMapper
from geoalchemy2.shape import from_shape
import geopandas as gpd

class GISService:
    @staticmethod
    def initialize_spatial_data(db: Session):
        """Seed the database with Tirana boundaries and H3 population grid."""
        # 1. Load boundaries
        boundaries_gdf = BoundaryLoader.load_boundaries()
        
        for _, row in boundaries_gdf.iterrows():
            unit = AdministrativeUnit(
                name=row['name'],
                population=0, # Will be updated or set from metadata
                geom=from_shape(row.geometry, srid=4326)
            )
            db.add(unit)
            
        # 2. Map Population to H3
        h3_gdf = PopulationMapper.map_population_to_h3(boundaries_gdf)
        
        for _, row in h3_gdf.iterrows():
            cell = HexCell(
                h3_index=row['h3_id'],
                population=int(row['population']),
                geom=from_shape(row.geometry, srid=4326)
            )
            db.add(cell)
            
        db.commit()

    @staticmethod
    def get_all_hex_cells(db: Session):
        return db.query(HexCell).all()

    @staticmethod
    def get_administrative_units(db: Session):
        return db.query(AdministrativeUnit).all()
