export function formatPrice(price) {
  if (price == null) return '---';
  return price.toFixed(2);
}

export function formatPercent(value) {
  if (value == null) return '---';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

export function formatScore(score) {
  if (score == null) return '--';
  return Math.round(score);
}

export function timeAgo(timestamp) {
  if (!timestamp) return 'never';
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export function directionArrow(direction) {
  if (!direction) return '→';
  const d = direction.toLowerCase();
  if (d === 'improving' || d === 'bullish' || d === 'up') return '↑';
  if (d === 'weakening' || d === 'bearish' || d === 'down') return '↓';
  return '→';
}
