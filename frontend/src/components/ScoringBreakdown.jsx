import { scoreColor } from '../utils/colors';

const CATEGORY_ORDER = ['volatility', 'momentum', 'trend', 'breadth', 'macro'];

export default function ScoringBreakdown({ subscores, totalScore }) {
  if (!subscores || typeof subscores !== 'object' || Object.keys(subscores).length === 0) {
    return (
      <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4">
        <h3 className="text-xs text-terminal-text-dim font-semibold tracking-wider mb-4">SCORING BREAKDOWN</h3>
        <p className="text-xs text-terminal-text-dim">No scoring data available</p>
      </div>
    );
  }

  const items = CATEGORY_ORDER
    .filter((key) => subscores[key])
    .map((key) => ({ name: key, ...subscores[key] }));

  return (
    <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4">
      <h3 className="text-xs text-terminal-text-dim font-semibold tracking-wider mb-4">
        SCORING BREAKDOWN
      </h3>

      <div className="space-y-3">
        {items.map((cat) => {
          const score = cat.score || 0;
          const weight = cat.weight || 0;
          const contribution = cat.contribution || score * weight;
          const color = scoreColor(score);

          return (
            <div key={cat.name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-terminal-text font-semibold uppercase">
                  {cat.name}
                </span>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-terminal-text-dim">
                    w: {Math.round(weight * 100)}%
                  </span>
                  <span className="text-xs font-bold" style={{ color }}>
                    {Math.round(score)}
                  </span>
                </div>
              </div>

              <div className="w-full h-2 bg-terminal-bg rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: `${Math.min(score, 100)}%`,
                    backgroundColor: color,
                    opacity: 0.8,
                  }}
                />
              </div>

              <div className="text-right mt-0.5">
                <span className="text-[10px] text-terminal-text-dim">
                  +{contribution.toFixed(1)} pts
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-terminal-border flex items-center justify-between">
        <span className="text-xs text-terminal-text-dim font-semibold tracking-wider">TOTAL</span>
        <span
          className="text-lg font-bold"
          style={{ color: scoreColor(totalScore || 0) }}
        >
          {Math.round(totalScore || 0)}
        </span>
      </div>
    </div>
  );
}
