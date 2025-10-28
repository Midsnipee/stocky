import { useEffect, useState } from 'react';

const STORAGE_KEY = 'stocky-theme';

function ThemeToggle() {
  const [theme, setTheme] = useState(() =>
    window.localStorage.getItem(STORAGE_KEY) || 'light'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    window.localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      Mode {theme === 'light' ? 'sombre' : 'clair'}
    </button>
  );
}

export default ThemeToggle;
