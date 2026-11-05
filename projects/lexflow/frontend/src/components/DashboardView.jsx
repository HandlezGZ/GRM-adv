import React from 'react';
import { 
  Inbox, 
  Clock, 
  PlayCircle, 
  CheckCircle2, 
  Zap, 
  ArrowUpRight,
  Sparkles,
  Layers,
  ChevronRight,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { getPriorityMeta, getStatusMeta, formatDate } from '../constants';

export default function DashboardView({ metrics, recentRequests, onSelectRequest, onNavigateIntake, onNavigateRequests, isLoading, onRefresh }) {
  if (isLoading && !metrics) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-slate-400">Carregando indicadores consolidados...</p>
        </div>
      </div>
    );
  }

  const total = metrics?.total_requests || 0;
  const open = metrics?.open_requests || 0;
  const resolved = metrics?.resolved_requests || 0;
  const reviewed = metrics?.reviewed_count || 0;
  const failures = metrics?.ai_failure_count || 0;
  const inProgress = metrics?.by_status?.IN_PROGRESS || 0;

  // Automation rate calculated as requests handled without human correction or resolution rate
  const automationRate = total > 0 
    ? Math.max(0, Math.round(((total - reviewed) / total) * 100)) 
    : 100;

  const kpis = [
    {
      title: 'Total Solicitações',
      value: total,
      subtext: 'Volume total acumulado',
      icon: Inbox,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/20',
    },
    {
      title: 'Triagem Pendente',
      value: open,
      subtext: 'Aguardando classificação',
      icon: Clock,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
    },
    {
      title: 'Em Andamento',
      value: inProgress,
      subtext: 'Em execução pelas equipes',
      icon: PlayCircle,
      color: 'text-sky-400',
      bgColor: 'bg-sky-500/10',
      borderColor: 'border-sky-500/20',
    },
    {
      title: 'Concluídas',
      value: resolved,
      subtext: 'Demandas finalizadas',
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
    {
      title: 'Taxa de Automatização',
      value: `${automationRate}%`,
      subtext: `${reviewed} revisões humanas`,
      icon: Zap,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
    },
  ];

  const categoryEntries = Object.entries(metrics?.by_category || {});
  const priorityEntries = Object.entries(metrics?.by_priority || {});

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium tracking-tight text-slate-100">Visão Geral Operacional</h1>
          <p className="text-sm leading-relaxed text-slate-400">
            Painel em tempo real de triagem de demandas internas e automação jurídica.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onNavigateIntake}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            Nova Solicitação
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpis.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <div
              key={index}
              className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 hover:border-slate-700/80 transition-all duration-200"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{kpi.title}</span>
                <div className={`p-2 rounded-lg border ${kpi.bgColor} ${kpi.borderColor} ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-2xl font-bold tracking-tight text-slate-100">{kpi.value}</div>
                <div className="text-xs text-slate-400 mt-1">{kpi.subtext}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Distribution Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category distribution */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-medium tracking-tight text-slate-100">Distribuição por Categoria</h2>
            <span className="text-xs text-slate-400 font-mono">{categoryEntries.length} categorias</span>
          </div>

          {categoryEntries.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-400">
              Nenhuma solicitação categorizada no momento.
            </div>
          ) : (
            <div className="space-y-3">
              {categoryEntries.map(([cat, count]) => {
                const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-medium">{cat}</span>
                      <span className="text-slate-400 font-mono">{count} ({percentage}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800/80 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Priority distribution */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-medium tracking-tight text-slate-100">Distribuição por Prioridade</h2>
            <span className="text-xs text-slate-400 font-mono">{priorityEntries.length} níveis</span>
          </div>

          {priorityEntries.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-400">
              Nenhum dado de prioridade disponível.
            </div>
          ) : (
            <div className="space-y-3">
              {priorityEntries.map(([prio, count]) => {
                const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                const meta = getPriorityMeta(prio);
                const colorMap = {
                  LOW: 'bg-slate-400',
                  NORMAL: 'bg-blue-500',
                  HIGH: 'bg-amber-500',
                  URGENT: 'bg-rose-500',
                };
                const barColor = colorMap[prio] || 'bg-slate-500';

                return (
                  <div key={prio} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-300 font-medium">{meta.label}</span>
                      <span className="text-slate-400 font-mono">{count} ({percentage}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800/80 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${barColor} rounded-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Recent requests table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-medium tracking-tight text-slate-100">Solicitações Recentes</h2>
            <p className="text-xs text-slate-400 mt-0.5">Últimas demandas registradas no sistema</p>
          </div>
          <button
            onClick={onNavigateRequests}
            className="inline-flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            Ver todas
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {recentRequests.length === 0 ? (
          <div className="py-12 text-center text-sm text-slate-400 border border-dashed border-slate-800 rounded-lg">
            Nenhuma solicitação encontrada no momento.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-400 bg-slate-950/40 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-medium">Protocolo</th>
                  <th className="py-3 px-4 font-medium">Título</th>
                  <th className="py-3 px-4 font-medium">Solicitante</th>
                  <th className="py-3 px-4 font-medium">Prioridade</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                  <th className="py-3 px-4 font-medium">Data</th>
                  <th className="py-3 px-4 font-medium text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-normal">
                {recentRequests.slice(0, 5).map((req) => {
                  const prioMeta = getPriorityMeta(req.priority);
                  const statusMeta = getStatusMeta(req.status);

                  return (
                    <tr
                      key={req.id}
                      className="hover:bg-slate-800/30 transition-colors cursor-pointer"
                      onClick={() => onSelectRequest(req.id)}
                    >
                      <td className="py-3 px-4 font-mono text-xs text-indigo-400 font-medium">
                        {req.id.slice(0, 8)}
                      </td>
                      <td className="py-3 px-4 font-medium text-slate-200 max-w-xs truncate">
                        {req.title}
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400">
                        {req.requester_name || 'Não informado'}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${prioMeta.badgeClass}`}>
                          {prioMeta.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${statusMeta.badgeClass}`}>
                          {statusMeta.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400 whitespace-nowrap">
                        {formatDate(req.created_at)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectRequest(req.id);
                          }}
                          className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded hover:bg-slate-800 transition-colors"
                        >
                          Detalhes
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
