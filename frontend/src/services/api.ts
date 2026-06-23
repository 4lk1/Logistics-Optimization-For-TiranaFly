import axios from 'axios';
import { 
  AdministrativeUnit, HexCell, Drone, OptimizationResult, SimulationRequest, SimulationResult
} from '../types';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const gisApi = {
  getAdminUnits: () => apiClient.get<AdministrativeUnit[]>('/gis/admin-units').then(res => res.data),
  getHexCells: () => apiClient.get<HexCell[]>('/gis/h3-cells').then(res => res.data),
  initialize: () => apiClient.post('/gis/initialize'),
};

export const optimizationApi = {
  run: (maxDepots: number) => apiClient.post('/optimization/run', { depot_count: maxDepots }).then(res => res.data),
  getLatest: () => apiClient.get<OptimizationResult>('/optimization/latest').then(res => res.data),
};

export const fleetApi = {
  getStatus: () => apiClient.get<Drone[]>('/fleet/status').then(res => res.data),
  initialize: (depotId: string, numDrones: number) => 
    apiClient.post(`/fleet/initialize/${depotId}?num_drones=${numDrones}`),
};

export const simulationApi = {
  run: (payload: SimulationRequest) => apiClient.post<SimulationResult>('/simulate', payload).then(res => res.data),
};

export default apiClient;
