import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { gisApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { Map, Users, Layers, Info } from 'lucide-react';
import { useStore } from '../store/useStore';

export default function GISOverview() {
  const { layers, toggleLayer } = useStore();
  const { data: adminUnits } = useQuery({ queryKey: ['adminUnits'], queryFn: gisApi.getAdminUnits });
  const { data: h3Cells } = useQuery({ queryKey: ['h3Cells'], queryFn: gisApi.getHexCells });

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sidebar Controls */}
      <div className="w-80 glass border-r h-full flex flex-col overflow-y-auto custom-scrollbar">
        <div className="p-8 space-y-8">
          <header>
            <h2 className="text-xl font-bold text-white flex items-center tracking-tight">
              <Map className="w-5 h-5 mr-3 text-blue-500" />
              GIS Repository
            </h2>
            <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
              Spatial inventory of Tirana's administrative structure and high-resolution population grid.
            </p>
          </header>

          <div className="space-y-6">
            <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Layer Visibility</h3>
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
          </div>

          <div className="pt-8 border-t border-white/5 space-y-6">
            <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">Regional Stats</h3>
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-muted-foreground">Admin Units</span>
                  <span className="text-sm font-bold text-white">14</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Total Area</span>
                  <span className="text-sm font-bold text-white">1,110 km²</span>
                </div>
              </div>
              
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                <div className="flex items-center mb-2">
                  <Users className="w-3 h-3 text-blue-400 mr-2" />
                  <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Census 2023</span>
                </div>
                <p className="text-xl font-bold text-white">807,029</p>
                <p className="text-[10px] text-blue-400/60 uppercase font-medium mt-1">Verified Residents</p>
              </div>
            </div>
          </div>
          
          <div className="p-6 rounded-2xl bg-yellow-500/5 border border-yellow-500/10 flex items-start">
            <Info className="w-4 h-4 text-yellow-500 mr-3 shrink-0 mt-0.5" />
            <p className="text-[10px] text-yellow-500/80 leading-relaxed font-medium">
              Spatial data is synchronized with the National Agency for Information Society (AKSHI) datasets.
            </p>
          </div>
        </div>
      </div>

      {/* Main Map */}
      <div className="flex-1 relative">
        <TiranaMap 
          boundaries={adminUnits}
          h3Cells={h3Cells}
        />
        
        {/* Layer Info Overlay */}
        <div className="absolute bottom-8 left-8 flex space-x-4 pointer-events-none">
          <div className="glass px-4 py-2 rounded-lg border flex items-center space-x-3">
            <div className="w-2 h-2 rounded-full bg-blue-400"></div>
            <span className="text-[10px] font-bold text-white uppercase tracking-widest">EPSG:4326 (WGS 84)</span>
          </div>
          <div className="glass px-4 py-2 rounded-lg border flex items-center space-x-3">
            <div className="w-2 h-2 rounded-full bg-green-400"></div>
            <span className="text-[10px] font-bold text-white uppercase tracking-widest">Res 9 (0.1 km²)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function LayerToggle({ label, active, onClick }: any) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all duration-200 group ${
        active 
          ? "bg-blue-600/10 border-blue-600/30 text-white" 
          : "bg-white/5 border-white/5 text-muted-foreground hover:bg-white/10 hover:text-white"
      }`}
    >
      <span className="text-xs font-medium tracking-tight">{label}</span>
      <div className={`w-8 h-4 rounded-full relative transition-colors ${active ? "bg-blue-500" : "bg-white/10"}`}>
        <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all shadow-sm ${active ? "left-4.5" : "left-0.5"}`}></div>
      </div>
    </button>
  );
}
