const RAW_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const ROOT_URL = RAW_URL.replace(/\/api\/v1\/?$/, '');
const API_V1 = `${ROOT_URL}/api/v1`;

async function request(endpoint, options = {}) {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_V1}${path}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      let errorMsg = `HTTP error: ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData && errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // ignore json parse error on response
      }
      throw new Error(errorMsg);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Request Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Health: attempts root /health and /api/v1/health gracefully
  getHealth: async () => {
    try {
      const res = await fetch(`${API_V1}/health`, { signal: AbortSignal.timeout(2500) });
      if (res.ok) return await res.json();
    } catch {
      // try root /health
    }
    const resRoot = await fetch(`${ROOT_URL}/health`, { signal: AbortSignal.timeout(2500) });
    if (!resRoot.ok) throw new Error(`Health error: ${resRoot.status}`);
    return await resRoot.json();
  },

  // Dashboard
  getDashboardMetrics: () => request('/dashboard/metrics'),

  // Datasets
  getDatasets: () => request('/datasets'),
  getDataset: (id) => request(`/datasets/${id}`),
  createDataset: (data) => request('/datasets', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getDatasetCases: (datasetId) => request(`/datasets/${datasetId}/cases`),
  createTestCase: (datasetId, data) => request(`/datasets/${datasetId}/cases`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Prompts
  getPrompts: () => request('/prompts'),
  createPrompt: (data) => request('/prompts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Eval runs
  triggerEvalRun: (payload) => request('/eval/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getEvalRuns: (limit = 50) => request(`/eval/runs?limit=${limit}`),
  getEvalRunDetail: (runId) => request(`/eval/runs/${runId}`),

  // Comparison
  compareRuns: (runAId, runBId) => 
    request(`/eval/compare?run_a_id=${encodeURIComponent(runAId)}&run_b_id=${encodeURIComponent(runBId)}`),

  // Failures
  getFailures: ({ datasetId, runId, reason, limit = 100 } = {}) => {
    const params = new URLSearchParams();
    if (datasetId) params.append('dataset_id', datasetId);
    if (runId) params.append('run_id', runId);
    if (reason) params.append('reason', reason);
    if (limit) params.append('limit', limit.toString());
    const query = params.toString();
    return request(`/eval/failures${query ? `?${query}` : ''}`);
  },
};
