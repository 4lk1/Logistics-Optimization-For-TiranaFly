from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase
from geoalchemy2 import Geometry
import datetime

class Base(DeclarativeBase):
    pass

class AdministrativeUnit(Base):
    __tablename__ = "administrative_units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    population = Column(Integer)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))

class HexCell(Base):
    __tablename__ = "hex_cells"
    id = Column(Integer, primary_key=True, index=True)
    h3_index = Column(String, unique=True, index=True)
    population = Column(Integer)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))

class Depot(Base):
    __tablename__ = "depots"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    capacity = Column(Integer)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    drones = relationship("Drone", back_populates="depot")

class Drone(Base):
    __tablename__ = "drones"
    id = Column(String, primary_key=True, index=True)
    model = Column(String)
    status = Column(String) # Enum mapping
    depot_id = Column(String, ForeignKey("depots.id"))
    depot = relationship("Depot", back_populates="drones")
    battery_id = Column(String, ForeignKey("batteries.id"))
    battery = relationship("Battery", uselist=False)

class Battery(Base):
    __tablename__ = "batteries"
    id = Column(String, primary_key=True, index=True)
    soc = Column(Float)
    soh = Column(Float)
    cycle_count = Column(Integer)

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(String)
    destination_id = Column(String)
    distance = Column(Float)
    geom = Column(Geometry(geometry_type='LINESTRING', srid=4326))

class Mission(Base):
    __tablename__ = "missions"
    id = Column(String, primary_key=True, index=True)
    drone_id = Column(String, ForeignKey("drones.id"))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String)
    payload_kg = Column(Float)

class OptimizationResultModel(Base):
    __tablename__ = "optimization_results"
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(JSON) # Store full OptimizationResult as JSON

class NoFlyZone(Base):
    __tablename__ = "no_fly_zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
