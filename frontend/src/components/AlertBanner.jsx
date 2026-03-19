export default function AlertBanner({ fomc }) {
  if (!fomc || !fomc.is_within_warning) return null;

  const daysText = fomc.days_until != null
    ? `IN ${fomc.days_until} DAY${fomc.days_until !== 1 ? 'S' : ''}`
    : 'SOON';

  return (
    <div className="w-full px-4 py-2 flex items-center justify-center gap-2"
      style={{
        background: 'linear-gradient(90deg, rgba(255,170,0,0.15) 0%, rgba(255,170,0,0.25) 50%, rgba(255,170,0,0.15) 100%)',
        borderBottom: '1px solid rgba(255,170,0,0.3)',
      }}
    >
      <span className="text-terminal-amber text-sm">&#9888;</span>
      <span className="text-terminal-amber text-xs font-semibold tracking-wider">
        FOMC MEETING {daysText} — Expect elevated volatility
      </span>
    </div>
  );
}
