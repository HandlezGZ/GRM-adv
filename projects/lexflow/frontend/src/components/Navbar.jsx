import React from 'react';
import { Layers, Activity, RefreshCw } from 'lucide-react';

export default function Navbar({ activeTab, onSelectTab, health, onRefreshHealth, isHealthLoading }) {
  const tabs = [
    { id: 'dashboard', label: 'Visão Geral' },
    { id: 'intake', label: 'Nova Solicitação' },
    { id: 'requests', label: 'Solicitações' },
    { id: 'review', label: 'Revisão Humana' },
    { id: 'failures', label: 'Qualidade & Falhas' },
  ];

  const isOnline = health && health.status === 'healthy';

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-lg tracking-tight text-slate-100">LexFlow</span>
                <span className="text-[10px] uppercase font-mono tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                  v{health?.version || '1.0.0'}
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Process Automation & Request Triage</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center space-x-1">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onSelectTab(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/70'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Backend Status Indicator */}
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border ${
                isOnline
                  ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/50'
                  : 'bg-rose-950/40 text-rose-300 border-rose-800/50'
              }`}
              title={
                isOnline
                  ? `Backend Online (${health?.classification_mode || 'rules'})`
                  : 'Backend Offline em http://localhost:8000'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
                }`}
              />
              <span className="hidden sm:inline font-mono">
                {isOnline ? `API ${health?.classification_mode || 'Online'}` : 'API Offline'}
              </span>
            </div>

            <button
              onClick={onRefreshHealth}
              disabled={isHealthLoading}
              title="Recarregar status da API"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isHealthLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex space-x-1 overflow-x-auto py-2 border-t border-slate-900">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`px-3 py-1 rounded-md text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-800 text-slate-100 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
