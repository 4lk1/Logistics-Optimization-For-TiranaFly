import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fleetApi, optimizationApi } from '../services/api';
import { 
  Plane, Battery, Activity, ShieldAlert, 
  MapPin, Plus, CheckCircle2, MoreVertical 
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function FleetOperations() {
  const queryClient = useQueryClient();
  const { data: fleet, isLoading: isFleetLoading } = useQuery({ 
    queryKey: ['fleet'], 
    queryFn: fleetApi.getStatus 
  });
  
  const { data: latestOpt } = useQuery({ 
    queryKey: ['latestOptimization'], 
    queryFn: optimizationApi.getLatest 
  });

  const initMutation = useMutation({
    mutationFn: ({ depotId, count }: any) => fleetApi.initialize(depotId, count),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleet'] });
    }
  });

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      <div className="p-8 pb-4">
        <header className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center">
              <Plane className="w-6 h-6 mr-3 text-blue-500" />
              Fleet Operations Center
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              Real-time telemetry and management of UAV assets across 14 municipal zones.
            </p>
          </div>
          
          <div className="flex space-x-4">
            <SummaryWidget label="Total Assets" value={fleet?.length || 0} />
            <SummaryWidget label="In Flight" value={fleet?.filter(d => d.status === 'EN_ROUTE').length || 0} color="text-yellow-500" />
            <SummaryWidget label="Available" value={fleet?.filter(d => d.status === 'AVAILABLE').length || 0} color="text-green-500" />
          </div>
        </header>
      </div>

      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-3 gap-8 p-8">
        {/* Depot Status List */}
        <div className="lg:col-span-2 space-y-6 overflow-y-auto custom-scrollbar pr-2">
          <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest px-2">Operational Depots</h3>
          
          {latestOpt?.data?.depots?.map((depot: any) => (
            <div key={depot.id} className="glass p-6 rounded-2xl border hover:border-white/20 transition-all">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mr-4">
                    <MapPin className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-white">{depot.id}</h4>
                    <p className="text-xs text-muted-foreground uppercase tracking-tighter">Coord: {depot.lat.toFixed(4)}, {depot.lng.toFixed(4)}</p>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button 
                    onClick={() => initMutation.mutate({ depotId: depot.id, count: 5 })}
                    disabled={initMutation.isPending}
                    className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-bold text-white border border-white/5 transition-all flex items-center"
                  >
                    <Plus className="w-3 h-3 mr-2" />
                    Deploy 5 Drones
                  </button>
                  <button className="p-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 transition-all">
                    <MoreVertical className="w-4 h-4 text-muted-foreground" />
                  </button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MiniStat label="Utilization" value="78%" />
                <MiniStat label="Charging" value="2" />
                <MiniStat label="Ready" value="3" />
                <MiniStat label="Health" value="98.5%" />
              </div>
            </div>
          ))}
          
          {(!latestOpt || latestOpt.data.depots.length === 0) && (
            <div className="p-12 rounded-3xl bg-white/5 border border-dashed flex flex-col items-center text-center">
              <ShieldAlert className="w-12 h-12 text-muted-foreground mb-4 opacity-20" />
              <p className="text-muted-foreground max-w-xs">No active depots found. Please run the optimization engine to deploy infrastructure.</p>
            </div>
          )}
        </div>

        {/* Live Telemetry Feed */}
        <div className="glass rounded-3xl border flex flex-col overflow-hidden">
          <header className="p-6 border-b border-white/5 bg-white/5">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center">
              <Activity className="w-4 h-4 mr-2 text-red-500 animate-pulse" />
              Live Telemetry
            </h3>
          </header>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-4">
            {fleet?.map((drone) => (
              <div key={drone.id} className="p-4 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between group hover:border-blue-500/30 transition-all">
                <div className="flex items-center">
                  <div className={cn(
                    "w-2 h-2 rounded-full mr-4 animate-pulse",
                    drone.status === 'EN_ROUTE' ? "bg-yellow-500" : "bg-green-500"
                  )}></div>
                  <div>
                    <p className="text-xs font-bold text-white uppercase tracking-tighter">{drone.id}</p>
                    <p className="text-[10px] text-muted-foreground">SOC: {((drone.battery?.soc || 0) * 100).toFixed(0)}% • {drone.status}</p>
                  </div>
                </div>
                <Battery className={cn(
                  "w-4 h-4",
                  (drone.battery?.soc || 0) < 0.3 ? "text-red-500" : "text-muted-foreground"
                )} />
              </div>
            ))}
            
            {(!fleet || fleet.length === 0) && (
              <p className="text-xs text-muted-foreground text-center py-12 italic">Waiting for fleet deployment...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryWidget({ label, value, color = "text-white" }: any) {
  return (
    <div className="px-6 py-3 glass rounded-xl border border-white/5 min-w-[120px]">
      <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1">{label}</p>
      <p className={cn("text-xl font-bold tracking-tight", color)}>{value}</p>
    </div>
  );
}

function MiniStat({ label, value }: any) {
  return (
    <div className="p-3 rounded-xl bg-white/5 border border-white/5">
      <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter mb-1">{label}</p>
      <p className="text-sm font-bold text-white">{value}</p>
    </div>
  );
}
