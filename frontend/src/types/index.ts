export interface AdministrativeUnit {
  id: number;
  name: string;
  population: number;
  geom: unknown;
}

export interface HexCell {
  h3_index: string;
  population: number;
  centroid_lat: number;
  centroid_lon: number;
  assigned_unit: string;
  coverage_depot_id?: string;
  geom: unknown;
}

export interface Depot {
  id: string;
  name: string;
  capacity: number;
  lat: number;
  lng: number;
  geom?: unknown;
}

export interface Drone {
  id: string;
  model: string;
  status: 'IDLE' | 'AVAILABLE' | 'EN_ROUTE' | 'RETURNING' | 'CHARGING' | 'MAINTENANCE' | 'OUT_OF_SERVICE';
  depot_id: string;
  lat?: number;
  lng?: number;
  battery?: Battery;
}

export interface Battery {
  id: string;
  soc: number;
  soh: number;
  cycle_count: number;
}

export interface Mission {
  id: string;
  drone_id: string;
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  payload_kg: number;
}

export interface OptimizationResult {
  id: number;
  method: string;
  timestamp: string;
  data: {
    depots: Depot[];
    assignments: unknown[];
    total_population_served: number;
    avg_distance: number;
    max_distance: number;
    total_cost: number;
  };
}

export interface SimulationRequest {
  iterations: number;
  depot_count: number;
  fleet_pool: number;
  replay_sample_size?: number;
}

export interface SimulationResult {
  total_orders_processed: number;
  successful_deliveries: number;
  failed_deliveries: number;
  system_delivery_success_rate: number;
  average_delivery_wait_time_sec: number;
  orders: SimulationOrder[];
}

export interface SimulationOrder {
  id: string;
  drone_id: string;
  depot_id: string;
  target_h3: string;
  destination: {
    lat: number;
    lng: number;
  };
  status: 'DELIVERED' | 'FAILED';
  path: string[];
  path_coordinates: [number, number][];
  distance_km: number;
  duration_sec: number;
}

export interface FleetStatus {
  total_drones: number;
  available_drones: number;
  active_missions: number;
  avg_battery_soc: number;
}
