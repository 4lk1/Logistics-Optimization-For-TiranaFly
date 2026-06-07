import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Map, Calculator, Plane, 
  Battery, Activity, Settings, Shield 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Map, label: 'GIS Overview', path: '/gis' },
  { icon: Calculator, label: 'Optimization', path: '/optimization' },
  { icon: Plane, label: 'Fleet Ops', path: '/fleet' },
  { icon: Battery, label: 'Batteries', path: '/batteries' },
  { icon: Activity, label: 'Simulations', path: '/simulations' },
  { icon: Shield, label: 'No-Fly Zones', path: '/no-fly' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 glass h-full flex flex-col border-r">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Tirana<span className="text-blue-500">Fly</span>
        </h1>
        <p className="text-xs text-muted-foreground uppercase tracking-widest mt-1">
          Logistics Control
        </p>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }: { isActive: boolean }) => cn(
              "flex items-center px-4 py-3 rounded-lg transition-all duration-200 group",
              isActive 
                ? "bg-blue-600/20 text-blue-400 border border-blue-600/30" 
                : "text-muted-foreground hover:bg-accent hover:text-white"
            )}
          >
            <item.icon className="w-5 h-5 mr-3" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-6 border-t border-white/5">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">
            LA
          </div>
          <div className="ml-3 overflow-hidden">
            <p className="text-sm font-medium text-white truncate">Lead Architect</p>
            <p className="text-xs text-muted-foreground truncate">Admin Role</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
