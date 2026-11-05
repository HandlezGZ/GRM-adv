/**
 * Formats a numeric value into Brazilian Real (BRL) currency format.
 * Example: 1234567.89 -> "R$ 1.234.567,89"
 */
export function formatBRL(value) {
  if (value === null || value === undefined || isNaN(Number(value))) {
    return 'R$ 0,00';
  }
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

/**
 * Formats a date string or timestamp into pt-BR date format (DD/MM/YYYY).
 */
export function formatDate(dateStr) {
  if (!dateStr) return 'Não informado';
  try {
    // If it's already in DD/MM/YYYY format
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr.trim())) {
      return dateStr.trim();
    }
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('pt-BR');
  } catch {
    return dateStr;
  }
}

/**
 * Formats file size in bytes to a human-readable format.
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

/**
 * Formats a CNPJ string into standard XX.XXX.XXX/XXXX-XX pattern.
 */
export function formatCNPJ(cnpj) {
  if (!cnpj) return 'Não localizado';
  const clean = cnpj.replace(/\D/g, '');
  if (clean.length === 14) {
    return clean.replace(
      /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
      '$1.$2.$3/$4-$5'
    );
  }
  return cnpj;
}

/**
 * Truncates text with ellipsis.
 */
export function truncate(text, length = 120) {
  if (!text) return '';
  if (text.length <= length) return text;
  return `${text.slice(0, length)}...`;
}
