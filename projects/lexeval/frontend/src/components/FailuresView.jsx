import React, { useEffect, useState } from 'react';
import { api } from '../api';
import {
  AlertTriangle,
  Filter,
  RefreshCw,
  AlertCircle,
  FileText,
  ChevronDown,
  ChevronRight,
  Database,
  Search,
} from 'lucide-react';

export default function FailuresView() {
  const [failures, setFailures] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [selectedReason, setSelectedReason] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedItems, setExpandedItems] = useState({});

  const failureReasons = [
    { value: '', label: 'Todas as Falhas' },
    { value: 'HALLUCINATION', label: 'Alucinação Geral (HALLUCINATION)' },
    { value: 'HALLUCINATED_CITATION', label: 'Citação Jurídica Inexistente (HALLUCINATED_CITATION)' },
    { value: 'HALLUCINATED_NUMERICAL_VALUE', label: 'Valor Numérico Falso (HALLUCINATED_NUMERICAL_VALUE)' },
    { value: 'SCHEMA_ERROR', label: 'Erro de Conformidade Schema (SCHEMA_ERROR)' },
    { value: 'UNGROUNDED_CLAIM', label: 'Afirmação Não Ancorada (UNGROUNDED_CLAIM)' },
    { value: 'MISSING_CITATION', label: 'Citação Ausente (MISSING_CITATION)' },
    { value: 'FORBIDDEN_TERM_VIOLATION', label: 'Violação de Termo Vedado (FORBIDDEN_TERM_VIOLATION)' },
    { value: 'LOW_FAITHFULNESS', label: 'Baixa Fidelidade (LOW_FAITHFULNESS)' },
    { value: 'INSUFFICIENT_RELEVANCE', label: 'Relevância Insuficiente (INSUFFICIENT_RELEVANCE)' },
  ];

  useEffect(() => {
    loadDatasets();
    fetchFailures();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await api.getDatasets();
      setDatasets(data || []);
    } catch {
      // ignore
    }
  };

  const fetchFailures = async (datasetId = selectedDatasetId, reason = selectedReason) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getFailures({
        datasetId: datasetId || undefined,
        reason: reason || undefined,
        limit: 100,
      });
      setFailures(data || []);
    } catch (err) {
      setError(err.message || 'Falha ao carregar catálogo de falhas.');
    } finally {
      setLoading(false);
    }
  };

  const handleDatasetChange = (dsId) => {
    setSelectedDatasetId(dsId);
    fetchFailures(dsId, selectedReason);
  };

  const handleReasonChange = (reason) => {
    setSelectedReason(reason);
    fetchFailures(selectedDatasetId, reason);
  };

  const toggleItem = (id) => {
    setExpandedItems((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Filter failures client-side by text search if user typed anything
  const filteredFailures = failures.filter((item) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      (item.test_case_title && item.test_case_title.toLowerCase().includes(term)) ||
      (item.failure_reason && item.failure_reason.toLowerCase().includes(term)) ||
      (item.generated_output && item.generated_output.toLowerCase().includes(term)) ||
      (item.dataset_name && item.dataset_name.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-8">
      {/* View Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-xl sm:text-2xl font-medium tracking-tight text-slate-100">
          Catálogo de Falhas e Incidentes de IA
        </h1>
        <p className="text-sm leading-relaxed text-slate-400 mt-1">
          Auditoria de alucinações fáticas, citações jurídicas espúrias, violações de formato e desvios de guardrails.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-rose-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <p className="font-medium">Falha na Busca</p>
            <p className="text-xs text-rose-400/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Filter Toolbar Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Dataset Filter */}
          <div>
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              Filtrar por Dataset
            </label>
            <select
              value={selectedDatasetId}
              onChange={(e) => handleDatasetChange(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            >
              <option value="">Todos os Datasets</option>
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          {/* Reason Filter */}
          <div>
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              Categoria do Erro
            </label>
            <select
              value={selectedReason}
              onChange={(e) => handleReasonChange(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            >
              {failureReasons.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div>
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              Busca Textual
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Pesquisar por caso, termo ou trecho..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
          <span className="font-mono text-slate-400">
            {filteredFailures.length} incidente(s) catalogado(s)
          </span>
          <button
            onClick={() => fetchFailures()}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Recarregar</span>
          </button>
        </div>
      </div>

      {/* Failures List */}
      {loading ? (
        <div className="py-16 text-center text-slate-500 font-mono text-sm flex items-center justify-center space-x-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span>Carregando catálogo de falhas...</span>
        </div>
      ) : filteredFailures.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-12 text-center">
          <AlertTriangle className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-medium text-slate-300">
            Nenhuma falha encontrada
          </h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Não foram encontrados incidentes com os filtros selecionados ou as avaliações obtiveram 100% de conformidade.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFailures.map((item) => {
            const isExpanded = !!expandedItems[item.id];
            const reason = item.failure_reason || 'ERRO_DESCONHECIDO';
            const dateStr = item.created_at ? new Date(item.created_at).toLocaleString('pt-BR') : '-';

            return (
              <div
                key={item.id}
                className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden"
              >
                {/* Header item */}
                <div className="p-4 sm:p-5 border-b border-slate-800/80">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="flex items-center space-x-2.5">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-rose-950/60 border border-rose-800/60 text-rose-300">
                        {reason}
                      </span>
                      <h3 className="text-base font-medium tracking-tight text-slate-100">
                        {item.test_case_title || 'Caso de Teste'}
                      </h3>
                    </div>
                    <div className="flex items-center space-x-3 text-xs font-mono text-slate-500">
                      <span>{dateStr}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mt-2 font-mono">
                    <span>Dataset: <span className="text-slate-200">{item.dataset_name || '-'}</span></span>
                    <span>•</span>
                    <span>Modelo: <span className="text-slate-200">{item.model_name || '-'}</span></span>
                    <span>•</span>
                    <span>Fidelidade: <span className="text-rose-400">{(item.faithfulness_score * 100).toFixed(1)}%</span></span>
                    <span>•</span>
                    <span>Schema: <span className="text-slate-200">{(item.schema_score ?? 1.0).toFixed(1)}</span></span>
                  </div>
                </div>

                {/* Diff Viewer Body */}
                <div className="p-4 sm:p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Generated Output */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono font-medium text-rose-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                        <span>Resposta Gerada (Com Defeito)</span>
                      </span>
                    </div>
                    <pre className="p-3.5 rounded-lg bg-slate-950 border border-rose-950/60 font-mono text-xs text-rose-200/90 whitespace-pre-wrap overflow-x-auto min-h-[140px] leading-relaxed">
                      {item.generated_output}
                    </pre>
                  </div>

                  {/* Reference Ground Truth */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono font-medium text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        <span>Gabarito Esperado (Ground Truth)</span>
                      </span>
                    </div>
                    <pre className="p-3.5 rounded-lg bg-slate-950 border border-emerald-950/60 font-mono text-xs text-emerald-200/90 whitespace-pre-wrap overflow-x-auto min-h-[140px] leading-relaxed">
                      {item.expected_output}
                    </pre>
                  </div>
                </div>

                {/* Expander for Context & Diagnostics */}
                <div className="border-t border-slate-800 bg-slate-950/50">
                  <button
                    onClick={() => toggleItem(item.id)}
                    className="w-full px-5 py-2.5 flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 transition-colors"
                  >
                    <span className="flex items-center space-x-2">
                      <FileText className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Ver Documento de Contexto Jurídico & Diagnóstico Técnico</span>
                    </span>
                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </button>

                  {isExpanded && (
                    <div className="p-5 border-t border-slate-800/80 space-y-4">
                      {/* Context Document */}
                      <div>
                        <span className="text-[11px] font-mono text-slate-400 uppercase block mb-1">
                          Documento de Contexto Fornecido à IA
                        </span>
                        <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-60">
                          {item.context_snippet}
                        </pre>
                      </div>

                      {/* Technical Diagnostics */}
                      {item.diagnostics && (
                        <div>
                          <span className="text-[11px] font-mono text-slate-400 uppercase block mb-1">
                            Diagnóstico Completo do Avaliador (JSON)
                          </span>
                          <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-400 whitespace-pre-wrap overflow-x-auto">
                            {JSON.stringify(item.diagnostics, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
