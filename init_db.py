from sqlalchemy import create_engine
from backend.db.models.spatial import Base
from backend.core.config import settings

def init_db():
    print(f"Connecting to database: {settings.database_url}")
    # Create engine. Note: GeoAlchemy2 needs PostGIS enabled on the database!
    engine = create_engine(settings.database_url)
    
    # Ensure PostGIS extension is enabled (might require superuser permissions)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    import sqlalchemy
    init_db()
