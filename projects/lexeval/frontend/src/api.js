const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
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
      let errorMsg = `HTTP error! Status: ${res.status}`;
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
  // Health
  getHealth: () => request('/health'),

  // Dashboard
  getDashboardMetrics: () => request('/api/v1/dashboard/metrics'),

  // Datasets
  getDatasets: () => request('/api/v1/datasets'),
  getDataset: (id) => request(`/api/v1/datasets/${id}`),
  createDataset: (data) => request('/api/v1/datasets', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getDatasetCases: (datasetId) => request(`/api/v1/datasets/${datasetId}/cases`),
  createTestCase: (datasetId, data) => request(`/api/v1/datasets/${datasetId}/cases`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Prompts
  getPrompts: () => request('/api/v1/prompts'),
  createPrompt: (data) => request('/api/v1/prompts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Eval runs
  triggerEvalRun: (payload) => request('/api/v1/eval/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getEvalRuns: (limit = 50) => request(`/api/v1/eval/runs?limit=${limit}`),
  getEvalRunDetail: (runId) => request(`/api/v1/eval/runs/${runId}`),

  // Comparison
  compareRuns: (runAId, runBId) => 
    request(`/api/v1/eval/compare?run_a_id=${encodeURIComponent(runAId)}&run_b_id=${encodeURIComponent(runBId)}`),

  // Failures
  getFailures: ({ datasetId, runId, reason, limit = 100 } = {}) => {
    const params = new URLSearchParams();
    if (datasetId) params.append('dataset_id', datasetId);
    if (runId) params.append('run_id', runId);
    if (reason) params.append('reason', reason);
    if (limit) params.append('limit', limit.toString());
    const query = params.toString();
    return request(`/api/v1/eval/failures${query ? `?${query}` : ''}`);
  },
};
