import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { gisApi, fleetApi, optimizationApi } from '../services/api';
import TiranaMap from '../maps/TiranaMap';
import { 
  Users, MapPin, Navigation, Battery, 
  BarChart3, Activity, Clock 
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, BarChart, Bar 
} from 'recharts';

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
  const { data: adminUnits } = useQuery({ queryKey: ['adminUnits'], queryFn: gisApi.getAdminUnits });
  const { data: h3Cells } = useQuery({ queryKey: ['h3Cells'], queryFn: gisApi.getHexCells });
  const { data: fleet } = useQuery({ queryKey: ['fleet'], queryFn: fleetApi.getStatus });
  const { data: latestOpt } = useQuery({ queryKey: ['latestOptimization'], queryFn: optimizationApi.getLatest });

  return (
    <div className="flex flex-col h-full">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-8">
        <StatCard 
          icon={Users} 
          label="Total Population" 
          value="807,029" 
          subValue="+1.2% growth"
          color="blue"
        />
        <StatCard 
          icon={MapPin} 
          label="Active Depots" 
          value={latestOpt?.data?.depots?.length || "0"} 
          subValue="Optimal deployment"
          color="green"
        />
        <StatCard 
          icon={Navigation} 
          label="Fleet Size" 
          value={fleet?.length || "0"} 
          subValue="98% availability"
          color="orange"
        />
        <StatCard 
          icon={Activity} 
          label="Coverage Index" 
          value={`${((latestOpt?.data?.total_population_served || 0) / 807029 * 100).toFixed(1)}%`} 
          subValue="Service reliability"
          color="purple"
        />
      </div>

      <div className="flex-1 flex min-h-0">
        {/* Map Section */}
        <div className="flex-[2] relative p-8 pr-4">
          <div className="w-full h-full rounded-2xl overflow-hidden border shadow-2xl relative">
            <TiranaMap 
              h3Cells={h3Cells}
              depots={latestOpt?.data?.depots}
            />
            
            {/* Map Overlay Stats */}
            <div className="absolute top-4 left-4 glass p-4 rounded-xl space-y-2 pointer-events-none">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                <span className="text-xs font-bold text-white uppercase tracking-tighter">Live Telemetry</span>
              </div>
              <p className="text-[10px] text-muted-foreground">Monitoring 14 administrative zones</p>
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="flex-1 p-8 pl-4 space-y-6 overflow-y-auto custom-scrollbar">
          <div className="glass p-6 rounded-2xl border">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold text-white uppercase tracking-widest flex items-center">
                <BarChart3 className="w-4 h-4 mr-2 text-blue-500" />
                Network Load
              </h3>
              <Clock className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                  <XAxis dataKey="time" hide />
                  <YAxis hide />
                  <Tooltip 
                    contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                    itemStyle={{ fontSize: '12px' }}
                  />
                  <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="drones" stroke="#f59e0b" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass p-6 rounded-2xl border">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center">
              <Battery className="w-4 h-4 mr-2 text-green-500" />
              Fleet Status
            </h3>
            <div className="space-y-4">
              <StatusProgress label="En Route" value={65} color="bg-blue-500" />
              <StatusProgress label="Charging" value={22} color="bg-yellow-500" />
              <StatusProgress label="Maintenance" value={8} color="bg-red-500" />
              <StatusProgress label="Ready" value={5} color="bg-green-500" />
            </div>
          </div>

          <div className="glass p-6 rounded-2xl border">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-4">Service Resilience</h3>
            <div className="flex items-center space-x-4">
              <div className="flex-1 text-center border-r border-white/5">
                <p className="text-2xl font-bold text-white">99.9</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-tighter">Uptime %</p>
              </div>
              <div className="flex-1 text-center border-r border-white/5">
                <p className="text-2xl font-bold text-white">4.2</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-tighter">Avg Latency (m)</p>
              </div>
              <div className="flex-1 text-center">
                <p className="text-2xl font-bold text-white">0.02</p>
                <p className="text-[10px] text-muted-foreground uppercase tracking-tighter">Loss Rate %</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, subValue, color }: any) {
  const colors: any = {
    blue: "text-blue-500 bg-blue-500/10",
    green: "text-green-500 bg-green-500/10",
    orange: "text-orange-500 bg-orange-500/10",
    purple: "text-purple-500 bg-purple-500/10",
  };

  return (
    <div className="glass p-6 rounded-2xl border hover:border-white/20 transition-all group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-widest mb-1">{label}</p>
          <h4 className="text-2xl font-bold text-white tracking-tight">{value}</h4>
          <p className="text-[10px] text-muted-foreground mt-1 font-medium">{subValue}</p>
        </div>
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}

function StatusProgress({ label, value, color }: any) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] uppercase font-bold tracking-tighter">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-white">{value}%</span>
      </div>
      <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-1000`} 
          style={{ width: `${value}%` }}
        ></div>
      </div>
    </div>
  );
}
