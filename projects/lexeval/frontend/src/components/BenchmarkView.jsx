import React, { useEffect, useState } from 'react';
import { api } from '../api';
import {
  Play,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Layers,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  FileText,
  Sliders,
  Sparkles,
  RefreshCw,
} from 'lucide-react';

export default function BenchmarkView({ initialDatasetId }) {
  const [datasets, setDatasets] = useState([]);
  const [prompts, setPrompts] = useState([]);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Form inputs
  const [selectedDatasetId, setSelectedDatasetId] = useState(initialDatasetId || '');
  const [selectedPromptId, setSelectedPromptId] = useState('');
  const [modelName, setModelName] = useState('rule-evaluator-v1');
  const [evaluatorType, setEvaluatorType] = useState('hybrid');
  const [threshold, setThreshold] = useState(0.70);

  // Run execution
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [runDetail, setRunDetail] = useState(null);
  const [error, setError] = useState(null);
  const [expandedCases, setExpandedCases] = useState({});

  useEffect(() => {
    loadPrerequisites();
  }, []);

  const loadPrerequisites = async () => {
    try {
      setLoadingInitial(true);
      const [dsList, promptList] = await Promise.all([
        api.getDatasets().catch(() => []),
        api.getPrompts().catch(() => []),
      ]);
      setDatasets(dsList);
      setPrompts(promptList);

      if (dsList.length > 0 && !selectedDatasetId) {
        setSelectedDatasetId(dsList[0].id);
      }
    } catch (err) {
      setError('Falha ao carregar datasets e prompts: ' + err.message);
    } finally {
      setLoadingInitial(false);
    }
  };

  const handleStartEvaluation = async (e) => {
    e.preventDefault();
    if (!selectedDatasetId) {
      setError('Selecione um Golden Dataset para iniciar a avaliação.');
      return;
    }

    try {
      setRunning(true);
      setError(null);
      setRunResult(null);
      setRunDetail(null);

      const payload = {
        dataset_id: selectedDatasetId,
        prompt_version_id: selectedPromptId ? selectedPromptId : null,
        model_name: modelName.trim() || 'rule-evaluator-v1',
        evaluator_type: evaluatorType,
        threshold: parseFloat(threshold),
      };

      const result = await api.triggerEvalRun(payload);
      setRunResult(result);

      // Fetch full details with case diagnostics
      if (result && result.id) {
        try {
          const detail = await api.getEvalRunDetail(result.id);
          setRunDetail(detail);
        } catch {
          setRunDetail(result);
        }
      }
    } catch (err) {
      setError(err.message || 'Erro durante a execução do benchmark.');
    } finally {
      setRunning(false);
    }
  };

  const toggleCase = (caseId) => {
    setExpandedCases((prev) => ({
      ...prev,
      [caseId]: !prev[caseId],
    }));
  };

  const activeResults = runDetail?.results || runResult?.results || [];

  return (
    <div className="space-y-8">
      {/* View Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-xl sm:text-2xl font-medium tracking-tight text-slate-100">
          Executar Benchmark & Bateria de Testes
        </h1>
        <p className="text-sm leading-relaxed text-slate-400 mt-1">
          Dispare baterias automatizadas com validação de fidelidade factual, conformidade de schema e juiz determinístico.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-rose-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <p className="font-medium">Erro na Operação</p>
            <p className="text-xs text-rose-400/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Configuration Form Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6">
        <div className="flex items-center space-x-2 mb-6">
          <Sliders className="w-4 h-4 text-indigo-400" />
          <h2 className="text-base font-medium tracking-tight text-slate-100">
            Parâmetros da Bateria
          </h2>
        </div>

        <form onSubmit={handleStartEvaluation} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Dataset Selector */}
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Golden Dataset
              </label>
              {loadingInitial ? (
                <div className="text-xs text-slate-500 font-mono py-2">Carregando datasets...</div>
              ) : datasets.length === 0 ? (
                <div className="text-xs text-rose-400 py-2">Nenhum dataset cadastrado</div>
              ) : (
                <select
                  value={selectedDatasetId}
                  onChange={(e) => setSelectedDatasetId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                >
                  {datasets.map((ds) => (
                    <option key={ds.id} value={ds.id}>
                      {ds.name} ({ds.test_cases_count || 0} casos) [{ds.category || 'GERAL'}]
                    </option>
                  ))}
                </select>
              )}
              <p className="text-[11px] text-slate-500 mt-1.5">
                Conjunto de dados de teste contra o qual o modelo será avaliado.
              </p>
            </div>

            {/* Prompt Version Selector */}
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Versão do Prompt
              </label>
              <select
                value={selectedPromptId}
                onChange={(e) => setSelectedPromptId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value="">Baseline / Modelo Padrão (Sem Prompt Versionado)</option>
                {prompts.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} (v{p.version})
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Prompt estruturado de sistema para o benchmark.
              </p>
            </div>

            {/* Evaluator Engine */}
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Motor Avaliador
              </label>
              <select
                value={evaluatorType}
                onChange={(e) => setEvaluatorType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value="hybrid">Híbrido (Regras + Fático + Juiz)</option>
                <option value="deterministic">Determinístico Puro (Léxico + Citações)</option>
                <option value="llm">LLM-as-a-Judge (Semântico)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Estratégia de cálculo do score de fidelidade.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2 border-t border-slate-800/80">
            {/* Model Identifier */}
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Identificador do Modelo
              </label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="Ex: rule-evaluator-v1, gpt-4o-mini, claude-3-5-sonnet"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
              <p className="text-[11px] text-slate-500 mt-1.5">
                Tag de rastreabilidade gravada no histórico de auditoria.
              </p>
            </div>

            {/* Threshold Slider */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Limiar Mínimo (Threshold)
                </label>
                <span className="font-mono text-xs text-indigo-400 font-medium">
                  {(threshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <p className="text-[11px] text-slate-500 mt-1.5">
                Pontuação mínima de fidelidade para aprovação do caso.
              </p>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={running || loadingInitial || datasets.length === 0}
              className={`inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all shadow-sm ${
                running || loadingInitial || datasets.length === 0
                  ? 'bg-indigo-600/50 cursor-not-allowed text-slate-300'
                  : 'bg-indigo-600 hover:bg-indigo-500'
              }`}
            >
              {running ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Executando Avaliação Caso a Caso...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Iniciar Execução de Avaliação</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {runResult && (
        <div className="space-y-6">
          {/* Summary KPIs of this run */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs font-mono text-slate-500">Run ID: {runResult.id}</span>
                <h3 className="text-lg font-medium tracking-tight text-slate-100 mt-0.5">
                  Resultado do Benchmark
                </h3>
              </div>
              <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-mono bg-emerald-950/40 border border-emerald-800 text-emerald-400">
                {runResult.status}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-[11px] font-mono text-slate-400 uppercase">Taxa de Aprovação</span>
                <div className="text-2xl font-mono font-semibold text-slate-100 mt-1">
                  {(runResult.pass_rate * 100).toFixed(1)}%
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  {runResult.passed_cases} de {runResult.total_cases} casos
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-[11px] font-mono text-slate-400 uppercase">Fidelidade Média</span>
                <div className="text-2xl font-mono font-semibold text-indigo-400 mt-1">
                  {(runResult.avg_faithfulness * 100).toFixed(1)}%
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  Ancoragem de contexto
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-[11px] font-mono text-slate-400 uppercase">Relevância Média</span>
                <div className="text-2xl font-mono font-semibold text-slate-100 mt-1">
                  {(runResult.avg_relevance * 100).toFixed(1)}%
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  Keywords e respostas
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="text-[11px] font-mono text-slate-400 uppercase">Tempo de Execução</span>
                <div className="text-2xl font-mono font-semibold text-slate-100 mt-1">
                  {Math.round(runResult.duration_ms)} ms
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  Latência total da bateria
                </span>
              </div>
            </div>
          </div>

          {/* Individual Test Cases Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-medium tracking-tight text-slate-100">
                  Resultados Detalhados por Caso de Teste
                </h3>
                <p className="text-xs leading-relaxed text-slate-400 mt-0.5">
                  Conformidade de schema, fidelidade fática e precisão de citações jurídicas.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-500">
                {activeResults.length} caso(s) avaliado(s)
              </span>
            </div>

            {activeResults.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-xs">
                Nenhum detalhe retornado pelo motor de execução.
              </div>
            ) : (
              <div className="space-y-3">
                {activeResults.map((item, index) => {
                  const isExpanded = !!expandedCases[item.id || index];
                  const passed = item.passed;
                  const title = item.test_case_title || `Caso #${index + 1}`;
                  const citationsDiag = item.diagnostics?.citations;
                  const citationPrecision = citationsDiag?.precision !== undefined
                    ? (citationsDiag.precision * 100).toFixed(0) + '%'
                    : '100%';

                  return (
                    <div
                      key={item.id || index}
                      className="rounded-lg border border-slate-800 bg-slate-950/40 overflow-hidden transition-colors"
                    >
                      {/* Accordion Header */}
                      <button
                        onClick={() => toggleCase(item.id || index)}
                        className="w-full flex items-center justify-between p-3.5 text-left hover:bg-slate-800/30 transition-colors"
                      >
                        <div className="flex items-center space-x-3 flex-1 min-w-0 pr-4">
                          {passed ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                          ) : (
                            <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                          )}
                          <div className="min-w-0">
                            <span className="text-sm font-medium text-slate-200 block truncate">
                              {title}
                            </span>
                            {!passed && item.failure_reason && (
                              <span className="text-[10px] font-mono text-rose-400">
                                Motivo: {item.failure_reason}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Scores summary in row */}
                        <div className="flex items-center space-x-4 font-mono text-xs flex-shrink-0">
                          <div className="hidden sm:block text-right">
                            <span className="text-[10px] text-slate-500 uppercase block">Schema</span>
                            <span className="text-slate-300">
                              {(item.schema_score ?? 1.0).toFixed(1)}
                            </span>
                          </div>
                          <div className="hidden sm:block text-right">
                            <span className="text-[10px] text-slate-500 uppercase block">Citações</span>
                            <span className="text-slate-300">{citationPrecision}</span>
                          </div>
                          <div className="text-right">
                            <span className="text-[10px] text-slate-500 uppercase block">Fidelidade</span>
                            <span className={item.faithfulness_score >= 0.7 ? 'text-emerald-400' : 'text-rose-400'}>
                              {(item.faithfulness_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="text-slate-500">
                            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                          </div>
                        </div>
                      </button>

                      {/* Accordion Content */}
                      {isExpanded && (
                        <div className="border-t border-slate-800/80 p-4 space-y-4 bg-slate-900/20 text-xs">
                          {/* Metrics Bar */}
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800">
                              <span className="text-[10px] text-slate-500 font-mono uppercase block">Conformidade Schema</span>
                              <span className="text-slate-200 font-mono font-medium">
                                {(item.schema_score ?? 1.0).toFixed(2)} / 1.00
                              </span>
                            </div>
                            <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800">
                              <span className="text-[10px] text-slate-500 font-mono uppercase block">Score de Fidelidade</span>
                              <span className="text-indigo-400 font-mono font-medium">
                                {(item.faithfulness_score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800">
                              <span className="text-[10px] text-slate-500 font-mono uppercase block">Precisão de Citação</span>
                              <span className="text-slate-200 font-mono font-medium">
                                {citationPrecision}
                              </span>
                            </div>
                            <div className="p-2.5 rounded bg-slate-950/70 border border-slate-800">
                              <span className="text-[10px] text-slate-500 font-mono uppercase block">Status</span>
                              <span className={`font-mono font-medium ${passed ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {passed ? 'Aprovado' : `Reprovado (${item.failure_reason || 'Falha'})`}
                              </span>
                            </div>
                          </div>

                          {/* Output Produced */}
                          <div>
                            <span className="text-[11px] font-medium text-slate-300 uppercase tracking-wider block mb-1.5">
                              Resposta Produzida pelo Modelo
                            </span>
                            <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto leading-relaxed">
                              {item.generated_output}
                            </pre>
                          </div>

                          {/* Diagnostics details if present */}
                          {item.diagnostics && Object.keys(item.diagnostics).length > 0 && (
                            <div>
                              <span className="text-[11px] font-medium text-slate-300 uppercase tracking-wider block mb-1.5">
                                Diagnóstico Técnico do Avaliador
                              </span>
                              <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 font-mono text-[11px] text-slate-400 whitespace-pre-wrap overflow-x-auto">
                                {JSON.stringify(item.diagnostics, null, 2)}
                              </pre>
                            </div>
                          )}
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
