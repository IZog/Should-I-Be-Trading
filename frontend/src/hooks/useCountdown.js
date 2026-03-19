import { useState, useEffect } from 'react';
import { timeAgo } from '../utils/formatters';

export function useCountdown(timestamp) {
  const [display, setDisplay] = useState('--');

  useEffect(() => {
    if (!timestamp) return;
    const update = () => setDisplay(timeAgo(timestamp));
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, [timestamp]);

  return display;
}
