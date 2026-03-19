import { COLORS } from '../utils/colors';

export default function ModeToggle({ mode, onModeChange }) {
  const modes = [
    { key: 'swing', label: 'SWING' },
    { key: 'day', label: 'DAY' },
  ];

  return (
    <div className="flex items-center justify-center gap-1 my-6">
      <span className="text-xs text-terminal-text-dim mr-3 tracking-wider">MODE</span>
      <div className="flex rounded-md overflow-hidden border border-terminal-border">
        {modes.map(m => (
          <button
            key={m.key}
            onClick={() => onModeChange(m.key)}
            className="px-5 py-1.5 text-xs font-semibold tracking-wider transition-all cursor-pointer"
            style={{
              backgroundColor: mode === m.key ? COLORS.blue : 'transparent',
              color: mode === m.key ? '#ffffff' : COLORS.textDim,
            }}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
}
