import React from 'react';
import { Bell, Search, Info, Wifi, Signal } from 'lucide-react';

export default function Header() {
  return (
    <header className="h-16 border-b glass flex items-center justify-between px-8 z-10">
      <div className="flex items-center flex-1">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search network, drones, or H3 cells..." 
            className="w-full bg-accent/50 border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-1 focus:ring-blue-500 transition-all outline-none"
          />
        </div>
      </div>
      
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-4 border-r pr-6 border-white/10">
          <div className="flex items-center space-x-2 text-green-500">
            <Wifi className="w-4 h-4" />
            <span className="text-xs font-medium uppercase tracking-tighter">System Online</span>
          </div>
          <div className="flex items-center space-x-2 text-blue-400">
            <Signal className="w-4 h-4" />
            <span className="text-xs font-medium uppercase tracking-tighter">Network 5G Ready</span>
          </div>
        </div>
        
        <button className="relative p-2 text-muted-foreground hover:text-white transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-background"></span>
        </button>
        
        <button className="p-2 text-muted-foreground hover:text-white transition-colors">
          <Info className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
