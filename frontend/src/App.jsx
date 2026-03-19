import { useState } from 'react';
import { useMarketData } from './hooks/useMarketData';
import TopBar from './components/TopBar';
import AlertBanner from './components/AlertBanner';
import HeroPanel from './components/HeroPanel';
import ModeToggle from './components/ModeToggle';
import CorePanelsGrid from './components/CorePanelsGrid';
import SectorHeatmap from './components/SectorHeatmap';
import ScoringBreakdown from './components/ScoringBreakdown';
import TerminalAnalysis from './components/TerminalAnalysis';

function SkeletonBlock({ className = '' }) {
  return (
    <div className={`bg-terminal-panel rounded-lg skeleton-pulse ${className}`} />
  );
}

function LoadingState() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <SkeletonBlock className="h-64" />
      <div className="flex justify-center">
        <SkeletonBlock className="h-10 w-48" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {[...Array(5)].map((_, i) => (
          <SkeletonBlock key={i} className="h-36" />
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SkeletonBlock className="h-80" />
        <SkeletonBlock className="h-80" />
      </div>
      <SkeletonBlock className="h-48" />
    </div>
  );
}

function ErrorState({ error, onRetry }) {
  return (
    <div className="max-w-6xl mx-auto px-4 py-20 text-center">
      <div className="bg-terminal-panel border border-terminal-border rounded-lg p-8 inline-block">
        <div className="text-terminal-red text-4xl mb-4">&#9888;</div>
        <h2 className="text-terminal-red text-lg font-bold mb-2">CONNECTION ERROR</h2>
        <p className="text-terminal-text-dim text-sm mb-6 max-w-md">
          Unable to reach the market data API. Make sure the backend is running on port 8000.
        </p>
        <p className="text-terminal-text-dim text-xs mb-6 font-mono">{error}</p>
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-terminal-blue text-white text-xs font-semibold tracking-wider rounded hover:opacity-80 transition-opacity cursor-pointer"
        >
          RETRY
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState('swing');
  const { data, loading, error, lastUpdated, isRefreshing, refresh } = useMarketData(mode);

  return (
    <div className="min-h-screen bg-terminal-bg font-mono flex flex-col">
      {/* Sticky top bar */}
      <TopBar
        data={data}
        lastUpdated={lastUpdated}
        isRefreshing={isRefreshing}
        onRefresh={refresh}
      />

      {/* Alert banner */}
      {data?.fomc && <AlertBanner fomc={data.fomc} />}

      {/* Main content */}
      <main className="flex-1">
        {loading && !data ? (
          <LoadingState />
        ) : error && !data ? (
          <ErrorState error={error} onRetry={refresh} />
        ) : data ? (
          <div className="max-w-6xl mx-auto px-4 py-6 space-y-2">
            {/* Hero */}
            <HeroPanel data={data} />

            {/* Mode toggle */}
            <ModeToggle mode={mode} onModeChange={setMode} />

            {/* Core scoring panels */}
            <CorePanelsGrid subscores={data.subscores} />

            {/* Two-column: Sectors + Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SectorHeatmap sectors={data.sectors} />
              <ScoringBreakdown
                subscores={data.subscores}
                totalScore={data.market_quality_score}
              />
            </div>

            {/* Terminal analysis */}
            <TerminalAnalysis summary={data.summary} />
          </div>
        ) : null}
      </main>

      {/* Footer */}
      <footer className="border-t border-terminal-border py-4 text-center">
        <span className="text-xs text-terminal-text-dim tracking-wider">
          Should I Be Trading? v1.0
        </span>
      </footer>
    </div>
  );
}
