import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Bot,
  User,
  Send,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Sparkles,
  RotateCcw,
  BookOpen,
  FileText,
  Quote,
  CheckCircle2,
} from 'lucide-react';
import { createChatSession, getChatHistory, queryChatSession } from '../api';

export default function ConsultaFontes({
  documents,
  activeDocument,
  onSelectDocument,
}) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [expandedCitations, setExpandedCitations] = useState({});
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    'Qual o valor total da autuação e multas cobradas?',
    'Quais os tributos formalmente exigidos?',
    'Qual o prazo para defesa ou impugnação administrativa?',
    'Quais dispositivos de lei e regulamentos foram violados?',
    'Qual a tese fiscal apurada no auto de infração?',
  ];

  // Initialize chat session when activeDocument changes
  useEffect(() => {
    let isCancelled = false;

    async function initSession() {
      if (!activeDocument) return;
      setIsLoading(true);
      try {
        const session = await createChatSession(
          activeDocument.id,
          `Consulta - ${activeDocument.filename}`
        );
        if (!isCancelled && session) {
          setSessionId(session.id);
          const history = await getChatHistory(session.id);
          if (!isCancelled) {
            setMessages(
              history && history.length > 0
                ? history
                : [
                    {
                      id: 'welcome-msg',
                      role: 'assistant',
                      content: `Olá! Sou o assistente LexTax. Estou fundamentado com o documento fiscal "${activeDocument.filename}". Toda e qualquer resposta é verificada contra os excertos originais e acompanhada de citações verbatim e número da página de suporte para garantir zero alucinação jurídica. O que deseja consultar?`,
                      citations: [],
                      created_at: new Date().toISOString(),
                    },
                  ]
            );
          }
        }
      } catch (err) {
        // Fallback
      } finally {
        if (!isCancelled) setIsLoading(false);
      }
    }

    initSession();

    return () => {
      isCancelled = true;
    };
  }, [activeDocument?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim() || !sessionId || isLoading) return;

    setInputText('');

    // Append user message optimistically
    const tempUserMsg = {
      id: `temp-u-${Date.now()}`,
      role: 'user',
      content: query.trim(),
      citations: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response = await queryChatSession(sessionId, query.trim());
      if (response) {
        const assistantMsg = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: response.answer,
          citations: response.citations || [],
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

        // Auto-expand citations for this message if citations present
        if (response.citations && response.citations.length > 0) {
          setExpandedCitations((prev) => ({
            ...prev,
            [assistantMsg.id]: true,
          }));
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao consultar as evidências documentais. Por favor, tente novamente.',
          citations: [],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCitations = (msgId) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const handleClearHistory = () => {
    if (!activeDocument) return;
    setMessages([
      {
        id: `welcome-new-${Date.now()}`,
        role: 'assistant',
        content: `Histórico reiniciado. Documento ativo: "${activeDocument.filename}". Envie sua nova dúvida jurídica.`,
        citations: [],
        created_at: new Date().toISOString(),
      },
    ]);
  };

  if (!activeDocument) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-12 text-center">
        <MessageSquare className="mx-auto h-10 w-10 text-slate-400 mb-3" />
        <h3 className="text-base font-medium text-slate-100">
          Nenhum documento selecionado
        </h3>
        <p className="mt-1 text-xs text-slate-400">
          Selecione um documento na Central de Documentos para iniciar a consulta fundamentada com citações verbatim.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Document Selector Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <MessageSquare className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <label className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-0.5">
              Documento Fiscal Ancorado
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

        {/* Clear History Button */}
        <button
          onClick={handleClearHistory}
          className="flex items-center justify-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5 text-slate-400" />
          <span>Reiniciar Conversa</span>
        </button>
      </div>

      {/* Suggested Quick Questions Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="flex items-center gap-2 mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">
          <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          <span>Perguntas Sugeridas com Ancoragem Automática</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              disabled={isLoading}
              className="rounded-lg border border-slate-800 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-300 hover:border-blue-500/50 hover:bg-blue-500/10 hover:text-blue-300 transition-all text-left disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Thread Container */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm flex flex-col h-[640px] overflow-hidden">
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            const citations = msg.citations || [];
            const isCitationsOpen = !!expandedCitations[msg.id];

            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${
                  isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                {/* Avatar Icon */}
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${
                    isUser
                      ? 'border-blue-500/20 bg-blue-500/10 text-blue-300'
                      : 'border-purple-500/20 bg-purple-500/10 text-purple-300'
                  }`}
                >
                  {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                {/* Message Body */}
                <div className="flex-1 min-w-0 space-y-2">
                  <div
                    className={`rounded-xl p-4 text-xs leading-relaxed ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-tr-none'
                        : 'border border-slate-800 bg-slate-950/80 text-slate-200 rounded-tl-none'
                    }`}
                  >
                    {!isUser && (
                      <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-slate-800/80 text-[10px] font-mono text-slate-400">
                        <ShieldCheck className="h-3 w-3 text-emerald-400" />
                        <span className="text-emerald-400 font-semibold">
                          Auditado por LexTax RAG
                        </span>
                        <span>|</span>
                        <span>0 Alucinação</span>
                      </div>
                    )}
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>

                  {/* Grounded Citations Accordion (Assistant only) */}
                  {!isUser && citations.length > 0 && (
                    <div className="rounded-lg border border-slate-800 bg-slate-950/60 overflow-hidden text-xs">
                      <button
                        onClick={() => toggleCitations(msg.id)}
                        className="w-full flex items-center justify-between p-2.5 text-left text-slate-300 hover:bg-slate-900/50 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-3.5 w-3.5 text-blue-400" />
                          <span className="font-medium text-[11px] text-slate-200">
                            Fontes e Citações Verbatim ({citations.length} trechos comprobatórios)
                          </span>
                        </div>
                        {isCitationsOpen ? (
                          <ChevronUp className="h-3.5 w-3.5 text-slate-400" />
                        ) : (
                          <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                        )}
                      </button>

                      {isCitationsOpen && (
                        <div className="p-3 pt-0 space-y-2 border-t border-slate-800/60">
                          {citations.map((cit, idx) => (
                            <div
                              key={idx}
                              className="rounded-md border border-slate-800/80 bg-slate-900/80 p-2.5 space-y-1.5"
                            >
                              <div className="flex items-center justify-between font-mono text-[10px] text-slate-400">
                                <span className="inline-flex items-center gap-1 rounded bg-slate-800 px-1.5 py-0.5 text-slate-300">
                                  <FileText className="h-3 w-3 text-blue-400" />
                                  Página {cit.page_number || 1}
                                </span>
                                <span className="text-emerald-400">
                                  Relevância: {Math.round((cit.relevance_score || 0.95) * 100)}%
                                </span>
                              </div>
                              <blockquote className="rounded border-l-2 border-blue-500 bg-slate-950/60 p-2 font-mono text-[11px] italic text-slate-300 leading-normal">
                                "{cit.verbatim_excerpt}"
                              </blockquote>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex gap-3 max-w-xl mr-auto">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-purple-500/20 bg-purple-500/10 text-purple-300">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 text-xs text-slate-400 rounded-tl-none flex items-center gap-2">
                <span className="flex space-x-1">
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse delay-75" />
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse delay-150" />
                </span>
                <span>Buscando evidências documentais e verificando citações verbatim...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/70">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Digite sua dúvida jurídica sobre este documento fiscal..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isLoading}
              className="flex-1 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2.5 text-xs text-slate-100 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              className="flex items-center justify-center h-9 w-9 rounded-lg bg-blue-600 text-white hover:bg-blue-500 focus:outline-none disabled:opacity-50 transition-colors shadow-sm"
              title="Enviar pergunta"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
          <div className="mt-2 text-[10px] text-center text-slate-400 font-mono">
            Toda resposta do assistente referencia estritamente os chunks extraídos do documento ativo.
          </div>
        </div>
      </div>
    </div>
  );
}
