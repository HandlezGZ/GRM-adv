import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import IntakeForm from './components/IntakeForm';
import RequestsTable from './components/RequestsTable';
import ReviewDetailsView from './components/ReviewDetailsView';
import QualityFailuresView from './components/QualityFailuresView';
import { 
  getHealth, 
  getDashboardMetrics, 
  listRequests, 
  createRequest, 
  listFailures 
} from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedRequestId, setSelectedRequestId] = useState(null);

  // Global state
  const [health, setHealth] = useState(null);
  const [isHealthLoading, setIsHealthLoading] = useState(false);

  const [metrics, setMetrics] = useState(null);
  const [isMetricsLoading, setIsMetricsLoading] = useState(false);

  const [requests, setRequests] = useState([]);
  const [totalRequests, setTotalRequests] = useState(0);
  const [isRequestsLoading, setIsRequestsLoading] = useState(false);

  const [failures, setFailures] = useState([]);
  const [isFailuresLoading, setIsFailuresLoading] = useState(false);

  const [filters, setFilters] = useState({
    status: 'TODOS',
    category: 'TODAS',
    priority: 'TODAS',
    search: '',
  });

  // Health fetch
  const fetchHealth = useCallback(async () => {
    setIsHealthLoading(true);
    const data = await getHealth();
    setHealth(data);
    setIsHealthLoading(false);
  }, []);

  // Metrics fetch
  const fetchMetrics = useCallback(async () => {
    setIsMetricsLoading(true);
    try {
      const data = await getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.warn('Could not load metrics:', err);
    } finally {
      setIsMetricsLoading(false);
    }
  }, []);

  // Requests fetch
  const fetchRequests = useCallback(async () => {
    setIsRequestsLoading(true);
    try {
      const res = await listRequests({
        status: filters.status,
        category: filters.category,
        priority: filters.priority,
        search: filters.search,
        limit: 50,
        offset: 0,
      });
      setRequests(res.items || []);
      setTotalRequests(res.total || 0);
    } catch (err) {
      console.warn('Could not load requests:', err);
    } finally {
      setIsRequestsLoading(false);
    }
  }, [filters]);

  // Failures fetch
  const fetchFailures = useCallback(async () => {
    setIsFailuresLoading(true);
    try {
      const data = await listFailures();
      setFailures(data || []);
    } catch (err) {
      console.warn('Could not load failures:', err);
    } finally {
      setIsFailuresLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchHealth();
    fetchMetrics();
    fetchRequests();
    fetchFailures();
  }, [fetchHealth, fetchMetrics, fetchRequests, fetchFailures]);

  // Navigate to review with a selected request
  const handleSelectRequest = (id) => {
    setSelectedRequestId(id);
    setActiveTab('review');
  };

  // Intake submit handler
  const handleCreateRequest = async (payload) => {
    const created = await createRequest(payload);
    // Refresh lists and dashboard
    fetchMetrics();
    fetchRequests();
    return created;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Header / Navigation */}
      <Navbar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        health={health}
        onRefreshHealth={fetchHealth}
        isHealthLoading={isHealthLoading}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <DashboardView
            metrics={metrics}
            recentRequests={requests}
            onSelectRequest={handleSelectRequest}
            onNavigateIntake={() => setActiveTab('intake')}
            onNavigateRequests={() => setActiveTab('requests')}
            isLoading={isMetricsLoading}
            onRefresh={() => {
              fetchMetrics();
              fetchRequests();
            }}
          />
        )}

        {activeTab === 'intake' && (
          <IntakeForm
            onSubmitSuccess={handleCreateRequest}
            onNavigateReview={handleSelectRequest}
          />
        )}

        {activeTab === 'requests' && (
          <RequestsTable
            requests={requests}
            total={totalRequests}
            onSelectRequest={handleSelectRequest}
            filters={filters}
            onFilterChange={setFilters}
            isLoading={isRequestsLoading}
            onRefresh={fetchRequests}
          />
        )}

        {activeTab === 'review' && (
          <ReviewDetailsView
            requestId={selectedRequestId}
            allRequests={requests}
            onSelectRequest={setSelectedRequestId}
            onRefreshList={() => {
              fetchRequests();
              fetchMetrics();
            }}
          />
        )}

        {activeTab === 'failures' && (
          <QualityFailuresView
            failures={failures}
            health={health}
            isLoading={isFailuresLoading}
            onRefresh={fetchFailures}
            onSelectRequest={handleSelectRequest}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-400">LexFlow</span>
            <span>&bull;</span>
            <span>Process Automation &amp; Request Triage</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="font-mono">FastAPI + React + Tailwind CSS</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
