import React, { useState, useRef } from 'react';
import {
  FileText,
  DollarSign,
  ShieldAlert,
  Clock,
  UploadCloud,
  FileCode,
  Search,
  Filter,
  Eye,
  FileSpreadsheet,
  MessageSquare,
  CheckCircle2,
  Calendar,
  AlertCircle,
  FileUp,
} from 'lucide-react';
import { formatBRL, formatDate, formatFileSize } from '../utils/formatters';
import ManualIntakeModal from './ManualIntakeModal';

export default function CentralDocumentos({
  metrics,
  documents,
  activeDocument,
  onSelectDocument,
  onNavigateTab,
  onUploadFile,
  onIntakeText,
  isUploading,
}) {
  const [filterType, setFilterType] = useState('TODOS');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const fileInputRef = useRef(null);

  const documentTypes = ['TODOS', 'AIIM', 'NL', 'COSIT', 'DARF'];

  const filteredDocs = documents.filter((doc) => {
    const matchesType = filterType === 'TODOS' || doc.document_type === filterType;
    const matchesSearch =
      searchQuery === '' ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (doc.id && doc.id.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadFile(e.target.files[0]);
    }
  };

  const getDocTypeBadgeStyle = (type) => {
    switch (type) {
      case 'AIIM':
        return 'border-rose-500/20 bg-rose-500/10 text-rose-300';
      case 'NL':
        return 'border-amber-500/20 bg-amber-500/10 text-amber-300';
      case 'COSIT':
        return 'border-blue-500/20 bg-blue-500/10 text-blue-300';
      case 'DARF':
        return 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300';
      default:
        return 'border-slate-700 bg-slate-800 text-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-medium tracking-tight text-slate-100 sm:text-2xl">
          Central de Documentos Fiscais
        </h1>
        <p className="mt-1 text-sm leading-relaxed text-slate-400">
          Visão consolidada do portfólio de contingências, ingestão de autos de infração e acompanhamento de auditoria.
        </p>
      </div>

      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1: Total Documentos */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Total de Documentos
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <FileText className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {metrics.total_documents}
            </span>
            <span className="ml-2 text-xs text-slate-400">
              ({metrics.total_pages_analyzed} páginas analisadas)
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Processados na base de conhecimento vetorial
          </p>
        </div>

        {/* KPI 2: Total em Autuações */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Total em Autuações
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <DollarSign className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {formatBRL(metrics.total_debt_brl || metrics.total_tax_amount)}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Principal somado a multas e encargos moratórios
          </p>
        </div>

        {/* KPI 3: Autos de Infração (AIIM) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Autos de Infração (AIIM)
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <ShieldAlert className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {metrics.aiim_count ?? metrics.documents_by_type?.AIIM ?? 0}
            </span>
            <span className="ml-2 text-xs text-rose-400 font-medium">
              Contingências ativas
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Autuações estaduais e federais em fase de defesa
          </p>
        </div>

        {/* KPI 4: Prazos Próximos */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              Prazos Próximos
            </span>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
              {metrics.high_risk_documents}
            </span>
            <span className="ml-2 text-xs text-amber-400 font-medium">
              Atenção prioritária
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Prazos preclusivos para impugnação administrativa
          </p>
        </div>
      </div>

      {/* Upload & Ingestion Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* PDF/File Dropzone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`lg:col-span-2 rounded-xl border-2 border-dashed p-6 transition-all flex flex-col items-center justify-center text-center cursor-pointer ${
            isDragOver
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-slate-800 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-900/50'
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.txt"
            className="hidden"
          />
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 mb-3">
            <UploadCloud className="h-6 w-6" />
          </div>
          <h3 className="text-sm font-medium text-slate-100 tracking-tight">
            Upload de Documento Fiscal (PDF ou Texto)
          </h3>
          <p className="mt-1 text-xs text-slate-400 max-w-sm">
            Arraste e solte autos de infração (AIIM), notificações de lançamento ou DARFs para extração automática e indexação.
          </p>
          <div className="mt-4 flex items-center gap-3">
            <button
              type="button"
              disabled={isUploading}
              className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-blue-500 disabled:opacity-50"
            >
              <FileUp className="h-3.5 w-3.5" />
              <span>{isUploading ? 'Processando Documento...' : 'Selecionar Arquivo'}</span>
            </button>
            <span className="text-[11px] text-slate-400">PDF, TXT até 25MB</span>
          </div>
        </div>

        {/* Manual Simulation Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
                <FileCode className="h-4 w-4" />
              </div>
              <h3 className="text-sm font-medium text-slate-100 tracking-tight">
                Ingestão Manual / Simulação
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Carregue modelos fiscais predefinidos de AIIM paulista, notificações da Receita Federal ou consultas tributárias COSIT para testes instantâneos.
            </p>
          </div>
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <button
              onClick={() => setIsModalOpen(true)}
              className="w-full flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
            >
              <FileCode className="h-3.5 w-3.5 text-purple-400" />
              <span>Abrir Simulador de Texto</span>
            </button>
          </div>
        </div>
      </div>

      {/* Documents Table Section */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
        {/* Table Toolbar */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Document Type Filter Tabs */}
          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {documentTypes.map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                  filterType === type
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por arquivo ou hash..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 py-1.5 pl-9 pr-3 text-xs text-slate-200 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
              <tr>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Arquivo & Identificador</th>
                <th className="px-4 py-3 font-medium">Páginas</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Data de Cadastro</th>
                <th className="px-4 py-3 font-medium text-right">Ações Rápidas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    Nenhum documento encontrado para o filtro selecionado.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => {
                  const isSelected = activeDocument?.id === doc.id;
                  return (
                    <tr
                      key={doc.id}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isSelected ? 'bg-blue-950/20' : ''
                      }`}
                    >
                      {/* Document Type Badge */}
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-mono font-medium ${getDocTypeBadgeStyle(
                            doc.document_type
                          )}`}
                        >
                          {doc.document_type}
                        </span>
                      </td>

                      {/* Filename & Hash */}
                      <td className="px-4 py-3 font-medium text-slate-200">
                        <div className="flex flex-col">
                          <span className="truncate max-w-xs sm:max-w-md font-sans">
                            {doc.filename}
                          </span>
                          <span className="font-mono text-[10px] text-slate-400 truncate max-w-xs">
                            SHA: {doc.sha256_hash ? doc.sha256_hash.slice(0, 16) : doc.id.slice(0, 16)}...
                          </span>
                        </div>
                      </td>

                      {/* Pages / Size */}
                      <td className="px-4 py-3 text-slate-300 font-mono">
                        {doc.total_pages || 1} pág{doc.total_pages > 1 ? 's' : ''}
                        {doc.file_size_bytes ? (
                          <span className="text-[10px] text-slate-400 block">
                            {formatFileSize(doc.file_size_bytes)}
                          </span>
                        ) : null}
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>{doc.status || 'PROCESSED'}</span>
                        </span>
                      </td>

                      {/* Date */}
                      <td className="px-4 py-3 text-slate-400">
                        {formatDate(doc.created_at)}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            title="Visualizar documento e extração"
                            onClick={() => {
                              onSelectDocument(doc.id);
                              onNavigateTab('visualizador');
                            }}
                            className="flex items-center gap-1 rounded border border-slate-700 bg-slate-800/80 px-2 py-1 text-[11px] text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
                          >
                            <Eye className="h-3 w-3 text-blue-400" />
                            <span>Visualizar</span>
                          </button>
                          <button
                            title="Ver resumo executivo e prazos"
                            onClick={() => {
                              onSelectDocument(doc.id);
                              onNavigateTab('resumo');
                            }}
                            className="flex items-center gap-1 rounded border border-slate-700 bg-slate-800/80 px-2 py-1 text-[11px] text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
                          >
                            <FileSpreadsheet className="h-3 w-3 text-emerald-400" />
                            <span>Resumo</span>
                          </button>
                          <button
                            title="Iniciar consulta fundamentada com fontes"
                            onClick={() => {
                              onSelectDocument(doc.id);
                              onNavigateTab('chat');
                            }}
                            className="flex items-center gap-1 rounded border border-slate-700 bg-slate-800/80 px-2 py-1 text-[11px] text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
                          >
                            <MessageSquare className="h-3 w-3 text-purple-400" />
                            <span>Chat</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Intake Modal */}
      <ManualIntakeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={async (data) => {
          await onIntakeText(data);
          setIsModalOpen(false);
        }}
        isSubmitting={isUploading}
      />
    </div>
  );
}
