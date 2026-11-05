import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  CheckCircle2, 
  AlertCircle, 
  Bot, 
  ArrowRight,
  Info,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { CATEGORIES, PRIORITIES, getPriorityMeta, getCategoryLabel } from '../constants';
import { testClassifyText } from '../api';

export default function IntakeForm({ onSubmitSuccess, onNavigateReview }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'NORMAL',
    department: '',
    requester_name: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isClassifying, setIsClassifying] = useState(false);
  const [aiPreview, setAiPreview] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleTestClassification = async () => {
    if (!formData.title || formData.title.trim().length < 5) {
      setErrorMsg('Informe um título com no mínimo 5 caracteres para testar a classificação.');
      return;
    }
    if (!formData.description || formData.description.trim().length < 10) {
      setErrorMsg('Informe uma descrição com no mínimo 10 caracteres para testar a classificação.');
      return;
    }

    setErrorMsg(null);
    setIsClassifying(true);
    try {
      const result = await testClassifyText(formData.title, formData.description);
      setAiPreview(result);
    } catch (err) {
      setErrorMsg(`Erro ao testar classificação: ${err.message}`);
    } finally {
      setIsClassifying(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || formData.title.trim().length < 5) {
      setErrorMsg('O título deve conter no mínimo 5 caracteres.');
      return;
    }
    if (!formData.description || formData.description.trim().length < 10) {
      setErrorMsg('A descrição deve conter no mínimo 10 caracteres.');
      return;
    }

    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category ? formData.category : (aiPreview?.category || null),
        priority: formData.priority || (aiPreview?.priority || 'NORMAL'),
        department: formData.department.trim() || null,
        requester_name: formData.requester_name.trim() || 'Usuário Operacional',
      };

      const result = await onSubmitSuccess(payload);
      setSuccessResult(result);
      setFormData({
        title: '',
        description: '',
        category: '',
        priority: 'NORMAL',
        department: '',
        requester_name: '',
      });
      setAiPreview(null);
    } catch (err) {
      setErrorMsg(err.message || 'Falha ao cadastrar a solicitação.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-medium tracking-tight text-slate-100">Nova Solicitação</h1>
        <p className="text-sm leading-relaxed text-slate-400">
          Registre uma demanda operacional para triagem determinística ou por inteligência artificial.
        </p>
      </div>

      {/* Success Banner */}
      {successResult && (
        <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/30 p-5 backdrop-blur-sm animate-fadeIn">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-emerald-200">
                  Solicitação protocolada com sucesso!
                </h3>
                <p className="text-xs text-emerald-400/80 mt-1">
                  Protocolo: <span className="font-mono font-medium">{successResult.id}</span>
                </p>
                <p className="text-xs text-slate-300 mt-2">
                  Status atual: <span className="font-medium text-slate-100">{successResult.status}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onNavigateReview(successResult.id)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/30 hover:bg-emerald-600/40 text-emerald-200 text-xs font-medium border border-emerald-500/30 transition-colors"
              >
                Inspecionar Demanda
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setSuccessResult(null)}
                className="px-2 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 text-xs transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {errorMsg && (
        <div className="rounded-xl border border-rose-800/50 bg-rose-950/30 p-4 backdrop-blur-sm flex items-start gap-3 text-rose-200 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">{errorMsg}</div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Container */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 space-y-5">
            {/* Title */}
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Título da Solicitação <span className="text-indigo-400">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Ex.: Liberação de acesso ao sistema de pesquisa de jurisprudência"
                className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                maxLength={120}
                required
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Mínimo 5 caracteres, máximo 120.</span>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                Descrição Detalhada <span className="text-indigo-400">*</span>
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={5}
                placeholder="Descreva a necessidade com contexto operacional, justificativa e eventuais sistemas envolvidos..."
                className="w-full px-3.5 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-y"
                required
              />
              <span className="text-[11px] text-slate-500 mt-1 block">Mínimo 10 caracteres.</span>
            </div>

            {/* Requester & Department */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Solicitante
                </label>
                <input
                  type="text"
                  name="requester_name"
                  value={formData.requester_name}
                  onChange={handleChange}
                  placeholder="Ex.: Lucas Mendes"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
                  Departamento
                </label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  placeholder="Ex.: Contencioso Cível"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>

            {/* Manual Override (Optional) */}
            <div className="pt-2 border-t border-slate-800/80">
              <div className="text-xs text-slate-400 mb-3 font-medium">Classificação Preliminar (Opcional)</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Categoria</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    <option value="">Deixar para classificação automática</option>
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Prioridade Inicial</label>
                  <select
                    name="priority"
                    value={formData.priority}
                    onChange={handleChange}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    {PRIORITIES.map((prio) => (
                      <option key={prio.value} value={prio.value}>
                        {prio.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <button
              type="button"
              onClick={handleTestClassification}
              disabled={isClassifying || !formData.title || !formData.description}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Bot className={`w-4 h-4 text-indigo-400 ${isClassifying ? 'animate-spin' : ''}`} />
              {isClassifying ? 'Classificando...' : 'Testar Classificação IA'}
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
              {isSubmitting ? 'Cadastrando...' : 'Cadastrar Solicitação'}
            </button>
          </div>
        </form>

        {/* AI Preview Card / Sidebar */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <Bot className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-medium text-slate-200 tracking-tight">Prévia da IA</h3>
            </div>

            {aiPreview ? (
              <div className="space-y-4 animate-fadeIn">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-2">
                  <div className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Categoria Sugerida</div>
                  <div className="text-sm font-medium text-slate-100">
                    {getCategoryLabel(aiPreview.category)}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <div className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Equipe</div>
                    <div className="text-xs font-medium text-indigo-300">{aiPreview.team}</div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <div className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Prioridade</div>
                    <div className="text-xs font-medium text-slate-200">{aiPreview.priority}</div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Confiança</span>
                    <span className="text-xs font-mono text-emerald-400">
                      {Math.round((aiPreview.confidence || 0) * 100)}%
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mt-1">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${(aiPreview.confidence || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Justificativa</div>
                  <p className="text-xs leading-relaxed text-slate-300 bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                    {aiPreview.reason}
                  </p>
                </div>

                <div className="pt-2 text-[11px] text-slate-500 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                  Origem do motor: <span className="font-mono text-slate-400">{aiPreview.source}</span>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center space-y-3">
                <Info className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 leading-relaxed">
                  Preencha o título e descrição ao lado e clique em <strong className="text-slate-300">"Testar Classificação IA"</strong> para obter sugestão instantânea de equipe, prioridade e categoria.
                </p>
              </div>
            )}
          </div>

          {/* Quick tips card */}
          <div className="rounded-xl border border-slate-800/60 bg-slate-900/30 p-4 text-xs text-slate-400 space-y-2">
            <div className="font-medium text-slate-300">Dica de Produtividade</div>
            <p>
              O classificador do LexFlow avalia termos-chave e intenções operacionais para rotear diretamente para as equipes de TI, Operações ou Inovação sem gargalos manuais.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
