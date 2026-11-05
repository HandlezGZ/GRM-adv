import React, { useEffect, useState } from 'react';
import { api } from '../api';
import {
  Database,
  Plus,
  Layers,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  FolderPlus,
  ShieldAlert,
  FileCheck,
} from 'lucide-react';

export default function DatasetsView() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [testCases, setTestCases] = useState([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [loadingCases, setLoadingCases] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Tabs: 'cases' or 'add_case' or 'add_dataset'
  const [activeSubTab, setActiveSubTab] = useState('cases');

  // Case expanders
  const [expandedCases, setExpandedCases] = useState({});

  // Form states: New Case
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseQuery, setNewCaseQuery] = useState('');
  const [newCaseContext, setNewCaseContext] = useState('');
  const [newCaseExpected, setNewCaseExpected] = useState('');
  const [newCaseKeywords, setNewCaseKeywords] = useState('');
  const [newCaseForbidden, setNewCaseForbidden] = useState('');
  const [submittingCase, setSubmittingCase] = useState(false);

  // Form states: New Dataset
  const [newDsName, setNewDsName] = useState('');
  const [newDsDesc, setNewDsDesc] = useState('');
  const [newDsCategory, setNewDsCategory] = useState('TRIBUTARIO');
  const [submittingDs, setSubmittingDs] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      loadCases(selectedDatasetId);
    } else {
      setTestCases([]);
    }
  }, [selectedDatasetId]);

  const loadDatasets = async (selectId = null) => {
    try {
      setLoadingDatasets(true);
      setError(null);
      const data = await api.getDatasets();
      setDatasets(data || []);

      if (data && data.length > 0) {
        const targetId = selectId || selectedDatasetId || data[0].id;
        setSelectedDatasetId(targetId);
      }
    } catch (err) {
      setError('Falha ao carregar datasets: ' + err.message);
    } finally {
      setLoadingDatasets(false);
    }
  };

  const loadCases = async (dsId) => {
    try {
      setLoadingCases(true);
      setError(null);
      const data = await api.getDatasetCases(dsId);
      setTestCases(data || []);
    } catch (err) {
      setError('Falha ao carregar casos de teste: ' + err.message);
    } finally {
      setLoadingCases(false);
    }
  };

  const handleToggleCase = (caseId) => {
    setExpandedCases((prev) => ({
      ...prev,
      [caseId]: !prev[caseId],
    }));
  };

  const handleCreateCase = async (e) => {
    e.preventDefault();
    if (!selectedDatasetId) {
      setError('Selecione um dataset primeiro.');
      return;
    }
    if (!newCaseTitle.trim() || !newCaseQuery.trim() || !newCaseContext.trim() || !newCaseExpected.trim()) {
      setError('Preencha todos os campos obrigatórios (Título, Consulta, Contexto e Resposta Esperada).');
      return;
    }

    try {
      setSubmittingCase(true);
      setError(null);
      setSuccessMsg(null);

      const requiredKeywords = newCaseKeywords
        .split(',')
        .map((k) => k.trim())
        .filter(Boolean);

      const forbiddenTerms = newCaseForbidden
        .split(',')
        .map((f) => f.trim())
        .filter(Boolean);

      const payload = {
        title: newCaseTitle.trim(),
        input_query: newCaseQuery.trim(),
        context_document: newCaseContext.trim(),
        expected_output: newCaseExpected.trim(),
        required_keywords: requiredKeywords,
        forbidden_terms: forbiddenTerms,
      };

      await api.createTestCase(selectedDatasetId, payload);
      setSuccessMsg('Caso de teste cadastrado com sucesso!');

      // Reset form
      setNewCaseTitle('');
      setNewCaseQuery('');
      setNewCaseContext('');
      setNewCaseExpected('');
      setNewCaseKeywords('');
      setNewCaseForbidden('');

      // Refresh cases and datasets count
      await loadCases(selectedDatasetId);
      await loadDatasets(selectedDatasetId);
      setActiveSubTab('cases');
    } catch (err) {
      setError('Erro ao cadastrar caso de teste: ' + err.message);
    } finally {
      setSubmittingCase(false);
    }
  };

  const handleCreateDataset = async (e) => {
    e.preventDefault();
    if (!newDsName.trim()) {
      setError('Informe o nome do dataset.');
      return;
    }

    try {
      setSubmittingDs(true);
      setError(null);
      setSuccessMsg(null);

      const payload = {
        name: newDsName.trim(),
        description: newDsDesc.trim() || null,
        category: newDsCategory.trim() || 'TRIBUTARIO',
      };

      const created = await api.createDataset(payload);
      setSuccessMsg(`Dataset "${created.name}" criado com sucesso!`);
      setNewDsName('');
      setNewDsDesc('');

      await loadDatasets(created.id);
      setActiveSubTab('cases');
    } catch (err) {
      setError('Erro ao criar dataset: ' + err.message);
    } finally {
      setSubmittingDs(false);
    }
  };

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId);

  return (
    <div className="space-y-8">
      {/* View Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-xl sm:text-2xl font-medium tracking-tight text-slate-100">
          Gerenciador de Golden Datasets & Casos de Teste
        </h1>
        <p className="text-sm leading-relaxed text-slate-400 mt-1">
          Curadoria de gabaritos jurídicos, documentos fáticos de referência e guardrails de conformidade.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-rose-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <p className="font-medium">Atenção</p>
            <p className="text-xs text-rose-400/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {successMsg && (
        <div className="rounded-xl border border-emerald-900/50 bg-emerald-950/20 p-4 text-emerald-300 text-sm flex items-start space-x-3">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5 text-emerald-400" />
          <div className="flex-1">
            <p className="font-medium">{successMsg}</p>
          </div>
        </div>
      )}

      {/* Dataset Selection Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              Selecione o Golden Dataset Ativo
            </label>
            {loadingDatasets ? (
              <div className="text-xs text-slate-500 font-mono py-2">Carregando datasets...</div>
            ) : datasets.length === 0 ? (
              <div className="text-xs text-slate-400 py-2">Nenhum dataset cadastrado. Crie um novo abaixo.</div>
            ) : (
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors font-medium"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} [{d.category || 'GERAL'}] — {d.test_cases_count || 0} caso(s)
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="flex items-center space-x-2 pt-2 sm:pt-4">
            <button
              onClick={() => setActiveSubTab('cases')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border ${
                activeSubTab === 'cases'
                  ? 'bg-slate-800 text-slate-100 border-slate-700'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
            >
              Casos Cadastrados ({testCases.length})
            </button>
            <button
              onClick={() => setActiveSubTab('add_case')}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border ${
                activeSubTab === 'add_case'
                  ? 'bg-indigo-600 text-white border-indigo-500'
                  : 'bg-slate-950 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Novo Caso</span>
            </button>
            <button
              onClick={() => setActiveSubTab('add_dataset')}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border ${
                activeSubTab === 'add_dataset'
                  ? 'bg-indigo-600 text-white border-indigo-500'
                  : 'bg-slate-950 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              <FolderPlus className="w-3.5 h-3.5" />
              <span>Novo Dataset</span>
            </button>
          </div>
        </div>

        {selectedDataset && (
          <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
            <span>Categoria: <span className="font-mono text-slate-200">{selectedDataset.category}</span></span>
            {selectedDataset.description && (
              <>
                <span>•</span>
                <span>Descrição: <span className="text-slate-300">{selectedDataset.description}</span></span>
              </>
            )}
            <span>•</span>
            <span>ID: <span className="font-mono text-slate-500">{selectedDataset.id}</span></span>
          </div>
        )}
      </div>

      {/* Tab: Test Cases List */}
      {activeSubTab === 'cases' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-medium tracking-tight text-slate-100">
              Casos de Teste do Dataset
            </h2>
            <button
              onClick={() => loadCases(selectedDatasetId)}
              disabled={loadingCases}
              className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingCases ? 'animate-spin' : ''}`} />
              <span>Atualizar</span>
            </button>
          </div>

          {loadingCases ? (
            <div className="py-12 text-center text-slate-500 font-mono text-xs flex items-center justify-center space-x-2">
              <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Carregando casos do dataset...</span>
            </div>
          ) : testCases.length === 0 ? (
            <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-12 text-center">
              <Database className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <h3 className="text-base font-medium text-slate-300">
                Nenhum caso de teste cadastrado neste dataset
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto mb-4">
                Adicione perguntas, documentos de contexto e gabaritos esperados para este benchmark.
              </p>
              <button
                onClick={() => setActiveSubTab('add_case')}
                className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Cadastrar Primeiro Caso</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {testCases.map((tc, idx) => {
                const isExpanded = !!expandedCases[tc.id || idx];
                const kws = tc.required_keywords || [];
                const fts = tc.forbidden_terms || [];

                return (
                  <div
                    key={tc.id || idx}
                    className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden"
                  >
                    {/* Header */}
                    <button
                      onClick={() => handleToggleCase(tc.id || idx)}
                      className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/30 transition-colors"
                    >
                      <div className="flex items-center space-x-3 flex-1 min-w-0 pr-4">
                        <span className="font-mono text-xs text-indigo-400 bg-indigo-950/60 border border-indigo-800/40 px-2 py-0.5 rounded">
                          #{idx + 1}
                        </span>
                        <span className="text-sm font-medium text-slate-200 truncate">
                          {tc.title}
                        </span>
                      </div>

                      <div className="flex items-center space-x-4 text-xs font-mono text-slate-500 flex-shrink-0">
                        <span className="hidden sm:inline">
                          {kws.length} kws / {fts.length} guardrails
                        </span>
                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                      </div>
                    </button>

                    {/* Expandable Body */}
                    {isExpanded && (
                      <div className="border-t border-slate-800 p-5 space-y-4 bg-slate-950/40 text-xs">
                        {/* Query */}
                        <div>
                          <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block mb-1">
                            Pergunta / Consulta Jurídica do Usuário
                          </span>
                          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 leading-relaxed font-sans">
                            {tc.input_query}
                          </div>
                        </div>

                        {/* Context Document */}
                        <div>
                          <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block mb-1">
                            Documento de Contexto Fático (Referência)
                          </span>
                          <pre className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-52">
                            {tc.context_document}
                          </pre>
                        </div>

                        {/* Expected Output */}
                        <div>
                          <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block mb-1">
                            Resposta Esperada (Ground Truth)
                          </span>
                          <pre className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/40 font-mono text-xs text-emerald-200 whitespace-pre-wrap overflow-x-auto leading-relaxed">
                            {tc.expected_output}
                          </pre>
                        </div>

                        {/* Guardrails and Keywords */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                              <FileCheck className="w-3.5 h-3.5 text-indigo-400" />
                              <span>Palavras-chave Obrigatórias</span>
                            </span>
                            {kws.length === 0 ? (
                              <p className="text-slate-500 text-[11px]">Nenhuma restrição específica.</p>
                            ) : (
                              <div className="flex flex-wrap gap-1.5 pt-1">
                                {kws.map((k, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-mono text-[11px] border border-slate-700"
                                  >
                                    {k}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                              <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                              <span>Termos Proibidos (Guardrails)</span>
                            </span>
                            {fts.length === 0 ? (
                              <p className="text-slate-500 text-[11px]">Nenhum termo vedado.</p>
                            ) : (
                              <div className="flex flex-wrap gap-1.5 pt-1">
                                {fts.map((f, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-0.5 rounded bg-rose-950/40 text-rose-300 font-mono text-[11px] border border-rose-800/40"
                                  >
                                    {f}
                                  </span>
                                ))}
                              </div>
                            )}
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
      )}

      {/* Tab: Form Add Case */}
      {activeSubTab === 'add_case' && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-medium tracking-tight text-slate-100">
                Cadastrar Novo Caso de Teste
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Dataset de destino: <span className="font-semibold text-slate-200">{selectedDataset?.name || 'Não selecionado'}</span>
              </p>
            </div>
            <button
              onClick={() => setActiveSubTab('cases')}
              className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancelar
            </button>
          </div>

          <form onSubmit={handleCreateCase} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Título do Caso *
              </label>
              <input
                type="text"
                value={newCaseTitle}
                onChange={(e) => setNewCaseTitle(e.target.value)}
                placeholder="Ex: Prescrição Intercorrente em Execução Fiscal (Art. 40 LEF)"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Pergunta / Consulta do Usuário *
              </label>
              <textarea
                value={newCaseQuery}
                onChange={(e) => setNewCaseQuery(e.target.value)}
                rows={3}
                placeholder="Ex: Quais são os requisitos para reconhecimento da prescrição intercorrente na execução fiscal?"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Documento de Contexto Fático / Jurídico *
              </label>
              <textarea
                value={newCaseContext}
                onChange={(e) => setNewCaseContext(e.target.value)}
                rows={4}
                placeholder="Ex: Cole o texto do acórdão, parecer ou dispositivo legal de base..."
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Resposta Esperada (Ground Truth) *
              </label>
              <textarea
                value={newCaseExpected}
                onChange={(e) => setNewCaseExpected(e.target.value)}
                rows={3}
                placeholder="Ex: Resposta jurídica exata e concisa esperada da IA..."
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Palavras-chave Obrigatórias
                </label>
                <input
                  type="text"
                  value={newCaseKeywords}
                  onChange={(e) => setNewCaseKeywords(e.target.value)}
                  placeholder="art. 40, LEF, 5 anos, suspensão (separadas por vírgula)"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Termos que o modelo DEVE conter para pontuar em relevância.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Termos Proibidos (Guardrails)
                </label>
                <input
                  type="text"
                  value={newCaseForbidden}
                  onChange={(e) => setNewCaseForbidden(e.target.value)}
                  placeholder="imprescritível, 10 anos, prazo decadencial (separados por vírgula)"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Se presentes na resposta, o caso será sumariamente reprovado.
                </p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setActiveSubTab('cases')}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={submittingCase}
                className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors"
              >
                {submittingCase ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Salvando...</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-3.5 h-3.5" />
                    <span>Salvar Caso de Teste</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tab: Form Add Dataset */}
      {activeSubTab === 'add_dataset' && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-medium tracking-tight text-slate-100">
                Criar Novo Golden Dataset
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Crie um novo repositório de casos de teste para uma área jurídica específica.
              </p>
            </div>
            <button
              onClick={() => setActiveSubTab('cases')}
              className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancelar
            </button>
          </div>

          <form onSubmit={handleCreateDataset} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Nome do Dataset *
              </label>
              <input
                type="text"
                value={newDsName}
                onChange={(e) => setNewDsName(e.target.value)}
                placeholder="Ex: Direito Societário — Dissolução Parcial de Sociedade"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Categoria
                </label>
                <select
                  value={newDsCategory}
                  onChange={(e) => setNewDsCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                >
                  <option value="TRIBUTARIO">Tributário</option>
                  <option value="SOCIETARIO">Societário</option>
                  <option value="CONTRATOS">Contratos</option>
                  <option value="TRABALHISTA">Trabalhista</option>
                  <option value="REGULATORIO">Regulatório</option>
                  <option value="GERAL">Geral</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Descrição (Opcional)
                </label>
                <input
                  type="text"
                  value={newDsDesc}
                  onChange={(e) => setNewDsDesc(e.target.value)}
                  placeholder="Ex: Bateria para validação de apuração de haveres"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setActiveSubTab('cases')}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={submittingDs}
                className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors"
              >
                {submittingDs ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Criando...</span>
                  </>
                ) : (
                  <>
                    <FolderPlus className="w-3.5 h-3.5" />
                    <span>Criar Dataset</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
