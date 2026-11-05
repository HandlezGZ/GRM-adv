// LexFlow API Client

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

/**
 * Check backend health
 */
export async function getHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`Health error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API health check error:', err);
    return null;
  }
}

/**
 * Get dashboard consolidated metrics
 */
export async function getDashboardMetrics() {
  const res = await fetch(`${API_V1}/dashboard/metrics`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch metrics: ${res.status}`);
  }
  return await res.json();
}

/**
 * List requests with optional filters and pagination
 */
export async function listRequests({
  status = null,
  category = null,
  priority = null,
  search = null,
  limit = 50,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit);
  if (offset) params.append('offset', offset);
  if (status && status !== 'ALL' && status !== 'TODOS') params.append('status', status);
  if (category && category !== 'ALL' && category !== 'TODAS') params.append('category', category);
  if (priority && priority !== 'ALL' && priority !== 'TODAS') params.append('priority', priority);
  if (search && search.trim().length >= 2) params.append('search', search.trim());

  const res = await fetch(`${API_V1}/requests?${params.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch requests: ${res.status}`);
  }
  return await res.json();
}

/**
 * Create a new request
 */
export async function createRequest(payload) {
  const res = await fetch(`${API_V1}/requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create request: ${res.status}`);
  }
  return await res.json();
}

/**
 * Get request details by ID
 */
export async function getRequestDetails(requestId) {
  const res = await fetch(`${API_V1}/requests/${requestId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to get request: ${res.status}`);
  }
  return await res.json();
}

/**
 * Classify a request by ID
 */
export async function classifyRequest(requestId) {
  const res = await fetch(`${API_V1}/requests/${requestId}/classify`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to classify request: ${res.status}`);
  }
  return await res.json();
}

/**
 * Test classification for raw title and description
 * If backend has no standalone endpoint, fallback to deterministic classification
 */
export async function testClassifyText(title, description) {
  try {
    const res = await fetch(`${API_V1}/classification/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('POST /api/v1/classification/classify unavailable, using local rules engine:', err);
  }

  // Deterministic local rule engine matching backend RulesClassifier
  return localRulesClassification(title, description);
}

/**
 * Human review of classification
 */
export async function reviewRequest(requestId, payload) {
  const res = await fetch(`${API_V1}/requests/${requestId}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to review classification: ${res.status}`);
  }
  return await res.json();
}

/**
 * Update request workflow status
 */
export async function updateRequestStatus(requestId, { newStatus, reason = null, actor = 'demo_user' }) {
  const res = await fetch(`${API_V1}/requests/${requestId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      new_status: newStatus,
      reason,
      actor,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update status: ${res.status}`);
  }
  return await res.json();
}

/**
 * Get request audit events
 */
export async function getRequestEvents(requestId) {
  const res = await fetch(`${API_V1}/requests/${requestId}/events`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch events: ${res.status}`);
  }
  return await res.json();
}

/**
 * List classification failures
 */
export async function listFailures(limit = 50) {
  // Try /api/v1/failures/classification first, then fallback to /api/v1/classification/failures
  try {
    const res = await fetch(`${API_V1}/failures/classification?limit=${limit}`);
    if (res.ok) return await res.json();
  } catch (err) {
    // try fallback
  }

  const res2 = await fetch(`${API_V1}/classification/failures?limit=${limit}`);
  if (!res2.ok) {
    const errorData = await res2.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to list failures: ${res2.status}`);
  }
  return await res2.json();
}

// Local rules-based classifier mirroring backend logic
function normalizeText(text) {
  return (text || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

function localRulesClassification(title, description) {
  const fullText = `${title || ''} ${description || ''}`;
  const norm = normalizeText(fullText);

  const mappings = {
    ACCESS_AND_SYSTEMS: {
      team: 'TI / Suporte',
      keywords: [
        'acesso', 'login', 'senha', 'password', 'reset', 'vpn',
        'software', 'sistema', 'ferramenta', 'token', 'certificado',
        'permissao', 'computador', 'notebook', 'email', 'outlook',
        'bloqueio', 'desbloqueio', 'suporte',
      ],
      reason: 'Demanda relacionada a contas, permissões, acessos ou suporte técnico.',
    },
    DOCUMENTS_AND_TEMPLATES: {
      team: 'Operações',
      keywords: [
        'modelo', 'minuta', 'procuracao', 'template', 'contrato padrao',
        'documento interno', 'clausula', 'formulario', 'substabelecimento',
        'padronizacao', 'cabecalho',
      ],
      reason: 'Demanda relacionada a minutas, modelos institucionais e documentos padrão.',
    },
    DATA_AND_REPORTS: {
      team: 'Dados / Inovação',
      keywords: [
        'relatorio', 'dados', 'extracao', 'planilha', 'metrica',
        'bi', 'dashboard', 'volumetria', 'exportacao', 'sql',
        'estatistica', 'grafico', 'painel', 'indicador',
      ],
      reason: 'Demanda analítica, envolvendo dados, relatórios ou consolidação de planilhas.',
    },
    AI_AND_AUTOMATION: {
      team: 'Inovação',
      keywords: [
        'automacao', 'ia', 'inteligencia artificial', 'llm', 'bot',
        'chat', 'fluxo automatico', 'robo', 'script', 'inovacao',
        'prompt', 'agente', 'ocr',
      ],
      reason: 'Demanda de novos fluxos automatizados, inteligência artificial ou inovação.',
    },
    INTERNAL_REQUEST: {
      team: 'Operações',
      keywords: [
        'sala de reuniao', 'compra', 'material', 'equipamento',
        'cracha', 'estacionamento', 'manutencao predial', 'escritorio',
        'viagem', 'reembolso', 'nota fiscal', 'despesa', 'correios',
        'copiadora', 'impressora',
      ],
      reason: 'Demanda operacional ou administrativa de infraestrutura e suprimentos.',
    },
  };

  const urgentKeywords = [
    'urgente', 'emergencia', 'imediato', 'prazo fatal', 'hoje',
    'critico', 'parado', 'fora do ar', 'bloqueado',
  ];
  const highKeywords = ['alta prioridade', 'importante', 'prioritario', 'breve', 'amanha'];
  const lowKeywords = ['sugestao', 'quando possivel', 'sem pressa', 'baixa', 'duvida geral'];

  let bestCategory = 'OTHER';
  let bestScore = 0;

  for (const [cat, config] of Object.entries(mappings)) {
    let score = 0;
    for (const kw of config.keywords) {
      const regex = new RegExp(`\\b${kw}\\b`, 'g');
      const matches = norm.match(regex);
      if (matches) score += matches.length;
    }
    if (score > bestScore) {
      bestScore = score;
      bestCategory = cat;
    }
  }

  let priority = 'NORMAL';
  if (urgentKeywords.some((w) => new RegExp(`\\b${w}\\b`).test(norm))) {
    priority = 'URGENT';
  } else if (highKeywords.some((w) => new RegExp(`\\b${w}\\b`).test(norm))) {
    priority = 'HIGH';
  } else if (lowKeywords.some((w) => new RegExp(`\\b${w}\\b`).test(norm))) {
    priority = 'LOW';
  }

  if (bestScore === 0) {
    return {
      category: 'OTHER',
      team: 'Triagem',
      priority,
      confidence: 0.50,
      reason: 'Nenhuma regra determinística encontrou correspondência clara. Encaminhado para triagem geral.',
      source: 'rules',
      fallback_used: false,
    };
  }

  const confidence = Math.min(0.65 + bestScore * 0.10, 0.95);
  const cfg = mappings[bestCategory];
  let reason = cfg.reason;
  if (priority === 'URGENT') {
    reason += ' Identificados termos críticos; prioridade urgente requer confirmação.';
  }

  return {
    category: bestCategory,
    team: cfg.team,
    priority,
    confidence: Number(confidence.toFixed(2)),
    reason,
    source: 'rules',
    fallback_used: false,
  };
}
