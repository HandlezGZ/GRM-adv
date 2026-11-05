export const CATEGORIES = [
  { value: 'ACCESS_AND_SYSTEMS', label: 'Acessos e Sistemas (TI)', team: 'TI / Suporte' },
  { value: 'DOCUMENTS_AND_TEMPLATES', label: 'Modelos e Minutas (Operações)', team: 'Operações' },
  { value: 'DATA_AND_REPORTS', label: 'Dados e Relatórios (Inovação)', team: 'Dados / Inovação' },
  { value: 'AI_AND_AUTOMATION', label: 'IA e Automações (Inovação)', team: 'Inovação' },
  { value: 'INTERNAL_REQUEST', label: 'Solicitação Interna / Suprimentos (Operações)', team: 'Operações' },
  { value: 'OTHER', label: 'Outros (Triagem Geral)', team: 'Triagem' },
];

export const PRIORITIES = [
  { value: 'LOW', label: 'Baixa', badgeClass: 'bg-slate-800 text-slate-300 border-slate-700' },
  { value: 'NORMAL', label: 'Normal', badgeClass: 'bg-blue-950/60 text-blue-300 border-blue-800/60' },
  { value: 'HIGH', label: 'Alta', badgeClass: 'bg-amber-950/60 text-amber-300 border-amber-800/60' },
  { value: 'URGENT', label: 'Urgente', badgeClass: 'bg-rose-950/60 text-rose-300 border-rose-800/60' },
];

export const STATUSES = [
  { value: 'NEW', label: 'Novo', badgeClass: 'bg-slate-800 text-slate-300 border-slate-700' },
  { value: 'TRIAGE', label: 'Triagem', badgeClass: 'bg-amber-950/60 text-amber-300 border-amber-800/60' },
  { value: 'IN_PROGRESS', label: 'Em Andamento', badgeClass: 'bg-indigo-950/60 text-indigo-300 border-indigo-800/60' },
  { value: 'WAITING', label: 'Aguardando', badgeClass: 'bg-yellow-950/60 text-yellow-300 border-yellow-800/60' },
  { value: 'RESOLVED', label: 'Concluído', badgeClass: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60' },
  { value: 'CANCELLED', label: 'Cancelado', badgeClass: 'bg-red-950/60 text-red-300 border-red-800/60' },
];

export function getCategoryLabel(val) {
  const item = CATEGORIES.find((c) => c.value === val);
  return item ? item.label : val || 'Não categorizado';
}

export function getPriorityMeta(val) {
  const item = PRIORITIES.find((p) => p.value === val);
  return item || { value: val, label: val || 'Indefinida', badgeClass: 'bg-slate-800 text-slate-300 border-slate-700' };
}

export function getStatusMeta(val) {
  const item = STATUSES.find((s) => s.value === val);
  return item || { value: val, label: val || 'Indefinido', badgeClass: 'bg-slate-800 text-slate-300 border-slate-700' };
}

export function formatDate(dateString) {
  if (!dateString) return '-';
  try {
    const d = new Date(dateString);
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (e) {
    return dateString;
  }
}
