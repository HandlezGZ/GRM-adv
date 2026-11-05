import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  UserCheck, 
  Clock, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  History, 
  FileText, 
  Send,
  Zap,
  ChevronRight,
  Shield,
  Activity,
  User,
  Building,
  RotateCcw
} from 'lucide-react';
import { 
  CATEGORIES, 
  PRIORITIES, 
  STATUSES, 
  getCategoryLabel, 
  getPriorityMeta, 
  getStatusMeta, 
  formatDate 
} from '../constants';
import { 
  getRequestDetails, 
  getRequestEvents, 
  classifyRequest, 
  reviewRequest, 
  updateRequestStatus 
} from '../api';

export default function ReviewDetailsView({
  requestId,
  allRequests = [],
  onSelectRequest,
  onRefreshList,
}) {
  const [request, setRequest] = useState(null);
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isClassifying, setIsClassifying] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Review Form state
  const [reviewForm, setReviewForm] = useState({
    category: '',
    team: '',
    priority: 'NORMAL',
    review_reason: '',
    reviewer_name: 'Analista de Triagem',
  });

  // Status transition state
  const [newStatus, setNewStatus] = useState('');
  const [statusReason, setStatusReason] = useState('');

  // Load request details and events
  const loadDetails = async (id) => {
    if (!id) return;
    setIsLoading(true);
    setFeedback(null);
    try {
      const [reqData, evData] = await Promise.all([
        getRequestDetails(id),
        getRequestEvents(id),
      ]);
      setRequest(reqData);
      setEvents(evData || []);
      setReviewForm({
        category: reqData.category || 'OTHER',
        team: reqData.team || 'TI / Suporte',
        priority: reqData.priority || 'NORMAL',
        review_reason: '',
        reviewer_name: 'Analista de Triagem',
      });
      setNewStatus(reqData.status);
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Falha ao carregar detalhes.' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (requestId) {
      loadDetails(requestId);
    } else if (allRequests.length > 0) {
      onSelectRequest(allRequests[0].id);
    }
  }, [requestId]);

  const handleRunAiClassification = async () => {
    if (!request) return;
    setIsClassifying(true);
    setFeedback(null);
    try {
      await classifyRequest(request.id);
      setFeedback({ type: 'success', message: 'Classificação executada com sucesso!' });
      await loadDetails(request.id);
      if (onRefreshList) onRefreshList();
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Erro ao executar classificação.' });
    } finally {
      setIsClassifying(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!reviewForm.review_reason || reviewForm.review_reason.trim().length < 5) {
      setFeedback({ type: 'error', message: 'A justificativa da revisão deve conter no mínimo 5 caracteres.' });
      return;
    }

    setIsReviewing(true);
    setFeedback(null);
    try {
      const payload = {
        category: reviewForm.category,
        team: reviewForm.team.trim() || 'Operações',
        priority: reviewForm.priority,
        review_reason: reviewForm.review_reason.trim(),
        reviewer_name: reviewForm.reviewer_name.trim() || 'Analista de Triagem',
      };
      await reviewRequest(request.id, payload);
      setFeedback({ type: 'success', message: 'Revisão humana confirmada e registrada com sucesso!' });
      await loadDetails(request.id);
      if (onRefreshList) onRefreshList();
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Erro ao submeter revisão humana.' });
    } finally {
      setIsReviewing(false);
    }
  };

  const handleStatusChangeSubmit = async (e) => {
    e.preventDefault();
    if (!newStatus || newStatus === request?.status) return;

    setIsUpdatingStatus(true);
    setFeedback(null);
    try {
      await updateRequestStatus(request.id, {
        newStatus,
        reason: statusReason.trim() || `Transição manual de status para ${newStatus}`,
      });
      setFeedback({ type: 'success', message: `Status atualizado para ${newStatus} com sucesso!` });
      setStatusReason('');
      await loadDetails(request.id);
      if (onRefreshList) onRefreshList();
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Erro ao alterar status.' });
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  if (!requestId && allRequests.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-12 text-center text-slate-400">
        Nenhuma solicitação cadastrada para revisão. Cadastre uma solicitação primeiro na aba "Nova Solicitação".
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Quick Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium tracking-tight text-slate-100">Revisão Humana & Detalhes</h1>
          <p className="text-sm leading-relaxed text-slate-400">
            Validação "Human-in-the-Loop", roteamento operacional e trilha de auditoria completa.
          </p>
        </div>

        {/* Quick selector dropdown */}
        {allRequests.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Selecionar:</span>
            <select
              value={requestId || ''}
              onChange={(e) => onSelectRequest(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500 max-w-xs truncate"
            >
              {allRequests.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id.slice(0, 8)} - {r.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Notifications */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border backdrop-blur-sm flex items-start gap-3 text-xs ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
              : 'bg-rose-950/40 border-rose-800/60 text-rose-300'
          }`}
        >
          {feedback.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          )}
          <div className="flex-1">{feedback.message}</div>
          <button
            onClick={() => setFeedback(null)}
            className="text-slate-400 hover:text-slate-200"
          >
            Fechar
          </button>
        </div>
      )}

      {isLoading || !request ? (
        <div className="py-24 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">Carregando dados da solicitação...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Info Banner */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
              <div>
                <div className="flex items-center gap-3 mb-1.5">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                    ID: {request.id}
                  </span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
                      getStatusMeta(request.status).badgeClass
                    }`}
                  >
                    {getStatusMeta(request.status).label}
                  </span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
                      getPriorityMeta(request.priority).badgeClass
                    }`}
                  >
                    Prioridade: {getPriorityMeta(request.priority).label}
                  </span>
                </div>
                <h2 className="text-xl font-medium tracking-tight text-slate-100">{request.title}</h2>
              </div>

              {/* Status Transition & AI classify quick action */}
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={handleRunAiClassification}
                  disabled={isClassifying}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 text-xs font-medium transition-colors disabled:opacity-50"
                >
                  <Bot className={`w-3.5 h-3.5 ${isClassifying ? 'animate-spin' : ''}`} />
                  {isClassifying ? 'Classificando...' : 'Reclassificar com IA'}
                </button>
              </div>
            </div>

            {/* Description & metadata */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-slate-400">
              <div className="md:col-span-2">
                <span className="text-[11px] uppercase tracking-wider text-slate-500 font-medium block mb-1">
                  Descrição
                </span>
                <p className="text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 whitespace-pre-wrap">
                  {request.description}
                </p>
              </div>

              <div className="space-y-3">
                <div>
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-medium block mb-1">
                    Solicitante
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-200">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span>{request.requester_name || 'Não informado'}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-medium block mb-1">
                    Departamento
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-200">
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    <span>{request.department || 'Geral'}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-medium block mb-1">
                    Criado em
                  </span>
                  <span className="text-slate-200">{formatDate(request.created_at)}</span>
                </div>
                <div>
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-medium block mb-1">
                    Última Atualização
                  </span>
                  <span className="text-slate-200">{formatDate(request.updated_at)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Workflow & Classification Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Status Transition Card */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <RotateCcw className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-medium text-slate-200">Mudar Status do Fluxo</h3>
              </div>

              <form onSubmit={handleStatusChangeSubmit} className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Novo Status</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                  >
                    {STATUSES.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label} ({s.value})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Motivo da Alteração</label>
                  <input
                    type="text"
                    value={statusReason}
                    onChange={(e) => setStatusReason(e.target.value)}
                    placeholder="Ex.: Triagem confirmada e direcionada para a fila de TI"
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500 placeholder-slate-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isUpdatingStatus || newStatus === request.status}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUpdatingStatus ? 'Atualizando...' : 'Confirmar Transição'}
                </button>
              </form>
            </div>

            {/* Current AI Classification Snapshot */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <Bot className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-medium text-slate-200">Diagnóstico da IA / Motor</h3>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-[11px] uppercase text-slate-500 font-medium block">Categoria Atual</span>
                  <div className="text-sm font-medium text-slate-100 mt-0.5">
                    {getCategoryLabel(request.category)}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-[11px] uppercase text-slate-500 font-medium block">Equipe</span>
                    <span className="text-slate-200 font-medium">{request.team || 'Não atribuída'}</span>
                  </div>
                  <div>
                    <span className="text-[11px] uppercase text-slate-500 font-medium block">Origem</span>
                    <span className="font-mono text-indigo-400">{request.classification_source || 'Indefinida'}</span>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] uppercase text-slate-500 font-medium">Confiança</span>
                    <span className="font-mono text-emerald-400">
                      {request.classification_confidence 
                        ? `${Math.round(request.classification_confidence * 100)}%` 
                        : 'N/A'}
                    </span>
                  </div>
                  {request.classification_confidence !== null && (
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mt-1">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${(request.classification_confidence || 0) * 100}%` }}
                      />
                    </div>
                  )}
                </div>

                <div>
                  <span className="text-[11px] uppercase text-slate-500 font-medium block mb-1">Justificativa</span>
                  <p className="text-slate-300 bg-slate-950/40 p-2.5 rounded border border-slate-800/60 leading-relaxed text-[11px]">
                    {request.classification_reason || 'Nenhuma justificativa registrada.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Human Review Form */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <UserCheck className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-medium text-slate-200">Revisão Humana (Override)</h3>
              </div>

              <form onSubmit={handleReviewSubmit} className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Categoria Confirmada</label>
                  <select
                    value={reviewForm.category}
                    onChange={(e) => setReviewForm({ ...reviewForm, category: e.target.value })}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                    required
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Equipe</label>
                    <input
                      type="text"
                      value={reviewForm.team}
                      onChange={(e) => setReviewForm({ ...reviewForm, team: e.target.value })}
                      placeholder="TI / Suporte"
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Prioridade</label>
                    <select
                      value={reviewForm.priority}
                      onChange={(e) => setReviewForm({ ...reviewForm, priority: e.target.value })}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                    >
                      {PRIORITIES.map((p) => (
                        <option key={p.value} value={p.value}>
                          {p.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1">Nome do Revisor</label>
                  <input
                    type="text"
                    value={reviewForm.reviewer_name}
                    onChange={(e) => setReviewForm({ ...reviewForm, reviewer_name: e.target.value })}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Justificativa da Revisão <span className="text-indigo-400">*</span>
                  </label>
                  <textarea
                    rows={2}
                    value={reviewForm.review_reason}
                    onChange={(e) => setReviewForm({ ...reviewForm, review_reason: e.target.value })}
                    placeholder="Explique o motivo do ajuste ou confirme a acurácia..."
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={isReviewing}
                  className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors disabled:opacity-50"
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  {isReviewing ? 'Salvando revisão...' : 'Aprovar / Ajustar Classificação'}
                </button>
              </form>
            </div>
          </div>

          {/* Audit Trail Timeline */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-medium text-slate-200">Trilha de Auditoria & Eventos Históricos</h3>
              </div>
              <span className="text-xs text-slate-500 font-mono">{events.length} evento(s)</span>
            </div>

            {events.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                Nenhum evento registrado até o momento.
              </div>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {[...events].reverse().map((ev) => {
                  const isHuman = ev.actor === 'human';
                  const isSystem = ev.actor === 'system';

                  return (
                    <div key={ev.id} className="relative group">
                      {/* Timeline dot */}
                      <div
                        className={`absolute -left-[23px] top-1.5 w-3.5 h-3.5 rounded-full border-2 border-slate-950 ${
                          isHuman ? 'bg-emerald-400' : isSystem ? 'bg-indigo-400' : 'bg-slate-400'
                        }`}
                      />

                      <div className="p-3.5 rounded-lg border border-slate-800/80 bg-slate-950/40 hover:border-slate-700/60 transition-colors">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-slate-200">
                              {ev.event_type}
                            </span>
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60 uppercase">
                              {ev.actor}
                            </span>
                          </div>
                          <span className="text-[11px] text-slate-500 font-mono">
                            {formatDate(ev.created_at)}
                          </span>
                        </div>

                        <p className="text-xs text-slate-300 leading-relaxed">
                          {ev.summary}
                        </p>

                        {ev.metadata_json && (
                          <div className="mt-2 text-[11px] font-mono text-slate-500 bg-slate-900/60 p-2 rounded border border-slate-800/40 overflow-x-auto">
                            {ev.metadata_json}
                          </div>
                        )}
                      </div>
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
