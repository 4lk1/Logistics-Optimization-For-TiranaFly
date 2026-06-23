import { create } from 'zustand';
import { Drone, OptimizationResult } from '../types';

interface MapViewport {
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
}

interface AppState {
  // Map State
  viewport: MapViewport;
  layers: {
    boundaries: boolean;
    h3: boolean;
    population: boolean;
    depots: boolean;
    drones: boolean;
    routes: boolean;
  };
  
  // Data State
  latestOptimization: OptimizationResult | null;
  fleet: Drone[];
  
  // Actions
  setViewport: (viewport: MapViewport) => void;
  toggleLayer: (layer: keyof AppState['layers']) => void;
  setLatestOptimization: (result: OptimizationResult) => void;
  setFleet: (fleet: Drone[]) => void;
}

export const useStore = create<AppState>((set) => ({
  viewport: {
    latitude: 41.3275,
    longitude: 19.8189,
    zoom: 12,
    pitch: 45,
    bearing: 0,
  },
  layers: {
    boundaries: true,
    h3: true,
    population: true,
    depots: true,
    drones: true,
    routes: true,
  },
  latestOptimization: null,
  fleet: [],

  setViewport: (viewport) => set({ viewport }),
  toggleLayer: (layer) => set((state) => ({
    layers: { ...state.layers, [layer]: !state.layers[layer] }
  })),
  setLatestOptimization: (latestOptimization) => set({ latestOptimization }),
  setFleet: (fleet) => set({ fleet }),
}));
