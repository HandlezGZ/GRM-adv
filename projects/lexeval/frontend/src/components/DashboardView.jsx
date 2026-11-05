import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Activity, 
  Target, 
  AlertCircle,
  RefreshCw,
  ChevronRight,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';

export default function DashboardView({ onNavigateToBenchmark, onSelectRunForCompare }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err.message || 'Falha ao carregar métricas do dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const passRate = metrics?.avg_pass_rate ? (metrics.avg_pass_rate * 100).toFixed(1) : '0.0';
  const avgFaithfulness = metrics?.avg_faithfulness ? (metrics.avg_faithfulness * 100).toFixed(1) : '0.0';
  const totalRuns = metrics?.total_runs ?? 0;
  const totalCases = metrics?.total_cases_evaluated ?? 0;
  const totalFailures = metrics?.total_failures ?? 0;
  const recentRuns = metrics?.recent_runs || [];

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-xl sm:text-2xl font-medium tracking-tight text-slate-100">
            Painel Geral de Avaliação Contínua
          </h1>
          <p className="text-sm leading-relaxed text-slate-400 mt-1">
            Monitoramento de fidelidade fática, taxa de conformidade e integridade dos modelos.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchMetrics}
            disabled={loading}
            className="inline-flex items-center space-x-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-slate-100 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Atualizar</span>
          </button>
          <button
            onClick={onNavigateToBenchmark}
            className="inline-flex items-center space-x-2 px-3.5 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-sm"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Novo Benchmark</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-rose-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <p className="font-medium">Falha na comunicação com o backend</p>
            <p className="text-xs text-rose-400/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Pass Rate Geral */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium tracking-tight uppercase text-slate-400">
              Pass Rate Geral
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-semibold tracking-tight text-slate-100">
              {passRate}%
            </span>
            <span className="text-xs font-mono text-emerald-400 flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" />
              Meta: 70%
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, parseFloat(passRate)))}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Porcentagem média de casos aprovados
          </p>
        </div>

        {/* Fidelidade Média */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium tracking-tight uppercase text-slate-400">
              Fidelidade Média
            </span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-semibold tracking-tight text-slate-100">
              {avgFaithfulness}%
            </span>
            <span className="text-xs font-mono text-slate-400">
              Score Fático
            </span>
          </div>
          <div className="mt-3 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, parseFloat(avgFaithfulness)))}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Ancoragem fática contra documentos de contexto
          </p>
        </div>

        {/* Total de Avaliações */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium tracking-tight uppercase text-slate-400">
              Total de Avaliações
            </span>
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-semibold tracking-tight text-slate-100">
              {totalRuns}
            </span>
            <span className="text-xs font-mono text-slate-400">
              runs
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
            <span>Casos Avaliados:</span>
            <span className="font-mono text-slate-200">{totalCases}</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Baterias de teste executadas
          </p>
        </div>

        {/* Casos Reprovados / Falhas */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium tracking-tight uppercase text-slate-400">
              Casos Reprovados
            </span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <XCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-semibold tracking-tight text-rose-400">
              {totalFailures}
            </span>
            <span className="text-xs font-mono text-slate-400">
              incidentes
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
            <span>Com falha crítica:</span>
            <span className="font-mono text-rose-400">{totalFailures}</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Alucinações ou quebras de schema
          </p>
        </div>
      </div>

      {/* Recent Runs Section */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-medium tracking-tight text-slate-100">
              Baterias de Avaliação Recentes
            </h2>
            <p className="text-xs leading-relaxed text-slate-400 mt-0.5">
              Histórico das últimas execuções de benchmark no sistema.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {recentRuns.length} registro(s)
          </span>
        </div>

        {recentRuns.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            Nenhuma avaliação registrada ainda. Dispare uma nova execução no menu "Executar Benchmark".
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-3">Run ID / Data</th>
                  <th className="py-3 px-3">Modelo</th>
                  <th className="py-3 px-3">Dataset</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Casos</th>
                  <th className="py-3 px-3">Pass Rate</th>
                  <th className="py-3 px-3">Fidelidade</th>
                  <th className="py-3 px-3">Duração</th>
                  <th className="py-3 px-3 text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                {recentRuns.map((run) => {
                  const runPassRate = (run.pass_rate * 100).toFixed(1);
                  const isSuccess = run.status === 'COMPLETED';
                  const isFailed = run.status === 'FAILED';
                  const dateStr = run.created_at ? new Date(run.created_at).toLocaleString('pt-BR') : '-';

                  return (
                    <tr key={run.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-3 text-slate-300">
                        <div className="font-semibold text-slate-200">
                          {run.id.substring(0, 8)}...
                        </div>
                        <div className="text-[10px] text-slate-500 flex items-center mt-0.5">
                          <Clock className="w-3 h-3 mr-1" />
                          {dateStr}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-slate-300">
                        <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200 text-[11px]">
                          {run.model_name}
                        </span>
                        {run.prompt_version_name && (
                          <div className="text-[10px] text-indigo-400 mt-1">
                            {run.prompt_version_name}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-3 text-slate-300 font-sans text-xs">
                        {run.dataset_name || run.dataset_id}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono border ${
                            isSuccess
                              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
                              : isFailed
                              ? 'bg-rose-950/40 border-rose-800 text-rose-400'
                              : 'bg-amber-950/40 border-amber-800 text-amber-400'
                          }`}
                        >
                          {run.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-300">
                        <span className="text-emerald-400">{run.passed_cases}</span>
                        <span className="text-slate-500"> / </span>
                        <span>{run.total_cases}</span>
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex items-center space-x-2">
                          <span className="text-slate-200 w-10 text-right">{runPassRate}%</span>
                          <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden hidden sm:block">
                            <div
                              className={`h-1.5 rounded-full ${
                                run.pass_rate >= 0.7 ? 'bg-emerald-500' : 'bg-rose-500'
                              }`}
                              style={{ width: `${Math.min(100, Math.max(0, run.pass_rate * 100))}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-indigo-300">
                        {(run.avg_faithfulness * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-3 text-slate-400">
                        {Math.round(run.duration_ms)} ms
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => onSelectRunForCompare && onSelectRunForCompare(run.id)}
                          title="Comparar esta execução no A/B"
                          className="inline-flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-slate-100 text-[11px] transition-colors"
                        >
                          <span>A/B</span>
                          <ChevronRight className="w-3 h-3" />
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
