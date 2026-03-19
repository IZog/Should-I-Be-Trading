import { useCountdown } from '../hooks/useCountdown';
import { formatPrice, formatPercent } from '../utils/formatters';
import { changeColor, COLORS } from '../utils/colors';

const TICKER_DISPLAY = [
  { key: 'SPY', label: 'SPY' },
  { key: 'QQQ', label: 'QQQ' },
  { key: '^VIX', label: 'VIX' },
  { key: 'DX-Y.NYB', label: 'DXY' },
  { key: '^TNX', label: 'TNX' },
];

export default function TopBar({ data, lastUpdated, isRefreshing, onRefresh }) {
  const updatedAgo = useCountdown(lastUpdated);
  const tickers = data?.tickers || {};

  const tickerItems = TICKER_DISPLAY.map((t) => {
    const td = tickers[t.key] || {};
    return (
      <span key={t.key} className="inline-flex items-center gap-2 px-4 whitespace-nowrap">
        <span className="text-terminal-text-dim text-xs font-semibold">{t.label}</span>
        <span className="text-terminal-text text-xs">{formatPrice(td.price)}</span>
        <span className="text-xs font-semibold" style={{ color: changeColor(td.change_pct) }}>
          {formatPercent(td.change_pct || 0)}
        </span>
      </span>
    );
  });

  // Also add top sector ETFs to the ticker tape
  const sectorKeys = ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE', 'XLC'];
  const sectors = data?.sectors || {};
  const sectorItems = sectorKeys.map((key) => {
    const s = sectors[key] || {};
    return (
      <span key={key} className="inline-flex items-center gap-2 px-4 whitespace-nowrap">
        <span className="text-terminal-text-dim text-xs font-semibold">{key}</span>
        <span className="text-terminal-text text-xs">{formatPrice(s.price)}</span>
        <span className="text-xs font-semibold" style={{ color: changeColor(s.change_pct) }}>
          {formatPercent(s.change_pct || 0)}
        </span>
      </span>
    );
  });

  const allItems = [...tickerItems, ...sectorItems];

  return (
    <div className="sticky top-0 z-50 border-b border-terminal-border" style={{ backgroundColor: '#070a1f' }}>
      <div className="flex items-center h-10">
        {/* Scrolling ticker tape */}
        <div className="flex-1 overflow-hidden relative">
          <div className="ticker-scroll inline-flex">
            {allItems}
            {allItems}
          </div>
        </div>

        {/* Right side: status + refresh */}
        <div className="flex items-center gap-3 px-4 border-l border-terminal-border h-full shrink-0">
          <div className="flex items-center gap-1.5">
            <div
              className="w-2 h-2 rounded-full pulse-green"
              style={{ backgroundColor: isRefreshing ? COLORS.amber : COLORS.green }}
            />
            <span className="text-xs text-terminal-text-dim">
              {isRefreshing ? 'UPDATING' : 'LIVE'}
            </span>
          </div>
          <span className="text-xs text-terminal-text-dim hidden sm:inline">
            {updatedAgo}
          </span>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="text-terminal-text-dim hover:text-terminal-cyan transition-colors text-sm disabled:opacity-30 cursor-pointer"
            title="Refresh data"
          >
            ↻
          </button>
        </div>
      </div>
    </div>
  );
}
