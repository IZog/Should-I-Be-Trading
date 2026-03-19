export const COLORS = {
  bg: '#0a0e27',
  panel: '#111638',
  panelHover: '#161b45',
  border: '#1a2050',
  green: '#00ff88',
  red: '#ff4444',
  amber: '#ffaa00',
  blue: '#4488ff',
  cyan: '#00d4ff',
  text: '#e0e0e0',
  textDim: '#888888',
};

export function scoreColor(score) {
  if (score >= 80) return COLORS.green;
  if (score >= 60) return COLORS.amber;
  return COLORS.red;
}

export function changeColor(value) {
  if (value > 0) return COLORS.green;
  if (value < 0) return COLORS.red;
  return COLORS.textDim;
}

export function decisionColor(decision) {
  if (decision === 'YES') return COLORS.green;
  if (decision === 'CAUTION') return COLORS.amber;
  return COLORS.red;
}

export function decisionGlow(decision) {
  if (decision === 'YES') return 'glow-green';
  if (decision === 'CAUTION') return 'glow-amber';
  return 'glow-red';
}
