import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import GISOverview from './pages/GISOverview';
import DepotOptimization from './pages/DepotOptimization';
import FleetOperations from './pages/FleetOperations';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <div className="flex h-screen w-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Header />
          <main className="flex-1 relative overflow-hidden">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/gis" element={<GISOverview />} />
              <Route path="/optimization" element={<DepotOptimization />} />
              <Route path="/fleet" element={<FleetOperations />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
