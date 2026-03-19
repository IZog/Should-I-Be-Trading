export default function TerminalAnalysis({ summary }) {
  if (!summary) return null;

  return (
    <div className="bg-terminal-panel border border-terminal-border rounded-lg p-4 my-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs text-terminal-green font-semibold tracking-wider">$</span>
        <span className="text-xs text-terminal-text-dim font-semibold tracking-wider">
          TERMINAL ANALYSIS
        </span>
        <div className="flex-1 border-t border-terminal-border ml-2" />
      </div>

      {/* Terminal-style text block */}
      <div className="bg-terminal-bg rounded p-4 font-mono">
        <pre className="text-sm text-terminal-text leading-relaxed whitespace-pre-wrap break-words">
          {summary}
          <span className="cursor-blink text-terminal-green ml-0.5">_</span>
        </pre>
      </div>
    </div>
  );
}
