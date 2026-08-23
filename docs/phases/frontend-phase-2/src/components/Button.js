/**
 * UX4G Button Component (Phase 2)
 */
export function Button({
  text,
  variant = 'primary',
  href = null,
  id = '',
  disabled = false,
  className = '',
  type = 'button',
  icon = '',
  onClick = null,
}) {
  const baseClasses = `btn ${variant} ${className}`.trim();
  const iconMarkup = icon ? `<span class="btn-icon" aria-hidden="true">${icon}</span>` : '';
  const content = `${iconMarkup}<span>${text}</span>`;

  if (href) {
    return `<a href="${href}" id="${id}" class="${baseClasses}" ${disabled ? 'aria-disabled="true" tabindex="-1"' : ''}>${content}</a>`;
  }

  return `<button type="${type}" id="${id}" class="${baseClasses}" ${disabled ? 'disabled' : ''}>${content}</button>`;
}
