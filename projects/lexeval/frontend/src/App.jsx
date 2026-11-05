import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import BenchmarkView from './components/BenchmarkView';
import ComparisonView from './components/ComparisonView';
import FailuresView from './components/FailuresView';
import DatasetsView from './components/DatasetsView';
import { api } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiHealth, setApiHealth] = useState('checking'); // 'healthy', 'unhealthy', 'checking'
  const [preselectedCompareRunId, setPreselectedCompareRunId] = useState(null);

  const checkHealth = async () => {
    try {
      setApiHealth('checking');
      const res = await api.getHealth();
      if (res && res.status === 'healthy') {
        setApiHealth('healthy');
      } else {
        setApiHealth('unhealthy');
      }
    } catch {
      setApiHealth('unhealthy');
    }
  };

  useEffect(() => {
    checkHealth();
    // Poll health periodically every 30s
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectRunForCompare = (runId) => {
    setPreselectedCompareRunId(runId);
    setActiveTab('comparison');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        apiHealth={apiHealth}
        onRefreshHealth={checkHealth}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <DashboardView
            onNavigateToBenchmark={() => setActiveTab('benchmark')}
            onSelectRunForCompare={handleSelectRunForCompare}
          />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkView />
        )}

        {activeTab === 'comparison' && (
          <ComparisonView preselectedRunAId={preselectedCompareRunId} />
        )}

        {activeTab === 'failures' && (
          <FailuresView />
        )}

        {activeTab === 'datasets' && (
          <DatasetsView />
        )}
      </main>

      {/* Subtle Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-[11px]">
          <span>LexEval Continuous AI Evaluation Engine</span>
          <span>FastAPI Backend - React Frontend - Deterministic & Factual Guardrails</span>
        </div>
      </footer>
    </div>
  );
}
