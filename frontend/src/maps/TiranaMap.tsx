import React, { useMemo } from 'react';
import Map from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer, ScatterplotLayer, LineLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { MapView } from '@deck.gl/core';
import { useStore } from '../store/useStore';
import 'maplibre-gl/dist/maplibre-gl.css';

interface TiranaMapProps {
  boundaries?: any;
  h3Cells?: any[];
  depots?: any[];
  routes?: any[];
  drones?: any[];
}

export default function TiranaMap({ 
  boundaries, h3Cells, depots, routes, drones 
}: TiranaMapProps) {
  const { viewport, layers, setViewport } = useStore();

  const deckLayers = useMemo(() => {
    return [
      // 1. Administrative Units
      layers.boundaries && boundaries && new GeoJsonLayer({
        id: 'boundaries-layer',
        data: boundaries,
        filled: true,
        stroked: true,
        getFillColor: [40, 100, 200, 20],
        getLineColor: [100, 150, 255, 100],
        getLineWidth: 20,
        pickable: true,
      }),

      // 2. H3 Population Grid
      layers.h3 && h3Cells && new H3HexagonLayer({
        id: 'h3-layer',
        data: h3Cells,
        pickable: true,
        wireframe: false,
        filled: true,
        extruded: true,
        elevationScale: 5,
        getHexagon: (d: any) => d.h3_index,
        getFillColor: (d: any) => {
          const p = d.population;
          if (p > 5000) return [200, 50, 50, 200];
          if (p > 2000) return [200, 150, 50, 200];
          return [50, 150, 50, 150];
        },
        getElevation: (d: any) => d.population / 10,
      }),

      // 3. Depots
      layers.depots && depots && new ScatterplotLayer({
        id: 'depots-layer',
        data: depots,
        getPosition: (d: any) => [d.lng, d.lat],
        getFillColor: [0, 150, 255],
        getRadius: 200,
        pickable: true,
      }),

      // 4. Drones (Live Positions)
      layers.drones && drones && new ScatterplotLayer({
        id: 'drones-layer',
        data: drones,
        getPosition: (d: any) => [d.lng, d.lat],
        getFillColor: (d: any) => d.status === 'EN_ROUTE' ? [255, 200, 0] : [0, 255, 100],
        getRadius: 50,
        pickable: true,
      }),
    ].filter(Boolean);
  }, [boundaries, h3Cells, depots, routes, drones, layers]);

  return (
    <div className="relative w-full h-full">
      <DeckGL
        initialViewState={viewport}
        controller={true}
        onViewStateChange={(e) => setViewport(e.viewState)}
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
