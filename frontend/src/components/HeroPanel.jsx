import CircularGauge from './CircularGauge';
import { decisionColor, decisionGlow } from '../utils/colors';

export default function HeroPanel({ data }) {
  const decision = data?.decision || 'NO';
  const detail = data?.decision_detail || '';
  const marketScore = data?.market_quality_score ?? 0;
  const execScore = data?.execution_window_score ?? 0;
  const color = decisionColor(decision);
  const glow = decisionGlow(decision);

  return (
    <div className="bg-terminal-panel border border-terminal-border rounded-lg p-8 text-center">
      {/* Decision badge */}
      <div className="mb-2">
        <span className="text-xs text-terminal-text-dim tracking-widest uppercase">Should you be trading?</span>
      </div>
      <div className="mb-6">
        <span
          className={`text-6xl sm:text-7xl md:text-8xl font-extrabold tracking-tight ${glow}`}
          style={{ color }}
        >
          {decision}
        </span>
      </div>

      {/* Gauges row */}
      <div className="flex items-center justify-center gap-8 sm:gap-16 mb-6 flex-wrap">
        <CircularGauge score={marketScore} size={180} label="MARKET QUALITY" />
        <CircularGauge score={execScore} size={130} label="EXEC WINDOW" />
      </div>

      {/* Detail text */}
      {detail && (
        <p className="text-terminal-text-dim text-sm max-w-2xl mx-auto leading-relaxed">
          {detail}
        </p>
      )}
    </div>
  );
}
