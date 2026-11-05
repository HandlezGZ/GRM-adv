import React from 'react';
import { Activity, ShieldCheck, RefreshCw } from 'lucide-react';

export default function Navbar({ activeTab, onSelectTab, apiHealth, onRefreshHealth }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'benchmark', label: 'Executar Benchmark' },
    { id: 'comparison', label: 'Comparador A/B' },
    { id: 'failures', label: 'Catálogo de Falhas' },
    { id: 'datasets', label: 'Golden Datasets' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-base tracking-tight text-slate-100">
                  LexEval
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Continuous AI Evaluation & Quality Monitoring
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 sm:space-x-2">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onSelectTab(tab.id)}
                  className={`px-3 py-2 text-xs sm:text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/60'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Health Indicator */}
          <div className="flex items-center space-x-2">
            <div
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${
                apiHealth === 'healthy'
                  ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
                  : apiHealth === 'checking'
                  ? 'bg-slate-900 border-slate-800 text-slate-400'
                  : 'bg-rose-950/40 border-rose-800 text-rose-400'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  apiHealth === 'healthy'
                    ? 'bg-emerald-500 animate-pulse'
                    : apiHealth === 'checking'
                    ? 'bg-slate-500 animate-spin'
                    : 'bg-rose-500'
                }`}
              />
              <span className="hidden md:inline">
                {apiHealth === 'healthy'
                  ? 'API Online (8001)'
                  : apiHealth === 'checking'
                  ? 'Verificando...'
                  : 'API Offline'}
              </span>
            </div>
            {onRefreshHealth && (
              <button
                onClick={onRefreshHealth}
                title="Recarregar status da API"
                className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
