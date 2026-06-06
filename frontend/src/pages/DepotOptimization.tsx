import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { optimizationApi, gisApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { 
  Calculator, Play, CheckCircle2, AlertCircle, 
  Settings2, Download, Info 
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function DepotOptimization() {
  const queryClient = useQueryClient();
  const [maxDepots, setMaxDepots] = useState(10);
  
  const { data: latestOpt, isLoading: isLatestLoading } = useQuery({ 
    queryKey: ['latestOptimization'], 
    queryFn: optimizationApi.getLatest 
  });
  
  const { data: h3Cells } = useQuery({ 
    queryKey: ['h3Cells'], 
    queryFn: gisApi.getHexCells 
  });

  const mutation = useMutation({
    mutationFn: (val: number) => optimizationApi.run(val),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['latestOptimization'] });
    }
  });

  return (
    <div className="flex h-full overflow-hidden">
      {/* Control Panel */}
      <div className="w-96 glass border-r h-full flex flex-col overflow-y-auto custom-scrollbar">
        <div className="p-8 space-y-8">
          <header>
            <h2 className="text-xl font-bold text-white flex items-center tracking-tight">
              <Calculator className="w-5 h-5 mr-3 text-blue-500" />
              Depot Selection
            </h2>
            <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
              Run mathematical models to determine the optimal facility locations based on Tirana's population density.
            </p>
          </header>

          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                  Target Facility Count
                </label>
                <span className="text-sm font-bold text-blue-400">{maxDepots}</span>
              </div>
              <input 
                type="range" 
                min="5" 
                max="25" 
                value={maxDepots}
                onChange={(e) => setMaxDepots(parseInt(e.target.value))}
                className="w-full accent-blue-500 bg-white/5 h-1.5 rounded-full appearance-none cursor-pointer"
              />
            </div>

            <div className="space-y-3">
              <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                Optimization Model
              </label>
              <select className="w-full bg-accent/50 border border-white/5 rounded-xl py-3 px-4 text-sm text-white focus:ring-1 focus:ring-blue-500 outline-none appearance-none">
                <option>Multi-Objective (Balanced)</option>
                <option>P-Median (Min Distance)</option>
                <option>P-Center (Fairness)</option>
                <option>Set Cover (Min Cost)</option>
              </select>
            </div>

            <button 
              onClick={() => mutation.mutate(maxDepots)}
              disabled={mutation.isPending}
              className={cn(
                "w-full py-4 rounded-xl font-bold text-sm flex items-center justify-center transition-all duration-300 shadow-lg shadow-blue-600/10",
                mutation.isPending 
                  ? "bg-muted text-muted-foreground cursor-not-allowed" 
                  : "bg-blue-600 hover:bg-blue-500 text-white"
              )}
            >
              {mutation.isPending ? (
                <span className="flex items-center">
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin mr-2"></div>
                  Optimizing Network...
                </span>
              ) : (
                <span className="flex items-center">
                  <Play className="w-4 h-4 mr-2" />
                  Run Optimization Engine
                </span>
              )}
            </button>
          </div>

          <div className="pt-8 border-t border-white/5 space-y-6">
            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Strategy Metrics</h3>
            
            {latestOpt ? (
              <div className="space-y-4">
                <MetricRow label="Method" value={latestOpt.method} />
                <MetricRow label="Pop. Served" value={latestOpt.data.total_population_served.toLocaleString()} />
                <MetricRow label="Coverage" value={`${((latestOpt.data.total_population_served / 807029) * 100).toFixed(2)}%`} />
                <MetricRow label="Avg. Distance" value={`${(latestOpt.data.avg_distance / 1000).toFixed(2)} km`} />
                <MetricRow label="Total Cost" value={`$${(latestOpt.data.total_cost / 1000).toFixed(0)}k`} />
              </div>
            ) : (
              <div className="p-6 rounded-2xl bg-white/5 border border-dashed flex flex-col items-center text-center">
                <Info className="w-8 h-8 text-muted-foreground mb-3 opacity-20" />
                <p className="text-xs text-muted-foreground">No active deployment found. Initialize a new strategy to begin.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Map View */}
      <div className="flex-1 relative">
        <TiranaMap 
          h3Cells={h3Cells}
          depots={latestOpt?.data?.depots}
        />
        
        {/* Legend */}
        <div className="absolute top-8 left-8 glass p-6 rounded-2xl border space-y-4 pointer-events-none">
          <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Map Legend</h4>
          <div className="space-y-3">
            <LegendItem color="bg-blue-500" label="Active Depot" />
            <LegendItem color="bg-red-500" label="High Demand Zone" />
            <LegendItem color="bg-green-500" label="Sufficient Coverage" />
            <LegendItem color="bg-white/10" label="Study Area" />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricRow({ label, value }: any) {
  return (
    <div className="flex justify-between items-center group">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">{value}</span>
    </div>
  );
}

function LegendItem({ color, label }: any) {
  return (
    <div className="flex items-center space-x-3">
      <div className={cn("w-3 h-3 rounded-full", color)}></div>
      <span className="text-xs font-medium text-white">{label}</span>
    </div>
  );
}
