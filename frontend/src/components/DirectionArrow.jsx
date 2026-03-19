import { COLORS } from '../utils/colors';

export default function DirectionArrow({ direction }) {
  const d = (direction || '').toLowerCase();
  let arrow, color;

  if (d === 'improving' || d === 'bullish' || d === 'up') {
    arrow = '▲'; color = COLORS.green;
  } else if (d === 'weakening' || d === 'bearish' || d === 'down') {
    arrow = '▼'; color = COLORS.red;
  } else {
    arrow = '▶'; color = COLORS.amber;
  }

  return <span style={{ color }} className="text-sm font-bold">{arrow}</span>;
}
