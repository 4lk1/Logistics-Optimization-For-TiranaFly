export interface AdministrativeUnit {
  id: number;
  name: string;
  population: number;
  geom: any;
}

export interface HexCell {
  h3_index: string;
  population: number;
  geom: any;
}

export interface Depot {
  id: string;
  name: string;
  capacity: number;
  geom: any;
}

export interface Drone {
  id: string;
  model: string;
  status: 'IDLE' | 'AVAILABLE' | 'EN_ROUTE' | 'RETURNING' | 'CHARGING' | 'MAINTENANCE' | 'OUT_OF_SERVICE';
  depot_id: string;
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
    depots: any[];
    assignments: any[];
    total_population_served: number;
    avg_distance: number;
    max_distance: number;
    total_cost: number;
  };
}

export interface FleetStatus {
  total_drones: number;
  available_drones: number;
  active_missions: number;
  avg_battery_soc: number;
}
