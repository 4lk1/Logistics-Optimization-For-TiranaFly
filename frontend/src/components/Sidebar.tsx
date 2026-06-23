import { NavLink } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { 
  LayoutDashboard, Map, Calculator, Plane, 
  Battery, Activity, Settings, Shield, X, RadioTower
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Map, label: 'GIS Overview', path: '/gis' },
  { icon: Calculator, label: 'Optimization', path: '/optimization' },
  { icon: Plane, label: 'Fleet Ops', path: '/fleet' },
];

const plannedItems = [
  { icon: Battery, label: 'Battery Labs' },
  { icon: Activity, label: 'Scenario Simulations' },
  { icon: Shield, label: 'No-Fly Intelligence' },
  { icon: Settings, label: 'Control Settings' },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      <AnimatePresence>
        {isOpen ? (
          <motion.button
            type="button"
            className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm lg:hidden"
            aria-label="Close navigation overlay"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        ) : null}
      </AnimatePresence>

      <aside
        className={cn(
          'glass fixed inset-y-0 left-0 z-50 flex w-[19rem] -translate-x-full flex-col border-r transition-transform duration-300 ease-out lg:static lg:z-auto lg:h-dvh lg:translate-x-0',
          isOpen && 'translate-x-0'
        )}
        aria-label="Primary navigation"
      >
        <div className="flex items-start justify-between p-6">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-500 text-white shadow-lg shadow-blue-500/20">
                <RadioTower className="h-5 w-5" aria-hidden="true" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Tirana<span className="text-blue-300">Fly</span>
                </h1>
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-slate-400">
                  Logistics Control
                </p>
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="focus-ring inline-flex h-10 w-10 items-center justify-center rounded-2xl text-slate-400 transition hover:bg-white/[0.07] hover:text-white lg:hidden"
            aria-label="Close navigation menu"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <div className="mx-6 rounded-3xl border border-blue-400/20 bg-blue-500/10 p-4">
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-blue-200">Tonight Objective</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">
            Balance depot placement, battery health, and live UAV coverage for the Tirana demand grid.
          </p>
        </div>
      
        <nav className="mt-6 flex-1 space-y-2 px-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }: { isActive: boolean }) => cn(
                'focus-ring group flex min-h-12 items-center rounded-2xl px-4 py-3 text-sm font-semibold transition-all duration-200',
                isActive 
                  ? 'border border-blue-400/30 bg-blue-500/15 text-blue-100 shadow-lg shadow-blue-950/20' 
                  : 'text-slate-400 hover:bg-white/[0.06] hover:text-white'
              )}
            >
              <item.icon className="mr-3 h-5 w-5" aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-4 pb-4">
          <p className="px-2 text-[10px] font-bold uppercase tracking-[0.22em] text-slate-500">Planned modules</p>
          <div className="mt-3 space-y-2">
            {plannedItems.map((item) => (
              <button
                type="button"
                key={item.label}
                disabled
                className="flex w-full min-h-11 cursor-not-allowed items-center rounded-2xl px-4 py-3 text-left text-sm font-medium text-slate-600"
              >
                <item.icon className="mr-3 h-4 w-4" aria-hidden="true" />
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-white/5 p-6">
          <div className="mb-5 grid grid-cols-2 gap-3">
            <div className="rounded-2xl bg-white/[0.04] p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Latency</p>
              <p className="mt-1 text-lg font-semibold text-white">4.2m</p>
            </div>
            <div className="rounded-2xl bg-white/[0.04] p-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Uptime</p>
              <p className="mt-1 text-lg font-semibold text-emerald-300">99.9%</p>
            </div>
          </div>
          <div className="flex items-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 text-xs font-bold text-white">
            LA
          </div>
          <div className="ml-3 min-w-0 overflow-hidden">
            <p className="truncate text-sm font-semibold text-white">Lead Architect</p>
            <p className="truncate text-xs text-slate-400">Operations Admin</p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
}
