import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  FileCode, 
  Zap,
  Info,
  Clock,
  ArrowRight
} from 'lucide-react';
import { formatDate } from '../constants';

export default function QualityFailuresView({
  failures = [],
  health,
  onRefresh,
  isLoading,
  onSelectRequest,
}) {
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium tracking-tight text-slate-100">
            Qualidade, Resiliência & Falhas
          </h1>
          <p className="text-sm leading-relaxed text-slate-400">
            Auditoria de incidentes, timeouts de provedores LLM e rastreabilidade do mecanismo de fallback determinístico.
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 text-xs font-medium transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Recarregar Logs
        </button>
      </div>

      {/* System Health / Status summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block mb-2">
            Status do Serviço
          </span>
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-rose-400'
              }`}
            />
            <span className="text-xl font-bold tracking-tight text-slate-100">
              {health?.status === 'healthy' ? 'Operacional' : 'Indisponível'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            {health?.service || 'FastAPI Service'} v{health?.version || '1.0.0'}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block mb-2">
            Modo de Classificação Ativo
          </span>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-indigo-400" />
            <span className="text-xl font-bold tracking-tight text-slate-100 font-mono uppercase">
              {health?.classification_mode || 'rules'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {health?.classification_mode === 'llm'
              ? 'Provedor OpenAI habilitado com fallback'
              : health?.classification_mode === 'hybrid'
              ? 'Abordagem híbrida Rules + LLM'
              : 'Regras determinísticas autônomas'}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block mb-2">
            Incidentes Registrados
          </span>
          <div className="flex items-center gap-2">
            <AlertTriangle
              className={`w-5 h-5 ${
                failures.length > 0 ? 'text-amber-400' : 'text-emerald-400'
              }`}
            />
            <span className="text-xl font-bold tracking-tight text-slate-100">
              {failures.length}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {failures.length === 0
              ? 'Zero falhas de execução no período'
              : 'Tentativas com acionamento de fallback'}
          </p>
        </div>
      </div>

      {/* Failures Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-base font-medium tracking-tight text-slate-100">
              Registro de Falhas e Fallbacks da IA
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Eventos onde a chamada ao modelo falhou e o motor acionou a regra determinística.
            </p>
          </div>
        </div>

        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-slate-400">Consultando logs de falhas...</p>
          </div>
        ) : failures.length === 0 ? (
          <div className="py-16 text-center text-slate-400 space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <p className="text-sm font-medium text-slate-200">
              Nenhuma falha de classificação registrada
            </p>
            <p className="text-xs text-slate-500">
              O motor de IA e os serviços de inferência estão operando com 100% de estabilidade.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-400 bg-slate-950/60 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-medium">ID Tentativa</th>
                  <th className="py-3 px-4 font-medium">Protocolo Solicitação</th>
                  <th className="py-3 px-4 font-medium">Provedor</th>
                  <th className="py-3 px-4 font-medium">Origem</th>
                  <th className="py-3 px-4 font-medium">Tipo do Erro</th>
                  <th className="py-3 px-4 font-medium">Latência</th>
                  <th className="py-3 px-4 font-medium">Data</th>
                  <th className="py-3 px-4 font-medium text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-normal">
                {failures.map((f) => (
                  <tr
                    key={f.id}
                    className="hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-400">
                      {f.id.slice(0, 8)}...
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-indigo-400 font-medium">
                      {f.request_id}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300 font-mono">
                      {f.provider}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {f.source}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-rose-950/60 text-rose-300 border border-rose-800/60">
                        {f.error_type || 'Desconhecido'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {f.duration_ms ? `${f.duration_ms} ms` : '-'}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 whitespace-nowrap">
                      {formatDate(f.created_at)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {onSelectRequest && (
                        <button
                          onClick={() => onSelectRequest(f.request_id)}
                          className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50"
                        >
                          Ver Demanda
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Resilience Architecture Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 space-y-4">
        <h3 className="text-base font-medium tracking-tight text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-indigo-400" />
          Arquitetura de Resiliência & Fallback Determinístico
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300 leading-relaxed">
          <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800/70 space-y-2">
            <div className="font-medium text-slate-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              1. Proteção contra Indisponibilidade (Zero Downtime)
            </div>
            <p className="text-slate-400">
              Quando a API da OpenAI atinge limites de taxa (rate limits), sofre timeout de rede ou devolve payloads incompatíveis, a solicitação não é rejeitada. O fluxo continua transparente.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800/70 space-y-2">
            <div className="font-medium text-slate-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              2. Fallback Heurístico e Determinístico
            </div>
            <p className="text-slate-400">
              O classificador de regras <code className="text-indigo-300">RulesClassifier</code> assume a classificação com base no léxico do vocabulário jurídico interno com alta confiabilidade e baixa latência.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800/70 space-y-2">
            <div className="font-medium text-slate-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              3. Rastreabilidade e Auditoria Completa
            </div>
            <p className="text-slate-400">
              Cada fallback grava um registro persistente em <code className="text-indigo-300">ClassificationAttempt</code> com os metadados do erro, permitindo auditorias técnicas e aprimoramento contínuo dos prompts.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800/70 space-y-2">
            <div className="font-medium text-slate-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              4. Transparência Human-in-the-Loop
            </div>
            <p className="text-slate-400">
              Solicitações classificadas via fallback exibem badge de alerta aos analistas, priorizando a revisão manual imediata para assegurar acurácia operacional de 100%.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
