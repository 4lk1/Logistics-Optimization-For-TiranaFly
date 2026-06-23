import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { optimizationApi, gisApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { 
  Calculator, Download, Info, Play, SlidersHorizontal, Sparkles 
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { EmptyState, ErrorState, LoadingState, PageFrame, Panel, SectionHeader, fadeUp, staggerContainer } from '@/components/ui';

export default function DepotOptimization() {
  const queryClient = useQueryClient();
  const [maxDepots, setMaxDepots] = useState(10);
  
  const { data: latestOpt, isLoading: isLatestLoading, isError: isLatestError } = useQuery({ 
    queryKey: ['latestOptimization'], 
    queryFn: optimizationApi.getLatest 
  });
  
  const { data: h3Cells, isLoading: isCellsLoading } = useQuery({ 
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
    <PageFrame>
      <div className="grid min-h-full grid-cols-1 gap-6 p-4 md:p-6 lg:grid-cols-[400px_minmax(0,1fr)] lg:p-8">
        <motion.aside variants={staggerContainer} initial="hidden" animate="show" className="space-y-6">
          <SectionHeader
            eyebrow="Facility location model"
            title="Depot Selection"
            description="Tune constraints, run the optimizer, and inspect the resulting depot footprint against Tirana's demand surface."
            icon={Calculator}
          />

          {isLatestError ? (
            <ErrorState message="Latest optimization could not be loaded. You can still run a fresh model." />
          ) : null}

          <Panel className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="flex items-center text-xs font-bold uppercase tracking-[0.22em] text-slate-300">
                <SlidersHorizontal className="mr-2 h-4 w-4 text-blue-300" aria-hidden="true" />
                Optimization Controls
              </h2>
              <span className="rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-100">
                {maxDepots} facilities
              </span>
            </div>

            <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label htmlFor="depot-count" className="text-xs font-bold text-slate-400 uppercase tracking-[0.22em]">
                  Target Facility Count
                </label>
                <span className="text-sm font-bold text-blue-400">{maxDepots}</span>
              </div>
              <input 
                id="depot-count"
                type="range" 
                min="5" 
                max="25" 
                value={maxDepots}
                onChange={(e) => setMaxDepots(parseInt(e.target.value))}
                className="focus-ring h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-blue-400"
              />
            </div>

            <div className="space-y-3">
              <label htmlFor="optimization-model" className="text-xs font-bold text-slate-400 uppercase tracking-[0.22em]">
                Optimization Model
              </label>
              <select
                id="optimization-model"
                className="focus-ring w-full appearance-none rounded-2xl border border-white/10 bg-white/[0.05] px-4 py-3 text-sm text-white outline-none transition hover:bg-white/[0.07]"
              >
                <option>Multi-Objective (Balanced)</option>
                <option>P-Median (Min Distance)</option>
                <option>P-Center (Fairness)</option>
                <option>Set Cover (Min Cost)</option>
              </select>
            </div>

            <button 
              type="button"
              onClick={() => mutation.mutate(maxDepots)}
              disabled={mutation.isPending}
              className={cn(
                "focus-ring flex min-h-12 w-full items-center justify-center rounded-2xl py-4 text-sm font-bold shadow-lg shadow-blue-600/10 transition-all duration-200 active:scale-[0.98]",
                mutation.isPending 
                  ? "bg-muted text-muted-foreground cursor-not-allowed" 
                  : "bg-blue-600 text-white hover:bg-blue-500"
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
          </Panel>

          <Panel className="p-6">
            <h2 className="mb-5 flex items-center text-xs font-bold uppercase tracking-[0.22em] text-slate-300">
              <Sparkles className="mr-2 h-4 w-4 text-cyan-300" aria-hidden="true" />
              Strategy Metrics
            </h2>
            
            {isLatestLoading ? (
              <LoadingState label="Reading latest optimization..." />
            ) : latestOpt ? (
              <div className="space-y-4">
                <MetricRow label="Method" value={latestOpt.method} />
                <MetricRow label="Pop. Served" value={latestOpt.data.total_population_served.toLocaleString()} />
                <MetricRow label="Coverage" value={`${((latestOpt.data.total_population_served / 807029) * 100).toFixed(2)}%`} />
                <MetricRow label="Avg. Distance" value={`${(latestOpt.data.avg_distance / 1000).toFixed(2)} km`} />
                <MetricRow label="Total Cost" value={`$${(latestOpt.data.total_cost / 1000).toFixed(0)}k`} />
              </div>
            ) : (
              <EmptyState
                icon={Info}
                title="No active deployment"
                description="Initialize a new strategy to begin evaluating coverage, distance, and cost."
              />
            )}
          </Panel>

          <motion.button
            type="button"
            variants={fadeUp}
            className="focus-ring flex min-h-12 w-full items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08] active:scale-[0.98]"
          >
            <Download className="mr-2 h-4 w-4" aria-hidden="true" />
            Export strategy brief
          </motion.button>
        </motion.aside>

        <Panel className="relative min-h-[640px] overflow-hidden p-2">
          {(isCellsLoading || mutation.isPending) ? (
            <LoadingState label={mutation.isPending ? 'Optimizing depot placement...' : 'Loading demand grid...'} />
          ) : (
            <TiranaMap h3Cells={h3Cells} depots={latestOpt?.data?.depots} />
          )}
        
          <div className="pointer-events-none absolute left-5 top-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5 backdrop-blur-xl">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">Map Legend</h3>
            <div className="mt-4 space-y-3">
              <LegendItem color="bg-blue-400" label="Active Depot" />
              <LegendItem color="bg-red-400" label="High Demand Zone" />
              <LegendItem color="bg-emerald-400" label="Sufficient Coverage" />
              <LegendItem color="bg-white/20" label="Study Area" />
            </div>
          </div>
        </Panel>
      </div>
    </PageFrame>
  );
}

function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3">
      <span className="text-xs font-medium text-slate-400">{label}</span>
      <span className="text-sm font-bold text-white transition-colors group-hover:text-blue-300">{value}</span>
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center space-x-3">
      <div className={cn("h-3 w-3 rounded-full", color)} />
      <span className="text-xs font-semibold text-white">{label}</span>
    </div>
  );
}
