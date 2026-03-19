import { changeColor } from '../utils/colors';
import { formatPercent } from '../utils/formatters';

const SECTOR_NAMES = {
  XLK: 'Technology',
  XLF: 'Financials',
  XLE: 'Energy',
  XLV: 'Health Care',
  XLI: 'Industrials',
  XLY: 'Cons. Disc.',
  XLP: 'Cons. Staples',
  XLU: 'Utilities',
  XLB: 'Materials',
  XLRE: 'Real Estate',
  XLC: 'Comm. Svcs',
};

export default function SectorHeatmap({ sectors }) {
  if (!sectors || typeof sectors !== 'object' || Object.keys(sectors).length === 0) {
    return (
      <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4">
        <h3 className="text-xs text-terminal-text-dim font-semibold tracking-wider mb-4">SECTOR PERFORMANCE</h3>
        <p className="text-xs text-terminal-text-dim">No sector data available</p>
      </div>
    );
  }

  const sorted = Object.entries(sectors)
    .map(([symbol, data]) => ({ symbol, name: data.name || SECTOR_NAMES[symbol] || symbol, ...data }))
    .sort((a, b) => (b.change_pct || 0) - (a.change_pct || 0));

  const maxAbs = Math.max(
    ...sorted.map((s) => Math.abs(s.change_pct || 0)),
    0.01
  );

  return (
    <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4">
      <h3 className="text-xs text-terminal-text-dim font-semibold tracking-wider mb-4">
        SECTOR PERFORMANCE
      </h3>

      <div className="space-y-1.5">
        {sorted.map((sector) => {
          const pct = sector.change_pct || 0;
          const barWidth = (Math.abs(pct) / maxAbs) * 100;
          const color = changeColor(pct);

          return (
            <div key={sector.symbol} className="flex items-center gap-2">
              <div className="w-28 shrink-0 flex items-baseline gap-1.5">
                <span className="text-xs font-semibold text-terminal-text">{sector.symbol}</span>
                <span className="text-[10px] text-terminal-text-dim truncate hidden sm:inline">
                  {sector.name}
                </span>
              </div>

              <div className="flex-1 h-4 bg-terminal-bg rounded-sm overflow-hidden">
                <div
                  className="h-full rounded-sm transition-all duration-500 ease-out"
                  style={{
                    width: `${Math.max(barWidth, 2)}%`,
                    backgroundColor: color,
                    opacity: 0.7,
                  }}
                />
              </div>

              <span className="text-xs font-semibold w-16 text-right shrink-0" style={{ color }}>
                {formatPercent(pct)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
