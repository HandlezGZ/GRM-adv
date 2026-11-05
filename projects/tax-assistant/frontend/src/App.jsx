import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import CentralDocumentos from './components/CentralDocumentos';
import VisualizadorExtracao from './components/VisualizadorExtracao';
import ResumoExecutivo from './components/ResumoExecutivo';
import ConsultaFontes from './components/ConsultaFontes';
import {
  getHealth,
  getDashboardMetrics,
  getDocuments,
  getDocument,
  uploadDocument,
  intakeTextDocument,
  extractDocument,
  getDocumentSummary,
} from './api';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('central');
  const [health, setHealth] = useState({ ok: false, status: 'checking' });
  const [checkingHealth, setCheckingHealth] = useState(false);
  const [metrics, setMetrics] = useState({
    total_documents: 0,
    total_tax_amount: 0,
    total_debt_brl: 0,
    total_principal_brl: 0,
    total_multa_brl: 0,
    total_juros_brl: 0,
    open_proceedings: 0,
    high_risk_documents: 0,
    aiim_count: 0,
    total_pages_analyzed: 0,
    documents_by_type: {},
    average_confidence_score: 0.95,
  });

  const [documents, setDocuments] = useState([]);
  const [activeDocId, setActiveDocId] = useState(null);
  const [activeDocDetails, setActiveDocDetails] = useState(null);
  const [activeDocExtraction, setActiveDocExtraction] = useState(null);
  const [activeDocSummary, setActiveDocSummary] = useState(null);

  const [isUploading, setIsUploading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };

  // Check health of backend
  const checkHealthStatus = useCallback(async () => {
    setCheckingHealth(true);
    try {
      const h = await getHealth();
      setHealth(h);
    } finally {
      setCheckingHealth(false);
    }
  }, []);

  // Fetch initial documents and metrics
  const loadData = useCallback(async () => {
    try {
      const [m, docs] = await Promise.all([
        getDashboardMetrics(),
        getDocuments(),
      ]);
      setMetrics(m);
      setDocuments(docs);
      if (docs.length > 0 && !activeDocId) {
        setActiveDocId(docs[0].id);
      }
    } catch (err) {
      // Handled
    }
  }, [activeDocId]);

  useEffect(() => {
    checkHealthStatus();
    loadData();
    const interval = setInterval(checkHealthStatus, 30000);
    return () => clearInterval(interval);
  }, [checkHealthStatus, loadData]);

  // Load active document details, extraction, and summary when activeDocId changes
  useEffect(() => {
    let isCancelled = false;
    async function loadActiveDoc() {
      if (!activeDocId) return;
      try {
        const [doc, ext, sum] = await Promise.all([
          getDocument(activeDocId),
          extractDocument(activeDocId),
          getDocumentSummary(activeDocId),
        ]);
        if (!isCancelled) {
          setActiveDocDetails(doc);
          setActiveDocExtraction(ext);
          setActiveDocSummary(sum);
        }
      } catch (err) {
        // Fallback
      }
    }
    loadActiveDoc();
    return () => {
      isCancelled = true;
    };
  }, [activeDocId]);

  // Handle file upload (PDF or TXT)
  const handleUploadFile = async (file) => {
    setIsUploading(true);
    try {
      const newDoc = await uploadDocument(file);
      showNotification(`Documento "${file.name}" processado com sucesso!`);
      await loadData();
      if (newDoc?.id) {
        setActiveDocId(newDoc.id);
      }
    } catch (err) {
      showNotification(err.message || 'Erro ao fazer upload do documento.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle manual text intake
  const handleIntakeText = async (data) => {
    setIsUploading(true);
    try {
      const newDoc = await intakeTextDocument(data);
      showNotification(`Documento "${data.filename}" registrado com sucesso!`);
      await loadData();
      if (newDoc?.id) {
        setActiveDocId(newDoc.id);
      }
    } catch (err) {
      showNotification(err.message || 'Erro ao registrar texto do documento.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  // Reprocess extraction
  const handleReprocessExtraction = async (docId) => {
    setIsExtracting(true);
    try {
      const ext = await extractDocument(docId, true);
      const sum = await getDocumentSummary(docId);
      setActiveDocExtraction(ext);
      setActiveDocSummary(sum);
      showNotification('Entidades fiscais reprocessadas com sucesso!');
      await loadData();
    } catch (err) {
      showNotification('Falha ao reprocessar extração.', 'error');
    } finally {
      setIsExtracting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Inter',sans-serif] antialiased selection:bg-blue-600/30">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 rounded-xl border border-slate-700 bg-slate-900/95 px-4 py-3 shadow-xl backdrop-blur-md animate-in fade-in slide-in-from-bottom-5">
          {notification.type === 'error' ? (
            <AlertCircle className="h-4 w-4 text-rose-400" />
          ) : (
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          )}
          <span className="text-xs font-medium text-slate-200">
            {notification.message}
          </span>
        </div>
      )}

      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        checkingHealth={checkingHealth}
        onRefreshHealth={checkHealthStatus}
        activeDocument={activeDocDetails}
      />

      {/* Main Content View */}
      <main className="flex-1 mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'central' && (
          <CentralDocumentos
            metrics={metrics}
            documents={documents}
            activeDocument={activeDocDetails}
            onSelectDocument={setActiveDocId}
            onNavigateTab={setActiveTab}
            onUploadFile={handleUploadFile}
            onIntakeText={handleIntakeText}
            isUploading={isUploading}
          />
        )}

        {activeTab === 'visualizador' && (
          <VisualizadorExtracao
            documents={documents}
            activeDocument={activeDocDetails}
            extraction={activeDocExtraction}
            onSelectDocument={setActiveDocId}
            onReprocessExtraction={handleReprocessExtraction}
            isExtracting={isExtracting}
          />
        )}

        {activeTab === 'resumo' && (
          <ResumoExecutivo
            documents={documents}
            activeDocument={activeDocDetails}
            summary={activeDocSummary}
            onSelectDocument={setActiveDocId}
          />
        )}

        {activeTab === 'chat' && (
          <ConsultaFontes
            documents={documents}
            activeDocument={activeDocDetails}
            onSelectDocument={setActiveDocId}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 text-center text-xs text-slate-400">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>LexTax - Auditoria Documental e Inteligência Tributária</span>
          <span className="font-mono text-[11px]">
            Arquitetura RAG Ancorada • 0 Alucinação
          </span>
        </div>
      </footer>
    </div>
  );
}
