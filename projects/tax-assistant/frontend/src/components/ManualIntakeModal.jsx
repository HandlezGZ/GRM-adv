import React, { useState } from 'react';
import { X, FileCode, Check, Sparkles, Send } from 'lucide-react';
import { SAMPLE_TEXT_TEMPLATES } from '../utils/sampleData';

export default function ManualIntakeModal({ isOpen, onClose, onSubmit, isSubmitting }) {
  const [filename, setFilename] = useState('AIIM_Simulado_2024.txt');
  const [docType, setDocType] = useState('AIIM');
  const [text, setText] = useState(SAMPLE_TEXT_TEMPLATES[0].text);
  const [activeTemplateIdx, setActiveTemplateIdx] = useState(0);

  if (!isOpen) return null;

  const handleSelectTemplate = (idx) => {
    setActiveTemplateIdx(idx);
    const tmpl = SAMPLE_TEXT_TEMPLATES[idx];
    setFilename(tmpl.filename);
    setDocType(tmpl.type);
    setText(tmpl.text);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit({
      filename: filename.trim() || 'documento_fiscal.txt',
      text: text.trim(),
      document_type: docType,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="w-full max-w-3xl rounded-xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <FileCode className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-medium tracking-tight text-slate-100">
                Ingestão Manual de Documento Fiscal
              </h3>
              <p className="text-xs text-slate-400">
                Simulação e processamento de texto integral para extração determinística
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Preset Templates */}
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-2">
              Modelos Rápidos Pré-configurados:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {SAMPLE_TEXT_TEMPLATES.map((tmpl, idx) => (
                <button
                  key={tmpl.name}
                  type="button"
                  onClick={() => handleSelectTemplate(idx)}
                  className={`flex flex-col text-left p-2.5 rounded-lg border text-xs transition-all ${
                    activeTemplateIdx === idx
                      ? 'border-blue-500 bg-blue-500/10 text-blue-300'
                      : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <span className="font-medium text-slate-200 truncate">{tmpl.name}</span>
                  <span className="text-[10px] text-slate-400 mt-1 uppercase font-mono">
                    Tipo: {tmpl.type}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="text-xs font-medium text-slate-300 block mb-1.5">
                Nome do Arquivo
              </label>
              <input
                type="text"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                placeholder="exemplo_aiim.txt"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1.5">
                Tipo do Documento
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="AIIM">AIIM (Auto de Infração)</option>
                <option value="NL">NL (Notificação de Lançamento)</option>
                <option value="COSIT">COSIT (Solução de Consulta)</option>
                <option value="DARF">DARF (Guia de Arrecadação)</option>
                <option value="OUTRO">OUTRO</option>
              </select>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300">
                Texto Integral do Documento
              </label>
              <span className="text-[11px] font-mono text-slate-400">
                {text.length.toLocaleString('pt-BR')} caracteres
              </span>
            </div>
            <textarea
              rows={12}
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300 font-mono leading-relaxed focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
              placeholder="Cole aqui o texto do documento fiscal ou auto de infração..."
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !text.trim()}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-medium text-white shadow-sm hover:bg-blue-500 focus:outline-none disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? (
                <span>Processando...</span>
              ) : (
                <>
                  <Send className="h-3.5 w-3.5" />
                  <span>Cadastrar & Processar</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
