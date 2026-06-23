import { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { LoadingState } from './components/ui';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const GISOverview = lazy(() => import('./pages/GISOverview'));
const DepotOptimization = lazy(() => import('./pages/DepotOptimization'));
const FleetOperations = lazy(() => import('./pages/FleetOperations'));

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="relative flex min-h-dvh w-full overflow-hidden bg-background text-foreground">
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <Header onMenuClick={() => setIsSidebarOpen(true)} />
          <main id="main-content" className="relative flex-1 overflow-hidden">
            <Suspense fallback={<RouteFallback />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/gis" element={<GISOverview />} />
                <Route path="/optimization" element={<DepotOptimization />} />
                <Route path="/fleet" element={<FleetOperations />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </div>
    </Router>
  );
}

function RouteFallback() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <LoadingState label="Preparing command workspace..." />
    </div>
  );
}

export default App;
