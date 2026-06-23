import { useMemo } from 'react';
import Map from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer, PathLayer, ScatterplotLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { MapView, type LayersList } from '@deck.gl/core';
import { useStore } from '../store/useStore';
import type { AdministrativeUnit, Depot, Drone, HexCell, SimulationOrder } from '@/types';
import 'maplibre-gl/dist/maplibre-gl.css';

type GeoJsonLayerData = ConstructorParameters<typeof GeoJsonLayer>[0]['data'];
type BoundarySource = GeoJsonLayerData | AdministrativeUnit[];

function isAdministrativeUnits(boundaries: BoundarySource): boundaries is AdministrativeUnit[] {
  return Array.isArray(boundaries) && boundaries.some((unit) => typeof unit === 'object' && unit !== null && 'geom' in unit);
}

const depotPalette: Record<string, [number, number, number, number]> = {
  DEPOT_00: [56, 189, 248, 120],
  DEPOT_01: [52, 211, 153, 120],
  DEPOT_02: [168, 85, 247, 120],
  DEPOT_03: [251, 146, 60, 120],
  DEPOT_04: [248, 113, 113, 120],
};

const boundaryPalette: [number, number, number, number][] = [
  [96, 165, 250, 48],
  [52, 211, 153, 48],
  [168, 85, 247, 48],
  [251, 146, 60, 48],
  [244, 114, 182, 48],
  [34, 211, 238, 48],
  [250, 204, 21, 48],
];

function boundaryFillColor(feature: { properties?: { id?: number } }): [number, number, number, number] {
  const id = feature.properties?.id ?? 1;
  return boundaryPalette[(id - 1) % boundaryPalette.length];
}

function coverageColor(cell: HexCell): [number, number, number, number] {
  if (cell.coverage_depot_id && depotPalette[cell.coverage_depot_id]) {
    return depotPalette[cell.coverage_depot_id];
  }

  return [59, 130, 246, 70];
}

function interpolatePath(path: [number, number][], progress: number): [number, number] {
  if (!path.length) return [19.8189, 41.3275];
  if (path.length === 1) return path[0];

  const clamped = Math.min(Math.max(progress, 0), 1);
  const scaled = clamped * (path.length - 1);
  const index = Math.min(Math.floor(scaled), path.length - 2);
  const segmentProgress = scaled - index;
  const start = path[index];
  const end = path[index + 1];

  return [
    start[0] + (end[0] - start[0]) * segmentProgress,
    start[1] + (end[1] - start[1]) * segmentProgress,
  ];
}

interface TiranaMapProps {
  boundaries?: BoundarySource;
  h3Cells?: HexCell[];
  depots?: Depot[];
  drones?: Drone[];
  simulationOrders?: SimulationOrder[];
  replayProgress?: number;
  selectedOrderId?: string | null;
}

export default function TiranaMap({ 
  boundaries, h3Cells, depots, drones, simulationOrders, replayProgress = 0, selectedOrderId 
}: TiranaMapProps) {
  const { viewport, layers, setViewport } = useStore();
  const boundaryData = useMemo<GeoJsonLayerData | undefined>(() => {
    if (!boundaries) return undefined;

    if (isAdministrativeUnits(boundaries)) {
      return boundaries.map((unit) => ({
        type: 'Feature',
        geometry: unit.geom,
        properties: {
          id: unit.id,
          name: unit.name,
          population: unit.population,
        },
      })) as GeoJsonLayerData;
    }

    return boundaries as GeoJsonLayerData;
  }, [boundaries]);
  const movingDrones = useMemo(() => {
    return (simulationOrders ?? [])
      .filter((order) => order.status === 'DELIVERED' && order.path_coordinates.length > 0)
      .map((order) => ({
        id: order.drone_id,
        order_id: order.id,
        depot_id: order.depot_id,
        position: interpolatePath(order.path_coordinates, replayProgress),
        selected: order.id === selectedOrderId,
      }));
  }, [replayProgress, selectedOrderId, simulationOrders]);

  const deckLayers = useMemo<LayersList>(() => {
    const deliveredOrders = (simulationOrders ?? []).filter((order) => order.path_coordinates.length > 1);

    return [
      // 1. H3 Population Grid
      layers.h3 && h3Cells && new H3HexagonLayer({
        id: 'h3-layer',
        data: h3Cells,
        pickable: true,
        wireframe: true,
        filled: true,
        extruded: false,
        getHexagon: (d: HexCell) => d.h3_index,
        getFillColor: coverageColor,
        getLineColor: [255, 255, 255, 35],
      }),

      // 2. Administrative Units
      layers.boundaries && boundaryData && new GeoJsonLayer({
        id: 'boundaries-layer',
        data: boundaryData,
        filled: true,
        stroked: true,
        getFillColor: boundaryFillColor,
        getLineColor: [255, 255, 255, 210],
        getLineWidth: 2,
        lineWidthUnits: 'pixels',
        pickable: true,
      }),

      // 3. Simulation Route Paths
      layers.routes && deliveredOrders.length > 0 && new PathLayer({
        id: 'simulation-routes-layer',
        data: deliveredOrders,
        pickable: true,
        widthUnits: 'pixels',
        getPath: (d: SimulationOrder) => d.path_coordinates,
        getColor: (d: SimulationOrder) => d.id === selectedOrderId ? [255, 255, 255, 230] : [34, 211, 238, 150],
        getWidth: (d: SimulationOrder) => d.id === selectedOrderId ? 4 : 2,
      }),

      // 4. Simulated Order Destinations
      simulationOrders && simulationOrders.length > 0 && new ScatterplotLayer({
        id: 'orders-layer',
        data: simulationOrders,
        getPosition: (d: SimulationOrder) => [d.destination.lng, d.destination.lat],
        getFillColor: (d: SimulationOrder) => d.status === 'DELIVERED' ? [34, 197, 94, 210] : [248, 113, 113, 230],
        getLineColor: [255, 255, 255, 180],
        getLineWidth: 1,
        getRadius: (d: SimulationOrder) => d.id === selectedOrderId ? 180 : 90,
        radiusMinPixels: 4,
        radiusMaxPixels: 14,
        stroked: true,
        pickable: true,
      }),

      // 5. Depots
      layers.depots && depots && new ScatterplotLayer({
        id: 'depots-layer',
        data: depots,
        getPosition: (d: Depot) => [d.lng, d.lat],
        getFillColor: [0, 150, 255],
        getRadius: 200,
        pickable: true,
      }),

      // 6. Drones (Live Positions)
      layers.drones && drones && new ScatterplotLayer({
        id: 'drones-layer',
        data: drones,
        getPosition: (d: Drone) => [d.lng ?? viewport.longitude, d.lat ?? viewport.latitude],
        getFillColor: (d: Drone) => d.status === 'EN_ROUTE' ? [255, 200, 0] : [0, 255, 100],
        getRadius: 50,
        pickable: true,
      }),

      // 7. Simulation Replay Drones
      layers.drones && movingDrones.length > 0 && new ScatterplotLayer({
        id: 'simulation-drones-layer',
        data: movingDrones,
        getPosition: (d) => d.position,
        getFillColor: (d) => d.selected ? [255, 255, 255, 255] : [250, 204, 21, 235],
        getLineColor: [15, 23, 42, 220],
        getLineWidth: 2,
        getRadius: (d) => d.selected ? 180 : 120,
        radiusMinPixels: 6,
        radiusMaxPixels: 18,
        stroked: true,
        pickable: true,
      }),
    ].filter(Boolean) as LayersList;
  }, [boundaryData, h3Cells, depots, drones, layers, movingDrones, selectedOrderId, simulationOrders, viewport.latitude, viewport.longitude]);

  return (
    <div className="relative w-full h-full">
      <DeckGL
        initialViewState={viewport}
        controller={true}
        onViewStateChange={(e) => setViewport({
          latitude: e.viewState.latitude,
          longitude: e.viewState.longitude,
          zoom: e.viewState.zoom,
          pitch: e.viewState.pitch ?? viewport.pitch,
          bearing: e.viewState.bearing ?? viewport.bearing,
        })}
        layers={deckLayers}
        views={new MapView({ id: 'main', repeat: true })}
      >
        <Map
          mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
          reuseMaps
        />
      </DeckGL>

      {/* Map Controls */}
      <div className="absolute bottom-8 right-8 flex flex-col space-y-2 z-50">
        <button className="w-10 h-10 glass rounded-lg flex items-center justify-center text-white hover:bg-blue-600/40 transition-colors" onClick={() => setViewport({ ...viewport, zoom: viewport.zoom + 1 })}>
          +
        </button>
        <button className="w-10 h-10 glass rounded-lg flex items-center justify-center text-white hover:bg-blue-600/40 transition-colors" onClick={() => setViewport({ ...viewport, zoom: viewport.zoom - 1 })}>
          -
        </button>
      </div>
    </div>
  );
}
