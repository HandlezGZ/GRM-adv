import React, { useState } from 'react';
import {
  FileText,
  RefreshCw,
  Search,
  Building2,
  Tag,
  DollarSign,
  Scale,
  Calendar,
  CheckCircle2,
  Copy,
  Check,
  Percent,
  Layers,
  Sparkles,
} from 'lucide-react';
import { formatBRL, formatCNPJ, formatDate } from '../utils/formatters';

export default function VisualizadorExtracao({
  documents,
  activeDocument,
  extraction,
  onSelectDocument,
  onReprocessExtraction,
  isExtracting,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('full'); // 'full' or 'chunks'
  const [copiedText, setCopiedText] = useState(false);

  if (!activeDocument) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-12 text-center">
        <FileText className="mx-auto h-10 w-10 text-slate-400 mb-3" />
        <h3 className="text-base font-medium text-slate-100">
          Nenhum documento selecionado
        </h3>
        <p className="mt-1 text-xs text-slate-400">
          Selecione um documento na Central de Documentos para visualizar o texto integral e entidades fiscais extraídas.
        </p>
      </div>
    );
  }

  const rawText = activeDocument.raw_text || '';
  const chunks = activeDocument.chunks || [];

  const handleCopy = () => {
    navigator.clipboard.writeText(rawText);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const getTaxBadgeColor = (tax) => {
    const t = tax.toUpperCase();
    if (t.includes('ICMS')) return 'border-orange-500/20 bg-orange-500/10 text-orange-300';
    if (t.includes('PIS')) return 'border-cyan-500/20 bg-cyan-500/10 text-cyan-300';
    if (t.includes('COFINS')) return 'border-blue-500/20 bg-blue-500/10 text-blue-300';
    if (t.includes('IRPJ')) return 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300';
    if (t.includes('CSLL')) return 'border-teal-500/20 bg-teal-500/10 text-teal-300';
    if (t.includes('ISS')) return 'border-indigo-500/20 bg-indigo-500/10 text-indigo-300';
    return 'border-purple-500/20 bg-purple-500/10 text-purple-300';
  };

  // Filter chunks if in chunks mode
  const filteredChunks = chunks.filter((c) =>
    searchTerm === '' ? true : c.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Document Selector Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <FileText className="h-5 w-5" />
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

        {/* Reprocess Extraction Button */}
        <button
          onClick={() => onReprocessExtraction(activeDocument.id)}
          disabled={isExtracting}
          className="flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 text-blue-400 ${isExtracting ? 'animate-spin' : ''}`} />
          <span>{isExtracting ? 'Extraindo Entidades...' : 'Reprocessar Extração'}</span>
        </button>
      </div>

      {/* Split Layout: Left Raw Text, Right Structured Entities */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Panel: Document Raw Text & Search */}
        <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm flex flex-col h-[760px] overflow-hidden">
          {/* Panel Header */}
          <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-950/40">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-200">
                Texto Integral do Documento
              </span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                {activeDocument.total_pages || 1} pág{activeDocument.total_pages > 1 ? 's' : ''}
              </span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                {chunks.length} chunks
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* View Switcher */}
              <div className="flex rounded-lg border border-slate-800 bg-slate-950 p-0.5 text-[11px]">
                <button
                  onClick={() => setViewMode('full')}
                  className={`px-2 py-0.5 rounded ${
                    viewMode === 'full' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Texto Contínuo
                </button>
                <button
                  onClick={() => setViewMode('chunks')}
                  className={`px-2 py-0.5 rounded ${
                    viewMode === 'chunks' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Chunks Indexados
                </button>
              </div>

              {/* Copy Button */}
              <button
                onClick={handleCopy}
                title="Copiar texto integral"
                className="flex items-center gap-1 rounded border border-slate-800 bg-slate-950 px-2 py-1 text-[11px] text-slate-300 hover:bg-slate-800 transition-colors"
              >
                {copiedText ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span className="text-emerald-400">Copiado</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 text-slate-400" />
                    <span>Copiar</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="px-4 py-2 border-b border-slate-800/80 bg-slate-950/20">
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="Localizar termos no texto fiscal (ex: multa, ICMS, prazo)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-md border border-slate-800 bg-slate-950 py-1 pl-8 pr-3 text-xs text-slate-200 placeholder-slate-400 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Text Area / Scroll View */}
          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs text-slate-300 leading-relaxed bg-slate-950/30">
            {viewMode === 'full' ? (
              <pre className="whitespace-pre-wrap font-mono text-xs selection:bg-blue-600/30">
                {rawText}
              </pre>
            ) : (
              <div className="space-y-3">
                {filteredChunks.map((chunk, idx) => (
                  <div
                    key={chunk.id || idx}
                    className="rounded-lg border border-slate-800 bg-slate-950/60 p-3"
                  >
                    <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5 pb-1 border-b border-slate-800/80 font-mono">
                      <span>Chunk #{chunk.chunk_index ?? idx} (Página {chunk.page_number || 1})</span>
                      <span>{chunk.token_count || 0} tokens</span>
                    </div>
                    <p className="text-slate-300 leading-normal whitespace-pre-wrap">
                      {chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Left Footer Info */}
          <div className="px-4 py-2 border-t border-slate-800 bg-slate-950/60 text-[10px] font-mono text-slate-400 flex items-center justify-between">
            <span>SHA-256: {activeDocument.sha256_hash || 'Disponível após verificação'}</span>
            <span>Total Caracteres: {rawText.length.toLocaleString('pt-BR')}</span>
          </div>
        </div>

        {/* Right Panel: Structured Tax Entities */}
        <div className="lg:col-span-5 space-y-4 overflow-y-auto max-h-[760px] pr-1">
          {/* Card: Contribuinte & Órgão Autuante */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              <Building2 className="h-4 w-4 text-blue-400" />
              <span>Contribuinte & Órgão Fiscal</span>
            </div>

            <div className="rounded-lg border border-slate-800/80 bg-slate-950/60 p-3 space-y-2">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Razão Social / Sujeito Passivo
                </span>
                <span className="text-sm font-semibold text-slate-100">
                  {extraction?.contribuinte_nome || 'Não identificado no documento'}
                </span>
              </div>
              <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-mono text-slate-400 block">
                    CNPJ / CPF
                  </span>
                  <span className="font-mono font-medium text-slate-300">
                    {formatCNPJ(extraction?.contribuinte_cnpj_cpf)}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-mono text-slate-400 block">
                    Período Apuração
                  </span>
                  <span className="font-mono text-slate-300">
                    {extraction?.periodo_apuracao || 'Competência contínua'}
                  </span>
                </div>
              </div>
              <div className="pt-1 border-t border-slate-800/60">
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Órgão Autuante / Jurisdição
                </span>
                <span className="text-xs text-slate-200">
                  {extraction?.orgao_fiscal || 'Administração Tributária Competente'}
                </span>
              </div>
            </div>
          </div>

          {/* Card: Tributos Envolvidos */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              <Tag className="h-4 w-4 text-emerald-400" />
              <span>Tributos Envolvidos</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {extraction?.tributos_identificados && extraction.tributos_identificados.length > 0 ? (
                extraction.tributos_identificados.map((tax) => (
                  <span
                    key={tax}
                    className={`rounded-md border px-2.5 py-1 text-xs font-mono font-semibold ${getTaxBadgeColor(
                      tax
                    )}`}
                  >
                    {tax}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">
                  Nenhum tributo específico detectado
                </span>
              )}
            </div>
          </div>

          {/* Card: Decomposição de Valores */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              <DollarSign className="h-4 w-4 text-emerald-400" />
              <span>Decomposição do Crédito Tributário</span>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5">
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Valor Principal
                </span>
                <span className="text-sm font-semibold font-mono text-slate-200">
                  {formatBRL(extraction?.valor_principal)}
                </span>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5">
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Multa de Ofício
                </span>
                <span className="text-sm font-semibold font-mono text-rose-300">
                  {formatBRL(extraction?.valor_multa)}
                </span>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5">
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Juros de Mora / Selic
                </span>
                <span className="text-sm font-semibold font-mono text-amber-300">
                  {formatBRL(extraction?.valor_juros)}
                </span>
              </div>

              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5">
                <span className="text-[10px] uppercase font-mono text-emerald-400 font-semibold block">
                  Total Geral Exigido
                </span>
                <span className="text-sm font-bold font-mono text-emerald-300">
                  {formatBRL(extraction?.valor_total)}
                </span>
              </div>
            </div>
          </div>

          {/* Card: Dispositivos Legais Invocados */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              <Scale className="h-4 w-4 text-purple-400" />
              <span>Dispositivos Legais Infringidos</span>
            </div>

            <ul className="space-y-1.5">
              {extraction?.dispositivos_legais && extraction.dispositivos_legais.length > 0 ? (
                extraction.dispositivos_legais.map((art, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 rounded-lg border border-slate-800/80 bg-slate-950/50 p-2 text-xs text-slate-300"
                  >
                    <span className="text-blue-400 font-mono text-[11px] shrink-0">
                      §{idx + 1}
                    </span>
                    <span className="font-mono text-[11px]">{art}</span>
                  </li>
                ))
              ) : (
                <li className="text-xs text-slate-400">
                  Nenhum artigo legal identificado
                </li>
              )}
            </ul>
          </div>

          {/* Card: Prazos e Metadados */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
              <Calendar className="h-4 w-4 text-cyan-400" />
              <span>Datas e Auditoria</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <span className="text-[10px] text-slate-400 block font-mono">Data Lavratura</span>
                <span className="font-medium text-slate-200">
                  {formatDate(extraction?.data_lavratura)}
                </span>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <span className="text-[10px] text-slate-400 block font-mono">Data Intimação</span>
                <span className="font-medium text-slate-200">
                  {formatDate(extraction?.data_intimacao)}
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span>Método: {extraction?.extraction_method || 'RULES_DETERMINISTIC'}</span>
              <span className="text-emerald-400 font-semibold">
                Confiança: {Math.round((extraction?.confidence_score || 0.95) * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
