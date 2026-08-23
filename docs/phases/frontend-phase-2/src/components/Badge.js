/**
 * Multi-Modal Status Badge Component (Phase 2)
 */
export function Badge({
  text,
  variant = 'neutral',
  icon = '',
  className = '',
}) {
  const defaultIcons = {
    success: '✓',
    warning: '◷',
    danger: '✕',
    info: 'ℹ',
    neutral: '•',
  };

  const badgeIcon = icon || defaultIcons[variant] || '•';

  return `
    <span class="badge ${variant} ${className}" role="status">
      <span aria-hidden="true">${badgeIcon}</span>
      <span>${text}</span>
    </span>
  `;
}
