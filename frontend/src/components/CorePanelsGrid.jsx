import ScoreCard from './ScoreCard';

const CATEGORY_ORDER = ['volatility', 'momentum', 'trend', 'breadth', 'macro'];

export default function CorePanelsGrid({ subscores }) {
  if (!subscores || typeof subscores !== 'object') return null;

  const items = CATEGORY_ORDER
    .filter((key) => subscores[key])
    .map((key) => ({ name: key, ...subscores[key] }));

  if (items.length === 0) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 my-6">
      {items.map((cat) => (
        <ScoreCard key={cat.name} category={cat} />
      ))}
    </div>
  );
}
