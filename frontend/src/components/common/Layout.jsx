import { NavLink } from 'react-router-dom';
import ThemeToggle from './ThemeToggle.jsx';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/orders', label: 'Commandes' },
  { to: '/items', label: 'Matériels' },
  { to: '/assignments', label: 'Attributions' }
];

function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Stocky</h1>
          <p className="sidebar-subtitle">Gestion des stocks & commandes</p>
        </div>
        <nav className="sidebar-nav">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <ThemeToggle />
      </aside>
      <main className="content">
        <header className="content-header">
          <h2>Portail de gestion</h2>
          <p>Suivi complet du cycle de vie des équipements</p>
        </header>
        <section className="content-body">{children}</section>
      </main>
    </div>
  );
}

export default Layout;
