import { motion } from 'framer-motion';
import { Bell, Info, Menu, Search, Signal, Wifi } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="glass z-30 flex min-h-16 items-center justify-between gap-4 border-b px-4 py-3 md:px-6 lg:px-8">
      <a
        href="#main-content"
        className="focus-ring sr-only rounded-full bg-blue-500 px-4 py-2 text-sm font-semibold text-white focus:not-sr-only"
      >
        Skip to main content
      </a>

      <div className="flex min-w-0 flex-1 items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="focus-ring inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] text-slate-200 transition hover:bg-white/[0.08] active:scale-95 lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="relative w-full max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <label htmlFor="global-search" className="sr-only">
            Search network, drones, or H3 cells
          </label>
          <input
            id="global-search"
            type="text" 
            placeholder="Search network, drones, or H3 cells..." 
            className="focus-ring h-11 w-full rounded-full border border-white/10 bg-white/[0.05] py-2 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-slate-500 hover:bg-white/[0.07]"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-2 md:gap-5">
        <div className="hidden items-center gap-4 border-r border-white/10 pr-5 xl:flex">
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="flex items-center space-x-2 text-emerald-300"
          >
            <Wifi className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-[0.2em]">System Online</span>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.08 }}
            className="flex items-center space-x-2 text-blue-300"
          >
            <Signal className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-[0.2em]">Network 5G Ready</span>
          </motion.div>
        </div>
        
        <button
          type="button"
          className="focus-ring relative inline-flex h-11 w-11 items-center justify-center rounded-2xl text-muted-foreground transition hover:bg-white/[0.07] hover:text-white active:scale-95"
          aria-label="Open alerts"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-background"></span>
        </button>
        
        <button
          type="button"
          className="focus-ring hidden h-11 w-11 items-center justify-center rounded-2xl text-muted-foreground transition hover:bg-white/[0.07] hover:text-white active:scale-95 sm:inline-flex"
          aria-label="Open system information"
        >
          <Info className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
