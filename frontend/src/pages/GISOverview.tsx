import { useQuery } from '@tanstack/react-query';
import { gisApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { motion } from 'framer-motion';
import { Database, Info, Layers, Map, ScanLine, Users } from 'lucide-react';
import { useStore } from '../store/useStore';
import { cn } from '@/lib/utils';
import { EmptyState, ErrorState, LoadingState, MetricCard, PageFrame, Panel, SectionHeader, fadeUp, staggerContainer } from '@/components/ui';

export default function GISOverview() {
  const { layers, toggleLayer } = useStore();
  const { data: adminUnits, isLoading: isAdminLoading, isError: isAdminError } = useQuery({ queryKey: ['adminUnits'], queryFn: gisApi.getAdminUnits });
  const { data: h3Cells, isLoading: isCellsLoading, isError: isCellsError } = useQuery({ queryKey: ['h3Cells'], queryFn: gisApi.getHexCells });

  return (
    <PageFrame>
      <div className="grid min-h-full grid-cols-1 gap-6 p-4 md:p-6 lg:grid-cols-[360px_minmax(0,1fr)] lg:p-8">
        <motion.aside variants={staggerContainer} initial="hidden" animate="show" className="space-y-6">
          <SectionHeader
            eyebrow="Spatial intelligence"
            title="GIS Repository"
            description="Curated map layers for boundaries, demand heat, and H3 population density."
            icon={Map}
          />

          {(isAdminError || isCellsError) ? (
            <ErrorState message="GIS services are offline. Layer controls remain available while map data reconnects." />
          ) : null}

          <Panel className="p-6">
            <h2 className="mb-5 flex items-center text-xs font-bold uppercase tracking-[0.22em] text-slate-300">
              <Layers className="mr-2 h-4 w-4 text-blue-300" aria-hidden="true" />
              Layer Visibility
            </h2>
            <div className="space-y-2">
              <LayerToggle 
                label="Municipality Boundary" 
                active={layers.boundaries} 
                onClick={() => toggleLayer('boundaries')} 
              />
              <LayerToggle 
                label="H3 Population Grid" 
                active={layers.h3} 
                onClick={() => toggleLayer('h3')} 
              />
              <LayerToggle 
                label="Demand Heatmap" 
                active={layers.population} 
                onClick={() => toggleLayer('population')} 
              />
            </div>
          </Panel>

          <motion.div variants={staggerContainer} className="grid grid-cols-1 gap-4">
            <MetricCard icon={Database} label="Admin Units" value={adminUnits?.length ?? 14} detail="Municipal zones in the boundary model." tone="cyan" />
            <MetricCard icon={Users} label="Census 2023" value="807,029" detail="Verified residents used for demand simulation." tone="blue" />
            <MetricCard icon={ScanLine} label="H3 Cells" value={h3Cells?.length ?? 'Pending'} detail="High-resolution population grid records." tone="green" />
          </motion.div>
          
          <motion.div variants={fadeUp} className="rounded-3xl border border-amber-400/20 bg-amber-500/10 p-5">
            <div className="flex items-start">
              <Info className="mr-3 mt-0.5 h-4 w-4 shrink-0 text-amber-300" aria-hidden="true" />
              <p className="text-sm leading-6 text-amber-100/90">
              Spatial data is synchronized with the National Agency for Information Society (AKSHI) datasets.
              </p>
            </div>
          </motion.div>
        </motion.aside>

        <Panel className="relative min-h-[640px] overflow-hidden p-2">
          {(isAdminLoading || isCellsLoading) ? (
            <LoadingState label="Loading GIS tiles and population grid..." />
          ) : (
            <TiranaMap boundaries={adminUnits} h3Cells={h3Cells} />
          )}
        
          <div className="pointer-events-none absolute bottom-5 left-5 right-5 flex flex-wrap gap-3">
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 backdrop-blur-xl">
              <div className="flex items-center space-x-3">
                <div className="h-2 w-2 rounded-full bg-blue-300" />
                <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-white">EPSG:4326 WGS 84</span>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 backdrop-blur-xl">
              <div className="flex items-center space-x-3">
                <div className="h-2 w-2 rounded-full bg-emerald-300" />
                <span className="text-[10px] font-bold uppercase tracking-[0.22em] text-white">H3 Res 8 / Full Coverage</span>
              </div>
            </div>
          </div>
        </Panel>

        {(!adminUnits && !h3Cells && !isAdminLoading && !isCellsLoading && !isAdminError && !isCellsError) ? (
          <div className="lg:col-start-2">
            <EmptyState title="No GIS records loaded" description="Initialize the GIS dataset to inspect boundaries and demand layers." />
          </div>
        ) : null}
      </div>
    </PageFrame>
  );
}

function LayerToggle({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button 
      type="button"
      onClick={onClick}
      className={`focus-ring group flex min-h-12 w-full items-center justify-between rounded-2xl border p-3 text-left transition-all duration-200 ${
        active 
          ? "border-blue-400/30 bg-blue-500/15 text-white" 
          : "border-white/10 bg-white/[0.04] text-slate-400 hover:bg-white/[0.08] hover:text-white"
      }`}
      aria-pressed={active}
    >
      <span className="text-sm font-semibold">{label}</span>
      <div className={cn('relative h-5 w-10 rounded-full transition-colors', active ? 'bg-blue-500' : 'bg-white/10')}>
        <motion.div
          layout
          className="absolute top-1 h-3 w-3 rounded-full bg-white shadow-sm"
          animate={{ left: active ? 22 : 4 }}
          transition={{ duration: 0.18, ease: 'easeOut' }}
        />
      </div>
    </button>
  );
}
