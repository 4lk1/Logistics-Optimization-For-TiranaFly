import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { gisApi, fleetApi, optimizationApi, simulationApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { 
  Activity, BarChart3, Battery, Clock, Loader2, MapPin, Navigation, Pause, Play, Route, ShieldCheck, ShoppingBag, Users
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';
import { EmptyState, ErrorState, MetricCard, PageFrame, Panel, SectionHeader, SkeletonBlock, fadeUp, staggerContainer } from '@/components/ui';
import type { Depot, HexCell, SimulationOrder } from '@/types';

const mockChartData = [
  { time: '08:00', orders: 120, drones: 15 },
  { time: '10:00', orders: 250, drones: 35 },
  { time: '12:00', orders: 480, drones: 85 },
  { time: '14:00', orders: 320, drones: 65 },
  { time: '16:00', orders: 410, drones: 75 },
  { time: '18:00', orders: 590, drones: 120 },
  { time: '20:00', orders: 380, drones: 90 },
];

export default function Dashboard() {
  const [simulationIterations, setSimulationIterations] = useState(250);
  const [replayProgress, setReplayProgress] = useState(0);
  const [isReplayPlaying, setIsReplayPlaying] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const { data: adminUnits, isLoading: isAdminLoading, isError: isAdminError } = useQuery({ queryKey: ['adminUnits'], queryFn: gisApi.getAdminUnits });
  const { data: h3Cells, isLoading: isGridLoading, isError: isGridError } = useQuery({ queryKey: ['h3Cells'], queryFn: gisApi.getHexCells });
  const { data: fleet, isLoading: isFleetLoading, isError: isFleetError } = useQuery({ queryKey: ['fleet'], queryFn: fleetApi.getStatus });
  const { data: latestOpt, isLoading: isOptimizationLoading, isError: isOptimizationError } = useQuery({ queryKey: ['latestOptimization'], queryFn: optimizationApi.getLatest });
  const simulationMutation = useMutation({
    mutationFn: () => simulationApi.run({
      iterations: simulationIterations,
      depot_count: Math.min(Math.max(depotCount || 3, 1), 10),
      fleet_pool: fleetCount || 65,
      replay_sample_size: 80,
    }),
    onSuccess: (result) => {
      setReplayProgress(0);
      setIsReplayPlaying(true);
      setSelectedOrderId(result.orders[0]?.id ?? null);
    },
  });

  const depotCount = latestOpt?.data?.depots?.length ?? 0;
  const fleetCount = fleet?.length ?? 0;
  const coverage = latestOpt?.data?.total_population_served
    ? `${((latestOpt.data.total_population_served / 807029) * 100).toFixed(1)}%`
    : 'Pending';
  const isLoading = isAdminLoading || isGridLoading || isFleetLoading || isOptimizationLoading;
  const replayOrders = simulationMutation.data?.orders ?? [];
  const selectedOrder = replayOrders.find((order) => order.id === selectedOrderId) ?? replayOrders[0];
  const coveredH3Cells = useMemo(() => assignCoverageToDepots(h3Cells, latestOpt?.data?.depots), [h3Cells, latestOpt?.data?.depots]);

  useEffect(() => {
    if (!isReplayPlaying || replayOrders.length === 0) return undefined;

    const interval = window.setInterval(() => {
      setReplayProgress((current) => {
        if (current >= 1) {
          setIsReplayPlaying(false);
          return 1;
        }

        return Math.min(current + 0.015, 1);
      });
    }, 120);

    return () => window.clearInterval(interval);
  }, [isReplayPlaying, replayOrders.length]);

  return (
    <PageFrame>
      <div className="space-y-8 p-4 md:p-6 lg:p-8">
        <SectionHeader
          eyebrow="Autonomous drone logistics"
          title="TiranaFly Command Center"
          description="A live operating picture for population demand, depot optimization, and UAV readiness across Tirana's administrative zones."
          icon={ShieldCheck}
          action={
            <div className="glass flex items-center gap-3 rounded-2xl px-4 py-3">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-300" />
              </span>
              <span className="text-sm font-semibold text-white">Operational confidence high</span>
            </div>
          }
        />

        {(isAdminError || isGridError || isFleetError || isOptimizationError || simulationMutation.isError) ? (
          <ErrorState message="Some live services are unreachable. The cockpit is showing resilient placeholders while the API recovers." />
        ) : null}

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
        >
          <MetricCard icon={Users} label="Total Population" value="807,029" detail="Verified residents in the service model." tone="blue" trend="+1.2% demand growth" />
          <MetricCard icon={MapPin} label="Active Depots" value={depotCount || 'Run model'} detail="Optimal infrastructure candidates." tone="green" trend="P-median ready" />
          <MetricCard icon={Navigation} label="Fleet Size" value={fleetCount || 'Standby'} detail="UAV assets synced to dispatch." tone="orange" trend="98% availability target" />
          <MetricCard icon={Activity} label="Coverage Index" value={coverage} detail="Population served by current strategy." tone="purple" trend="Reliability weighted" />
        </motion.div>

        <div className="grid min-h-[680px] grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(360px,0.8fr)]">
          <Panel className="relative min-h-[460px] overflow-hidden p-2">
            {isLoading ? (
              <div className="h-full min-h-[520px] p-3">
                <SkeletonBlock className="h-full min-h-[500px]" />
              </div>
            ) : (
              <TiranaMap
                boundaries={adminUnits}
                h3Cells={coveredH3Cells}
                depots={latestOpt?.data?.depots}
                simulationOrders={replayOrders}
                replayProgress={replayProgress}
                selectedOrderId={selectedOrder?.id}
              />
            )}

            <div className="pointer-events-none absolute left-5 top-5 max-w-xs rounded-2xl border border-white/10 bg-slate-950/70 p-4 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400 shadow-lg shadow-red-400/40" />
                <span className="text-xs font-bold uppercase tracking-[0.22em] text-white">Live Telemetry</span>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-300">Monitoring full H3 coverage with depot-centered service zones and replayable orders.</p>
            </div>

            <div className="pointer-events-none absolute bottom-5 left-5 right-5 grid gap-3 md:grid-cols-3">
              {[
                `${coveredH3Cells?.length ?? 0} H3 cells covered`,
                replayOrders.length ? `${replayOrders.length} replay orders loaded` : 'Run simulation for drone paths',
                selectedOrder ? `${selectedOrder.id} ${selectedOrder.status.toLowerCase()}` : 'Orders pending',
              ].map((label) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-xs font-semibold text-slate-200 backdrop-blur-xl">
                  {label}
                </div>
              ))}
            </div>
          </Panel>

          <motion.aside variants={staggerContainer} initial="hidden" animate="show" className="space-y-6">
            <Panel className="p-6">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="flex items-center text-sm font-bold uppercase tracking-[0.22em] text-white">
                  <BarChart3 className="mr-2 h-4 w-4 text-blue-300" aria-hidden="true" />
                  Network Load
                </h2>
                <Clock className="h-4 w-4 text-slate-500" aria-hidden="true" />
              </div>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
                    <XAxis dataKey="time" stroke="#94a3b8" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
                    <YAxis hide />
                    <Tooltip 
                      contentStyle={{ background: '#0f172a', border: '1px solid rgba(148,163,184,0.2)', borderRadius: '16px', color: '#fff' }}
                      itemStyle={{ fontSize: '12px' }}
                    />
                    <Line type="monotone" dataKey="orders" stroke="#60a5fa" strokeWidth={3} dot={false} />
                    <Line type="monotone" dataKey="drones" stroke="#fb923c" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Panel>

            <Panel className="p-6">
              <h2 className="mb-6 flex items-center text-sm font-bold uppercase tracking-[0.22em] text-white">
                <Battery className="mr-2 h-4 w-4 text-emerald-300" aria-hidden="true" />
                Fleet Status
              </h2>
              <div className="space-y-5">
                <StatusProgress label="En Route" value={65} color="bg-blue-400" />
                <StatusProgress label="Charging" value={22} color="bg-amber-400" />
                <StatusProgress label="Maintenance" value={8} color="bg-red-400" />
                <StatusProgress label="Ready" value={5} color="bg-emerald-400" />
              </div>
            </Panel>

            <Panel className="p-6">
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <h2 className="flex items-center text-sm font-bold uppercase tracking-[0.22em] text-white">
                    <Play className="mr-2 h-4 w-4 text-cyan-300" aria-hidden="true" />
                    Simulation Run
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Stress test the current depot and fleet plan against stochastic order demand.
                  </p>
                </div>
                <span className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-100">
                  {simulationIterations} runs
                </span>
              </div>

              <div className="space-y-5">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label htmlFor="simulation-iterations" className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                      Iterations
                    </label>
                    <span className="text-xs font-semibold text-slate-300">
                      {Math.min(Math.max(depotCount || 3, 1), 10)} depots / {fleetCount || 65} drones
                    </span>
                  </div>
                  <input
                    id="simulation-iterations"
                    type="range"
                    min="10"
                    max="1000"
                    step="10"
                    value={simulationIterations}
                    onChange={(event) => setSimulationIterations(Number(event.target.value))}
                    className="focus-ring h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-cyan-300"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => simulationMutation.mutate()}
                  disabled={simulationMutation.isPending || isLoading}
                  className="focus-ring flex min-h-12 w-full items-center justify-center rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-cyan-500/10 transition hover:bg-cyan-300 active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-white/10 disabled:text-slate-500"
                >
                  {simulationMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                      Running simulation...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" aria-hidden="true" />
                      Run Simulation
                    </>
                  )}
                </button>

                {simulationMutation.data ? (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <SimulationStat label="Success" value={`${simulationMutation.data.system_delivery_success_rate.toFixed(1)}%`} />
                      <SimulationStat label="Orders" value={simulationMutation.data.total_orders_processed.toLocaleString()} />
                      <SimulationStat label="Delivered" value={simulationMutation.data.successful_deliveries.toLocaleString()} />
                      <SimulationStat label="Failed" value={simulationMutation.data.failed_deliveries.toLocaleString()} />
                      <div className="col-span-2 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">Avg Wait</p>
                        <p className="mt-1 text-lg font-semibold text-white">
                          {(simulationMutation.data.average_delivery_wait_time_sec / 60).toFixed(1)} min
                        </p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                      <div className="mb-3 flex items-center justify-between">
                        <h3 className="flex items-center text-[10px] font-bold uppercase tracking-[0.18em] text-slate-300">
                          <Route className="mr-2 h-3.5 w-3.5 text-cyan-300" aria-hidden="true" />
                          Replay
                        </h3>
                        <button
                          type="button"
                          onClick={() => {
                            if (replayProgress >= 1) setReplayProgress(0);
                            setIsReplayPlaying((current) => !current);
                          }}
                          className="focus-ring rounded-xl border border-white/10 bg-white/[0.06] px-3 py-2 text-xs font-bold text-white transition hover:bg-white/[0.1]"
                        >
                          {isReplayPlaying ? (
                            <span className="flex items-center"><Pause className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" />Pause</span>
                          ) : (
                            <span className="flex items-center"><Play className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" />Play</span>
                          )}
                        </button>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={Math.round(replayProgress * 100)}
                        onChange={(event) => {
                          setIsReplayPlaying(false);
                          setReplayProgress(Number(event.target.value) / 100);
                        }}
                        className="focus-ring h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-cyan-300"
                        aria-label="Simulation replay progress"
                      />
                    </div>

                    <div className="max-h-72 space-y-2 overflow-y-auto pr-1 custom-scrollbar">
                      {replayOrders.map((order) => (
                        <OrderReplayRow
                          key={order.id}
                          order={order}
                          selected={order.id === selectedOrder?.id}
                          onSelect={() => setSelectedOrderId(order.id)}
                        />
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm leading-6 text-slate-400">
                    No run completed yet. Launch a simulation to populate delivery reliability KPIs.
                  </p>
                )}
              </div>
            </Panel>

            <Panel className="overflow-hidden">
              <div className="p-6">
                <h2 className="text-sm font-bold uppercase tracking-[0.22em] text-white">Service Resilience</h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">SLA posture calculated against current demand and route latency.</p>
              </div>
              <div className="grid grid-cols-3 border-t border-white/10">
                <ResilienceStat label="Uptime" value="99.9%" />
                <ResilienceStat label="Latency" value="4.2m" />
                <ResilienceStat label="Loss" value="0.02%" />
              </div>
            </Panel>

            {!depotCount && !isOptimizationLoading ? (
              <motion.div variants={fadeUp}>
                <EmptyState
                  title="No strategy committed"
                  description="Run the optimization engine to populate depot markers and coverage metrics."
                />
              </motion.div>
            ) : null}
          </motion.aside>
        </div>
      </div>
    </PageFrame>
  );
}

function StatusProgress({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] font-bold uppercase tracking-[0.18em]">
        <span className="text-slate-400">{label}</span>
        <span className="text-white">{value}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.65, ease: 'easeOut' }}
          className={`h-full ${color}`}
        />
      </div>
    </div>
  );
}

function ResilienceStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-r border-white/10 p-5 last:border-r-0">
      <p className="text-2xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</p>
    </div>
  );
}

function SimulationStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

function assignCoverageToDepots(cells?: HexCell[], depots?: Depot[]): HexCell[] | undefined {
  if (!cells) return undefined;
  if (!depots?.length) return cells;

  return cells.map((cell) => {
    const nearestDepot = depots.reduce((best, depot) => {
      const distance = Math.hypot(cell.centroid_lat - depot.lat, cell.centroid_lon - depot.lng);
      return distance < best.distance ? { depot, distance } : best;
    }, { depot: depots[0], distance: Number.POSITIVE_INFINITY });

    return {
      ...cell,
      coverage_depot_id: nearestDepot.depot.id,
    };
  });
}

function OrderReplayRow({
  order,
  selected,
  onSelect,
}: {
  order: SimulationOrder;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`focus-ring w-full rounded-2xl border p-3 text-left transition ${
        selected
          ? 'border-cyan-300/40 bg-cyan-400/10'
          : 'border-white/10 bg-white/[0.04] hover:bg-white/[0.08]'
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="flex items-center text-xs font-bold uppercase tracking-[0.16em] text-white">
          <ShoppingBag className="mr-2 h-3.5 w-3.5 text-cyan-300" aria-hidden="true" />
          {order.id}
        </span>
        <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase tracking-[0.14em] ${
          order.status === 'DELIVERED' ? 'bg-emerald-500/15 text-emerald-200' : 'bg-red-500/15 text-red-200'
        }`}>
          {order.status}
        </span>
      </div>
      <p className="mt-2 text-xs leading-5 text-slate-400">
        {order.drone_id} from {order.depot_id} / {order.distance_km.toFixed(1)} km
      </p>
    </button>
  );
}
