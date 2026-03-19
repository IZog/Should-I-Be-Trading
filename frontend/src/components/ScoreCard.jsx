import DirectionArrow from './DirectionArrow';
import { scoreColor, COLORS } from '../utils/colors';

export default function ScoreCard({ category }) {
  if (!category) return null;

  const {
    name = 'UNKNOWN',
    score = 0,
    direction,
    interpretation = '',
    weight,
  } = category;

  const color = scoreColor(score);

  return (
    <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4 hover:bg-terminal-panel-hover transition-colors">
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-terminal-text-dim font-semibold tracking-wider uppercase">
          {name}
        </span>
        {weight != null && (
          <span className="text-[10px] text-terminal-text-dim bg-terminal-bg px-1.5 py-0.5 rounded">
            {Math.round(weight * 100)}%
          </span>
        )}
      </div>

      {/* Score + arrow */}
      <div className="flex items-end gap-2 mb-2">
        <span className="text-3xl font-bold leading-none" style={{ color }}>
          {Math.round(score)}
        </span>
        <span className="text-xs text-terminal-text-dim mb-1">/100</span>
        <div className="ml-auto mb-1">
          <DirectionArrow direction={direction} />
        </div>
      </div>

      {/* Score bar */}
      <div className="w-full h-1.5 bg-terminal-bg rounded-full mb-2 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${Math.min(score, 100)}%`, backgroundColor: color }}
        />
      </div>

      {/* Interpretation */}
      {interpretation && (
        <p className="text-[11px] text-terminal-text-dim leading-snug mt-1 line-clamp-2">
          {interpretation}
        </p>
      )}
    </div>
  );
}
