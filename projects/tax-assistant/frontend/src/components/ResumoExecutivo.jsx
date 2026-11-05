import React, { useState } from 'react';
import {
  FileSpreadsheet,
  ShieldAlert,
  ShieldCheck,
  Clock,
  Calendar,
  DollarSign,
  Copy,
  Check,
  Download,
  AlertTriangle,
  ArrowRight,
  FileText,
  BookmarkCheck,
} from 'lucide-react';
import { formatBRL, formatDate } from '../utils/formatters';

export default function ResumoExecutivo({
  documents,
  activeDocument,
  summary,
  onSelectDocument,
  isLoading,
}) {
  const [copied, setCopied] = useState(false);

  if (!activeDocument) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-12 text-center">
        <FileSpreadsheet className="mx-auto h-10 w-10 text-slate-400 mb-3" />
        <h3 className="text-base font-medium text-slate-100">
          Nenhum documento selecionado
        </h3>
        <p className="mt-1 text-xs text-slate-400">
          Selecione um documento na Central de Documentos para visualizar a análise de risco e linha do tempo de prazos.
        </p>
      </div>
    );
  }

  const risk = summary?.grau_risco || 'MEDIO';
  const totalAmount = summary?.total_autuado || 0;
  const prazos = summary?.prazos || {};
  const tese = summary?.tese_acusacao || 'Exigência de crédito tributário e aplicação de sanções legais.';
  const memoText = summary?.resumo_texto || '';

  const handleCopyMemo = () => {
    navigator.clipboard.writeText(memoText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadMemo = () => {
    const blob = new Blob([memoText], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `memorando_${activeDocument.filename.replace(/\.[^/.]+$/, '')}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getRiskDetails = (riskLevel) => {
    switch (riskLevel) {
      case 'ALTO':
        return {
          color: 'text-rose-400',
          bg: 'bg-rose-500/10 border-rose-500/20',
          icon: ShieldAlert,
          title: 'Grau de Risco Elevado',
          description:
            'Autuação com valor vultoso ou multa qualificada de ofício (50% a 75%). Risco de execução fiscal prioritária.',
        };
      case 'MEDIO':
        return {
          color: 'text-amber-400',
          bg: 'bg-amber-500/10 border-amber-500/20',
          icon: AlertTriangle,
          title: 'Grau de Risco Moderado',
          description:
            'Exigência tributária comum com possibilidade de discussão meritória em sede administrativa.',
        };
      default:
        return {
          color: 'text-emerald-400',
          bg: 'bg-emerald-500/10 border-emerald-500/20',
          icon: ShieldCheck,
          title: 'Grau de Risco Baixo / Preventivo',
          description:
            'Matéria consultiva ou com impacto pecuniário imediato reduzido.',
        };
    }
  };

  const riskInfo = getRiskDetails(risk);
  const RiskIcon = riskInfo.icon;

  const timelineSteps = [
    {
      title: 'Lavratura do Auto',
      date: summary?.prazos?.data_lavratura || activeDocument?.created_at,
      status: 'Concluído',
      detail: 'Formalização do lançamento fiscal de ofício pelo auditor',
      completed: true,
    },
    {
      title: 'Intimação do Sujeito Passivo',
      date: prazos?.data_intimacao || '20/02/2024',
      status: 'Concluído',
      detail: 'Início da contagem preclusiva dos prazos de defesa',
      completed: true,
    },
    {
      title: 'Vencimento c/ Desconto Legal',
      date: prazos?.prazo_pagamento_com_desconto || prazos?.data_vencimento || '30 dias',
      status: 'Vigente',
      detail: 'Redução de até 50% no valor da multa para pagamento integral',
      completed: false,
      current: true,
    },
    {
      title: 'Prazo Limite para Impugnação',
      date: prazos?.prazo_impugnacao_administrativa || '30 dias da intimação',
      status: 'Pendente',
      detail: 'Prazo fatal de 30 dias para defesa perante o contencioso administrativo',
      completed: false,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Document Selector Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <FileSpreadsheet className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <label className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-0.5">
              Documento Fiscal Selecionado
            </label>
            <select
              value={activeDocument.id}
              onChange={(e) => onSelectDocument(e.target.value)}
              className="w-full sm:max-w-md rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-medium text-slate-100 focus:border-blue-500 focus:outline-none"
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.document_type})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyMemo}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copiado</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-400" />
                <span>Copiar Memorando</span>
              </>
            )}
          </button>
          <button
            onClick={handleDownloadMemo}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-medium text-white hover:bg-blue-500 shadow-sm transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Baixar (.md)</span>
          </button>
        </div>
      </div>

      {/* Top 3 Analytical Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Risk Card */}
        <div className={`rounded-xl border p-5 ${riskInfo.bg} backdrop-blur-sm shadow-sm`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Grau de Risco & Contingência
            </span>
            <RiskIcon className={`h-5 w-5 ${riskInfo.color}`} />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className={`text-2xl font-bold font-mono tracking-tight ${riskInfo.color}`}>
              {risk}
            </span>
            <span className="text-xs font-medium text-slate-300">
              {riskInfo.title}
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            {riskInfo.description}
          </p>
        </div>

        {/* Impugnação Deadline Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Prazo Limite para Impugnação
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {prazos?.prazo_impugnacao_administrativa || '30 dias'}
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Prazo fatal para defesa tempestiva e suspensão da exigibilidade do crédito tributário.
          </p>
        </div>

        {/* Total Financial Demand Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Exigência Fiscal Total
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <DollarSign className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {formatBRL(totalAmount)}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
            <span>Principal: {formatBRL(summary?.valor_principal)}</span>
            <span>|</span>
            <span>Multa: {formatBRL(summary?.valor_multa)}</span>
          </div>
        </div>
      </div>

      {/* Procedural Deadlines Timeline */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Calendar className="h-5 w-5 text-blue-400" />
          <h2 className="text-base font-medium tracking-tight text-slate-100">
            Linha do Tempo Processual e Prazos Decadenciais / Preclusivos
          </h2>
        </div>

        <div className="relative">
          {/* Timeline Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {timelineSteps.map((step, idx) => (
              <div
                key={step.title}
                className={`relative rounded-xl border p-4 transition-all ${
                  step.current
                    ? 'border-blue-500/40 bg-blue-500/10 shadow-sm shadow-blue-500/10'
                    : step.completed
                    ? 'border-slate-800 bg-slate-950/60'
                    : 'border-slate-800/80 bg-slate-950/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] text-slate-400 uppercase">
                    Etapa {idx + 1}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-mono font-medium ${
                      step.current
                        ? 'bg-blue-500/20 text-blue-300'
                        : step.completed
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {step.status}
                  </span>
                </div>

                <h3 className="text-xs font-semibold text-slate-200 mb-1">
                  {step.title}
                </h3>
                <div className="font-mono text-sm font-bold text-slate-100 mb-2">
                  {formatDate(step.date)}
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {step.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Allegation Thesis & Complete Executive Memo */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Allegation Thesis */}
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookmarkCheck className="h-5 w-5 text-purple-400" />
              <h3 className="text-sm font-medium tracking-tight text-slate-100">
                Tese de Acusação Fiscal
              </h3>
            </div>
            <div className="rounded-lg border border-purple-500/20 bg-purple-500/5 p-4 text-xs text-purple-200 leading-relaxed">
              {tese}
            </div>

            <div className="mt-5">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-400 block mb-2">
                Fundamentação Normativa Resumida
              </span>
              <div className="space-y-1.5">
                {summary?.dispositivos_legais?.slice(0, 4).map((art, i) => (
                  <div
                    key={i}
                    className="rounded border border-slate-800 bg-slate-950/60 px-2.5 py-1.5 font-mono text-[11px] text-slate-300"
                  >
                    {art}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-400">
            Recomenda-se protocolo de defesa no contencioso administrativo antes de qualquer inscrição em Dívida Ativa.
          </div>
        </div>

        {/* Executive Memo Markdown View */}
        <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-medium tracking-tight text-slate-100">
                Memorando Resumido Completo
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Formato Markdown Jurídico
            </span>
          </div>

          <div className="rounded-lg border border-slate-800/80 bg-slate-950/70 p-4 font-mono text-xs text-slate-300 leading-relaxed max-h-[460px] overflow-y-auto whitespace-pre-wrap selection:bg-blue-600/30">
            {memoText || 'Carregando resumo executivo estruturado...'}
          </div>
        </div>
      </div>
    </div>
  );
}
