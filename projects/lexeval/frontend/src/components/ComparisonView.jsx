import React, { useEffect, useState } from 'react';
import { api } from '../api';
import {
  GitCompare,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Scale,
} from 'lucide-react';

export default function ComparisonView({ preselectedRunAId }) {
  const [runs, setRuns] = useState([]);
  const [loadingRuns, setLoadingRuns] = useState(true);

  const [runAId, setRunAId] = useState(preselectedRunAId || '');
  const [runBId, setRunBId] = useState('');
  const [comparing, setComparing] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [error, setError] = useState(null);

  // Filter state
  const [statusFilter, setStatusFilter] = useState('ALL'); // ALL, REGRESSION, GAIN, TIE
  const [expandedCases, setExpandedCases] = useState({});

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      setLoadingRuns(true);
      setError(null);
      const data = await api.getEvalRuns(50);
      setRuns(data);

      if (data && data.length >= 2) {
        if (!runAId) setRunAId(data[1].id);
        if (!runBId) setRunBId(data[0].id);
      } else if (data && data.length === 1 && !runAId) {
        setRunAId(data[0].id);
      }
    } catch (err) {
      setError('Falha ao carregar lista de execuções: ' + err.message);
    } finally {
      setLoadingRuns(false);
    }
  };

  const handleRunComparison = async (e) => {
    if (e) e.preventDefault();
    if (!runAId || !runBId) {
      setError('Selecione ambas as execuções (Baseline A e Candidato B) para comparar.');
      return;
    }
    if (runAId === runBId) {
      setError('Selecione execuções diferentes para a comparação A/B.');
      return;
    }

    try {
      setComparing(true);
      setError(null);
      const result = await api.compareRuns(runAId, runBId);
      setComparisonData(result);
    } catch (err) {
      setError(err.message || 'Falha ao executar análise comparativa A/B.');
    } finally {
      setComparing(false);
    }
  };

  const toggleCase = (id) => {
    setExpandedCases((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const comparisons = comparisonData?.comparisons || [];
  const filteredComparisons = comparisons.filter((c) => {
    if (statusFilter === 'ALL') return true;
    return c.status === statusFilter;
  });

  const verdict = comparisonData?.verdict;
  const deltaPassRate = comparisonData?.pass_rate_delta !== undefined
    ? (comparisonData.pass_rate_delta * 100).toFixed(1)
    : '0.0';
  const deltaFaithfulness = comparisonData?.faithfulness_delta !== undefined
    ? (comparisonData.faithfulness_delta * 100).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-xl sm:text-2xl font-medium tracking-tight text-slate-100">
          Comparador e Versionador de Prompts (A/B Testing)
        </h1>
        <p className="text-sm leading-relaxed text-slate-400 mt-1">
          Detecte regressões silenciosas, ganhos de precisão fática e variações comportamentais entre prompts e modelos.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-rose-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <p className="font-medium">Erro na Comparação</p>
            <p className="text-xs text-rose-400/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Selectors Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Baseline A */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-slate-300 uppercase tracking-wider">
                Baseline — Execução A
              </label>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                Padrão / Controle
              </span>
            </div>
            {loadingRuns ? (
              <div className="text-xs text-slate-500 font-mono py-2">Carregando execuções...</div>
            ) : runs.length === 0 ? (
              <div className="text-xs text-rose-400 py-2">Nenhuma execução disponível</div>
            ) : (
              <select
                value={runAId}
                onChange={(e) => setRunAId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value="">Selecione o baseline...</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>
                    Run {r.id.substring(0, 8)} — {r.model_name} (Pass: {(r.pass_rate * 100).toFixed(1)}%) [{r.dataset_name || 'Dataset'}]
                  </option>
                ))}
              </select>
            )}
            <p className="text-[11px] text-slate-500 mt-1.5">
              Versão prévia ou estável de referência para conferência.
            </p>
          </div>

          {/* Candidate B */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-slate-300 uppercase tracking-wider">
                Candidato — Execução B
              </label>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/40">
                Novo Prompt / Modelo
              </span>
            </div>
            {loadingRuns ? (
              <div className="text-xs text-slate-500 font-mono py-2">Carregando execuções...</div>
            ) : runs.length === 0 ? (
              <div className="text-xs text-rose-400 py-2">Nenhuma execução disponível</div>
            ) : (
              <select
                value={runBId}
                onChange={(e) => setRunBId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value="">Selecione o candidato...</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>
                    Run {r.id.substring(0, 8)} — {r.model_name} (Pass: {(r.pass_rate * 100).toFixed(1)}%) [{r.dataset_name || 'Dataset'}]
                  </option>
                ))}
              </select>
            )}
            <p className="text-[11px] text-slate-500 mt-1.5">
              Versão candidata sob teste para validação de regressão.
            </p>
          </div>
        </div>

        <div className="flex justify-end pt-5 mt-5 border-t border-slate-800">
          <button
            onClick={handleRunComparison}
            disabled={comparing || loadingRuns || runs.length < 2}
            className={`inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all shadow-sm ${
              comparing || loadingRuns || runs.length < 2
                ? 'bg-indigo-600/50 cursor-not-allowed text-slate-300'
                : 'bg-indigo-600 hover:bg-indigo-500'
            }`}
          >
            {comparing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analisando Regressões Fáticas...</span>
              </>
            ) : (
              <>
                <GitCompare className="w-4 h-4" />
                <span>Executar Análise Comparativa A/B</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      {comparisonData && (
        <div className="space-y-6">
          {/* Verdict Banner */}
          <div
            className={`rounded-xl border p-5 backdrop-blur-sm ${
              verdict === 'POSITIVE_PROGRESSION'
                ? 'border-emerald-800/80 bg-emerald-950/20'
                : verdict === 'CRITICAL_REGRESSION'
                ? 'border-rose-800/80 bg-rose-950/20'
                : verdict === 'MODERATE_IMPROVEMENT'
                ? 'border-amber-800/80 bg-amber-950/20'
                : 'border-slate-800 bg-slate-900/50'
            }`}
          >
            <div className="flex items-start space-x-3">
              <div
                className={`p-2 rounded-lg mt-0.5 ${
                  verdict === 'POSITIVE_PROGRESSION'
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : verdict === 'CRITICAL_REGRESSION'
                    ? 'bg-rose-500/10 text-rose-400'
                    : verdict === 'MODERATE_IMPROVEMENT'
                    ? 'bg-amber-500/10 text-amber-400'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                <Scale className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono uppercase tracking-wider font-semibold text-slate-300">
                    Veredito da Análise A/B
                  </span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                      verdict === 'POSITIVE_PROGRESSION'
                        ? 'border-emerald-700 bg-emerald-900/40 text-emerald-300'
                        : verdict === 'CRITICAL_REGRESSION'
                        ? 'border-rose-700 bg-rose-900/40 text-rose-300'
                        : verdict === 'MODERATE_IMPROVEMENT'
                        ? 'border-amber-700 bg-amber-900/40 text-amber-300'
                        : 'border-slate-700 bg-slate-800 text-slate-300'
                    }`}
                  >
                    {verdict || 'EQUIVALENT'}
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-100 mt-1">
                  {verdict === 'POSITIVE_PROGRESSION' &&
                    'Progressão Positiva: O candidato B superou o baseline A sem regressões críticas detectadas.'}
                  {verdict === 'CRITICAL_REGRESSION' &&
                    'Regressão Crítica Detectada: O candidato B introduziu falhas ou teve desempenho inferior ao baseline.'}
                  {verdict === 'MODERATE_IMPROVEMENT' &&
                    'Melhoria Moderada: Ganhos superaram perdas, mas requer atenção a casos específicos.'}
                  {verdict === 'EQUIVALENT' &&
                    'Equivalente: Desempenho idêntico ou sem variações estatisticamente relevantes.'}
                </p>
              </div>
            </div>
          </div>

          {/* 4 Comparison Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {/* Delta Pass Rate */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
              <span className="text-[11px] font-mono uppercase text-slate-400 block">
                Delta Pass Rate
              </span>
              <div className="flex items-baseline space-x-2 mt-2">
                <span
                  className={`text-2xl font-mono font-semibold ${
                    parseFloat(deltaPassRate) > 0
                      ? 'text-emerald-400'
                      : parseFloat(deltaPassRate) < 0
                      ? 'text-rose-400'
                      : 'text-slate-300'
                  }`}
                >
                  {parseFloat(deltaPassRate) > 0 ? `+${deltaPassRate}%` : `${deltaPassRate}%`}
                </span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                {(comparisonData.run_a_pass_rate * 100).toFixed(0)}% → {(comparisonData.run_b_pass_rate * 100).toFixed(0)}%
              </span>
            </div>

            {/* Ganhos */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
              <span className="text-[11px] font-mono uppercase text-slate-400 block">
                Ganhos (+)
              </span>
              <div className="flex items-baseline space-x-2 mt-2">
                <span className="text-2xl font-mono font-semibold text-emerald-400">
                  +{comparisonData.gains_count}
                </span>
                <span className="text-[10px] font-mono text-emerald-400/80">
                  casos recuperados
                </span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                A reprovou → B aprovou
              </span>
            </div>

            {/* Regressões */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
              <span className="text-[11px] font-mono uppercase text-slate-400 block">
                Regressões (-)
              </span>
              <div className="flex items-baseline space-x-2 mt-2">
                <span className="text-2xl font-mono font-semibold text-rose-400">
                  -{comparisonData.regressions_count}
                </span>
                <span className="text-[10px] font-mono text-rose-400/80">
                  casos perdidos
                </span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                A aprovava → B reprovou
              </span>
            </div>

            {/* Empates */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
              <span className="text-[11px] font-mono uppercase text-slate-400 block">
                Empates (=)
              </span>
              <div className="flex items-baseline space-x-2 mt-2">
                <span className="text-2xl font-mono font-semibold text-slate-300">
                  {comparisonData.ties_count}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  invariantes
                </span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                Mesmo resultado em A e B
              </span>
            </div>
          </div>

          {/* Side-by-Side Regression Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-medium tracking-tight text-slate-100">
                  Análise Comparativa Caso a Caso
                </h3>
                <p className="text-xs leading-relaxed text-slate-400 mt-0.5">
                  Inspeção detalhada de variações de acurácia fática e notas diagnósticas.
                </p>
              </div>

              {/* Filters */}
              <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
                <button
                  onClick={() => setStatusFilter('ALL')}
                  className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                    statusFilter === 'ALL'
                      ? 'bg-slate-800 text-slate-100'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Todos ({comparisons.length})
                </button>
                <button
                  onClick={() => setStatusFilter('REGRESSION')}
                  className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                    statusFilter === 'REGRESSION'
                      ? 'bg-rose-950/60 text-rose-300 border border-rose-800/50'
                      : 'text-slate-400 hover:text-rose-400'
                  }`}
                >
                  Regressões ({comparisonData.regressions_count})
                </button>
                <button
                  onClick={() => setStatusFilter('GAIN')}
                  className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                    statusFilter === 'GAIN'
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50'
                      : 'text-slate-400 hover:text-emerald-400'
                  }`}
                >
                  Ganhos ({comparisonData.gains_count})
                </button>
                <button
                  onClick={() => setStatusFilter('TIE')}
                  className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                    statusFilter === 'TIE'
                      ? 'bg-slate-800 text-slate-100'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Empates ({comparisonData.ties_count})
                </button>
              </div>
            </div>

            {filteredComparisons.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-xs font-mono">
                Nenhum caso encontrado para o filtro "{statusFilter}".
              </div>
            ) : (
              <div className="space-y-3">
                {filteredComparisons.map((c) => {
                  const isExpanded = !!expandedCases[c.test_case_id];
                  const deltaFt = (c.delta_faithfulness * 100).toFixed(1);
                  const isGain = c.status === 'GAIN';
                  const isRegression = c.status === 'REGRESSION';

                  return (
                    <div
                      key={c.test_case_id}
                      className="rounded-lg border border-slate-800 bg-slate-950/40 overflow-hidden transition-colors"
                    >
                      <button
                        onClick={() => toggleCase(c.test_case_id)}
                        className="w-full flex items-center justify-between p-3.5 text-left hover:bg-slate-800/30 transition-colors"
                      >
                        <div className="flex items-center space-x-3 flex-1 min-w-0 pr-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium border flex-shrink-0 ${
                              isGain
                                ? 'bg-emerald-950/50 border-emerald-800 text-emerald-400'
                                : isRegression
                                ? 'bg-rose-950/50 border-rose-800 text-rose-400'
                                : 'bg-slate-800 border-slate-700 text-slate-300'
                            }`}
                          >
                            {c.status}
                          </span>
                          <span className="text-sm font-medium text-slate-200 truncate">
                            {c.title}
                          </span>
                        </div>

                        <div className="flex items-center space-x-6 font-mono text-xs flex-shrink-0">
                          <div className="text-right hidden sm:block">
                            <span className="text-[10px] text-slate-500 uppercase block">Baseline A</span>
                            <span className={c.run_a_passed ? 'text-emerald-400' : 'text-rose-400'}>
                              {(c.run_a_faithfulness * 100).toFixed(1)}% {c.run_a_passed ? '(Pass)' : '(Fail)'}
                            </span>
                          </div>

                          <div className="text-right hidden sm:block">
                            <span className="text-[10px] text-slate-500 uppercase block">Candidato B</span>
                            <span className={c.run_b_passed ? 'text-emerald-400' : 'text-rose-400'}>
                              {(c.run_b_faithfulness * 100).toFixed(1)}% {c.run_b_passed ? '(Pass)' : '(Fail)'}
                            </span>
                          </div>

                          <div className="text-right">
                            <span className="text-[10px] text-slate-500 uppercase block">Delta</span>
                            <span
                              className={`font-semibold ${
                                parseFloat(deltaFt) > 0
                                  ? 'text-emerald-400'
                                  : parseFloat(deltaFt) < 0
                                  ? 'text-rose-400'
                                  : 'text-slate-400'
                              }`}
                            >
                              {parseFloat(deltaFt) > 0 ? `+${deltaFt}%` : `${deltaFt}%`}
                            </span>
                          </div>

                          <div className="text-slate-500">
                            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                          </div>
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="border-t border-slate-800/80 p-4 space-y-3 bg-slate-900/20 text-xs">
                          <div>
                            <span className="text-[11px] font-medium text-slate-300 uppercase tracking-wider block mb-1">
                              Diagnóstico do Comparador
                            </span>
                            <p className="text-slate-300 bg-slate-950 p-2.5 rounded border border-slate-800 font-sans leading-relaxed">
                              {c.notes || 'Sem notas adicionais para esta variação.'}
                            </p>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                            <div className="p-3 rounded bg-slate-950/80 border border-slate-800 space-y-1">
                              <span className="text-[10px] text-slate-400 font-mono uppercase block">
                                Execução A (Baseline)
                              </span>
                              <div className="flex items-center space-x-2">
                                <span className="font-mono text-slate-200">
                                  Fidelidade: {(c.run_a_faithfulness * 100).toFixed(1)}%
                                </span>
                                <span
                                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                                    c.run_a_passed
                                      ? 'bg-emerald-950 text-emerald-400'
                                      : 'bg-rose-950 text-rose-400'
                                  }`}
                                >
                                  {c.run_a_passed ? 'Aprovado' : 'Reprovado'}
                                </span>
                              </div>
                            </div>

                            <div className="p-3 rounded bg-slate-950/80 border border-slate-800 space-y-1">
                              <span className="text-[10px] text-indigo-400 font-mono uppercase block">
                                Execução B (Candidato)
                              </span>
                              <div className="flex items-center space-x-2">
                                <span className="font-mono text-slate-200">
                                  Fidelidade: {(c.run_b_faithfulness * 100).toFixed(1)}%
                                </span>
                                <span
                                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                                    c.run_b_passed
                                      ? 'bg-emerald-950 text-emerald-400'
                                      : 'bg-rose-950 text-rose-400'
                                  }`}
                                >
                                  {c.run_b_passed ? 'Aprovado' : 'Reprovado'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
