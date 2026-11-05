import React from 'react';
import {
  Scale,
  Layers,
  FileText,
  FileSpreadsheet,
  MessageSquare,
  Activity,
  CheckCircle2,
  AlertCircle,
  FileCheck2,
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  health,
  checkingHealth,
  onRefreshHealth,
  activeDocument,
}) {
  const tabs = [
    {
      id: 'central',
      label: 'Central de Documentos',
      icon: Layers,
      description: 'Portfólio & Ingestão',
    },
    {
      id: 'visualizador',
      label: 'Visualizador & Extração',
      icon: FileText,
      description: 'Texto Integral & Entidades',
    },
    {
      id: 'resumo',
      label: 'Resumo Executivo',
      icon: FileSpreadsheet,
      description: 'Prazos & Contingências',
    },
    {
      id: 'chat',
      label: 'Consulta com Fontes',
      icon: MessageSquare,
      description: 'Q&A Fundamentado',
    },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/10 border border-blue-500/20 text-blue-400">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold tracking-tight text-slate-100">
                  LexTax
                </span>
                <span className="rounded border border-slate-700 bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-medium tracking-wide uppercase text-slate-300">
                  Tax Intelligence
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Análise Documental & Auditoria Tributária Fundamentada
              </p>
            </div>
          </div>

          {/* Center Navigation Tabs */}
          <nav className="hidden md:flex items-center space-x-1 rounded-xl bg-slate-900/60 p-1 border border-slate-800/80">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Status & Active Doc Indicator */}
          <div className="flex items-center gap-3">
            {activeDocument && (
              <div className="hidden lg:flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/40 px-2.5 py-1 text-xs text-slate-300">
                <FileCheck2 className="h-3.5 w-3.5 text-blue-400" />
                <span className="max-w-[140px] truncate" title={activeDocument.filename}>
                  {activeDocument.filename}
                </span>
                <span className="rounded bg-slate-800 px-1 py-0.2 text-[10px] text-slate-400 font-mono">
                  {activeDocument.document_type}
                </span>
              </div>
            )}

            {/* Health Status Indicator */}
            <div
              className={`flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs transition-colors cursor-pointer ${
                health?.ok
                  ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300'
                  : 'border-amber-500/20 bg-amber-500/10 text-amber-300'
              }`}
              onClick={onRefreshHealth}
              title="Clique para verificar conexão com o backend FastAPI"
            >
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    health?.ok ? 'bg-emerald-400' : 'bg-amber-400'
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    health?.ok ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                />
              </span>
              <span className="font-mono text-[11px] font-medium hidden sm:inline">
                {checkingHealth ? 'Verificando...' : health?.ok ? 'FastAPI Online' : 'Modo Simulação'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation bar */}
        <div className="flex md:hidden overflow-x-auto py-2 gap-1 border-t border-slate-800/60 no-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
