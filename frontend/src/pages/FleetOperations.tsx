import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fleetApi, optimizationApi } from '../services/api';
import { 
  Activity, Battery, CheckCircle2, MapPin, MoreVertical, Plane, Plus, ShieldAlert, Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { EmptyState, ErrorState, LoadingState, MetricCard, PageFrame, Panel, SectionHeader, staggerContainer } from '@/components/ui';
import type { Drone } from '@/types';

export default function FleetOperations() {
  const queryClient = useQueryClient();
  const { data: fleet, isLoading: isFleetLoading, isError: isFleetError } = useQuery({ 
    queryKey: ['fleet'], 
    queryFn: fleetApi.getStatus 
  });
  
  const { data: latestOpt, isLoading: isOptimizationLoading, isError: isOptimizationError } = useQuery({ 
    queryKey: ['latestOptimization'], 
    queryFn: optimizationApi.getLatest 
  });

  const initMutation = useMutation({
    mutationFn: ({ depotId, count }: { depotId: string; count: number }) => fleetApi.initialize(depotId, count),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleet'] });
    }
  });

  const activeFleet = fleet ?? [];
  const inFlight = activeFleet.filter((drone) => drone.status === 'EN_ROUTE').length;
  const available = activeFleet.filter((drone) => drone.status === 'AVAILABLE').length;
  const avgSoc = activeFleet.length
    ? Math.round((activeFleet.reduce((sum, drone) => sum + (drone.battery?.soc ?? 0), 0) / activeFleet.length) * 100)
    : 0;

  return (
    <PageFrame>
      <div className="space-y-8 p-4 md:p-6 lg:p-8">
        <SectionHeader
          eyebrow="UAV readiness"
          title="Fleet Operations Center"
          description="Real-time telemetry and deployment controls for drones staged across the current depot plan."
          icon={Plane}
        />

        {(isFleetError || isOptimizationError || initMutation.isError) ? (
          <ErrorState message="Fleet services are not fully reachable. Deployment actions will recover automatically after the API reconnects." />
        ) : null}

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
        >
          <MetricCard icon={Plane} label="Total Assets" value={activeFleet.length || 'Standby'} detail="Registered drones in the active fleet." tone="blue" />
          <MetricCard icon={Zap} label="In Flight" value={inFlight} detail="Aircraft currently assigned to missions." tone="orange" />
          <MetricCard icon={CheckCircle2} label="Available" value={available} detail="Ready for immediate dispatch." tone="green" />
          <MetricCard icon={Battery} label="Avg SOC" value={avgSoc ? `${avgSoc}%` : 'N/A'} detail="Battery state of charge across fleet." tone="cyan" />
        </motion.div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.8fr)]">
          <motion.section variants={staggerContainer} initial="hidden" animate="show" className="space-y-5">
            <div className="flex items-center justify-between px-1">
              <h2 className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">Operational Depots</h2>
              <span className="text-xs font-semibold text-slate-400">{latestOpt?.data?.depots?.length ?? 0} online</span>
            </div>
          
            {isOptimizationLoading ? <LoadingState label="Loading depot status..." /> : null}

            {latestOpt?.data?.depots?.map((depot) => (
              <Panel key={depot.id} className="p-5" motionProps={{ whileHover: { y: -3 }, transition: { duration: 0.2 } }}>
              <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex items-center">
                  <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-300">
                    <MapPin className="h-6 w-6" aria-hidden="true" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-white">{depot.id}</h4>
                    <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">Coord: {depot.lat.toFixed(4)}, {depot.lng.toFixed(4)}</p>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button 
                    type="button"
                    onClick={() => initMutation.mutate({ depotId: depot.id, count: 5 })}
                    disabled={initMutation.isPending}
                    className="focus-ring flex min-h-11 items-center rounded-2xl border border-white/10 bg-white/[0.05] px-4 py-2 text-xs font-bold text-white transition hover:bg-white/[0.09] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <Plus className="mr-2 h-3 w-3" aria-hidden="true" />
                    {initMutation.isPending ? 'Deploying...' : 'Deploy 5 drones'}
                  </button>
                  <button
                    type="button"
                    className="focus-ring flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.05] transition hover:bg-white/[0.09] active:scale-95"
                    aria-label={`Open ${depot.id} actions`}
                  >
                    <MoreVertical className="h-4 w-4 text-slate-400" aria-hidden="true" />
                  </button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <MiniStat label="Utilization" value="78%" />
                <MiniStat label="Charging" value="2" />
                <MiniStat label="Ready" value="3" />
                <MiniStat label="Health" value="98.5%" />
              </div>
              </Panel>
            ))}
          
            {(!latestOpt || latestOpt.data.depots.length === 0) && !isOptimizationLoading ? (
              <EmptyState
                icon={ShieldAlert}
                title="No active depots"
                description="Run the optimization engine before deploying UAV assets to infrastructure."
              />
            ) : null}
          </motion.section>

          <Panel className="flex max-h-[720px] flex-col overflow-hidden">
            <header className="border-b border-white/10 bg-white/[0.04] p-6">
              <h2 className="flex items-center text-xs font-bold uppercase tracking-[0.22em] text-white">
              <Activity className="mr-2 h-4 w-4 text-red-300" aria-hidden="true" />
              Live Telemetry
              </h2>
          </header>
          
            <div className="flex-1 space-y-4 overflow-y-auto p-5 custom-scrollbar">
              {isFleetLoading ? <LoadingState label="Loading live telemetry..." /> : null}

              {activeFleet.map((drone) => (
                <TelemetryRow key={drone.id} drone={drone} />
              ))}
            
              {!activeFleet.length && !isFleetLoading ? (
                <EmptyState
                  icon={Battery}
                  title="Waiting for fleet deployment"
                  description="Deploy drones from a depot to begin streaming telemetry and battery health."
                />
              ) : null}
            </div>
          </Panel>
        </div>
      </div>
    </PageFrame>
  );
}

function TelemetryRow({ drone }: { drone: Drone }) {
  const soc = Math.round((drone.battery?.soc ?? 0) * 100);
  const isLowBattery = soc < 30;

  return (
    <motion.article
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.28, ease: 'easeOut' }}
      className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.04] p-4 transition hover:border-blue-400/30 hover:bg-white/[0.07]"
    >
                <div className="flex items-center">
                  <div className={cn(
                    "mr-4 h-2.5 w-2.5 rounded-full",
                    drone.status === 'EN_ROUTE' ? "bg-yellow-500" : "bg-green-500"
                  )} />
                  <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-white">{drone.id}</p>
          <p className="mt-1 text-xs text-slate-400">SOC: {soc}% | {drone.status}</p>
                  </div>
                </div>
                <Battery className={cn(
        "h-5 w-5",
        isLowBattery ? "text-red-300" : "text-slate-400"
      )} aria-hidden="true" />
    </motion.article>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="text-sm font-bold text-white">{value}</p>
    </div>
  );
}
