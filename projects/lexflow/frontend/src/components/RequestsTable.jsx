import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  ArrowUpRight, 
  RefreshCw, 
  ChevronLeft, 
  ChevronRight,
  SlidersHorizontal,
  X
} from 'lucide-react';
import { 
  CATEGORIES, 
  PRIORITIES, 
  STATUSES, 
  getCategoryLabel, 
  getPriorityMeta, 
  getStatusMeta, 
  formatDate 
} from '../constants';

export default function RequestsTable({
  requests,
  total,
  onSelectRequest,
  filters,
  onFilterChange,
  isLoading,
  onRefresh,
}) {
  const [searchInput, setSearchInput] = useState(filters.search || '');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onFilterChange({ ...filters, search: searchInput });
  };

  const handleClearFilters = () => {
    setSearchInput('');
    onFilterChange({
      status: 'TODOS',
      category: 'TODAS',
      priority: 'TODAS',
      search: '',
    });
  };

  const hasActiveFilters = 
    (filters.status && filters.status !== 'TODOS') ||
    (filters.category && filters.category !== 'TODAS') ||
    (filters.priority && filters.priority !== 'TODAS') ||
    (filters.search && filters.search.trim().length > 0);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium tracking-tight text-slate-100">Solicitações</h1>
          <p className="text-sm leading-relaxed text-slate-400">
            Gerenciamento centralizado de demandas, filtros operacionais e auditoria.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 text-xs font-medium transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm p-4 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Buscar por título ou descrição (mínimo 2 letras)..."
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => {
                  setSearchInput('');
                  onFilterChange({ ...filters, search: '' });
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
          >
            Buscar
          </button>
        </form>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800/60">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <SlidersHorizontal className="w-3.5 h-3.5 text-slate-500" />
            <span>Filtros:</span>
          </div>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => onFilterChange({ ...filters, status: e.target.value })}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
          >
            <option value="TODOS">Todos os Status</option>
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                Status: {s.label}
              </option>
            ))}
          </select>

          {/* Priority Filter */}
          <select
            value={filters.priority}
            onChange={(e) => onFilterChange({ ...filters, priority: e.target.value })}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
          >
            <option value="TODAS">Todas as Prioridades</option>
            {PRIORITIES.map((p) => (
              <option key={p.value} value={p.value}>
                Prioridade: {p.label}
              </option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={filters.category}
            onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
          >
            <option value="TODAS">Todas as Categorias</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 ml-auto transition-colors"
            >
              <X className="w-3.5 h-3.5" />
              Limpar filtros
            </button>
          )}
        </div>
      </div>

      {/* Table Container */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-slate-400">Carregando solicitações...</p>
          </div>
        ) : requests.length === 0 ? (
          <div className="py-16 text-center text-sm text-slate-400">
            Nenhuma solicitação encontrada para os critérios informados.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-400 bg-slate-950/60 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-medium">Protocolo</th>
                  <th className="py-3 px-4 font-medium">Título</th>
                  <th className="py-3 px-4 font-medium">Solicitante</th>
                  <th className="py-3 px-4 font-medium">Categoria</th>
                  <th className="py-3 px-4 font-medium">Prioridade</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                  <th className="py-3 px-4 font-medium">Data</th>
                  <th className="py-3 px-4 font-medium text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-normal">
                {requests.map((req) => {
                  const prioMeta = getPriorityMeta(req.priority);
                  const statusMeta = getStatusMeta(req.status);

                  return (
                    <tr
                      key={req.id}
                      className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                      onClick={() => onSelectRequest(req.id)}
                    >
                      <td className="py-3.5 px-4 font-mono text-xs text-indigo-400 font-medium">
                        {req.id.slice(0, 8)}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-200 max-w-xs truncate">
                        {req.title}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-400">
                        {req.requester_name || 'Não informado'}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-300">
                        {getCategoryLabel(req.category)}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${prioMeta.badgeClass}`}
                        >
                          {prioMeta.label}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${statusMeta.badgeClass}`}
                        >
                          {statusMeta.label}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-400 whitespace-nowrap">
                        {formatDate(req.created_at)}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectRequest(req.id);
                          }}
                          className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-100 px-2.5 py-1 rounded bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 transition-colors"
                        >
                          Ver Detalhes
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer info */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between text-xs text-slate-400">
          <span>Exibindo {requests.length} de {total || requests.length} registro(s)</span>
          <span className="font-mono">LexFlow Data Engine</span>
        </div>
      </div>
    </div>
  );
}
