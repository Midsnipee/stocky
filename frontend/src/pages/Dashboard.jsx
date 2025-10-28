import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import WidgetCard from '../components/widgets/WidgetCard.jsx';
import { useData } from '../context/DataContext.jsx';

const AVAILABLE_WIDGETS = [
  'stockByCategory',
  'pendingDeliveries',
  'warrantyAlerts',
  'recentAssignments',
  'stockValue',
  'alerts'
];

const WIDGET_LABELS = {
  stockByCategory: 'Stock par catégorie',
  pendingDeliveries: 'Livraisons en attente',
  warrantyAlerts: 'Garanties à surveiller',
  recentAssignments: 'Attributions récentes',
  stockValue: 'Valeur du stock',
  alerts: 'Alertes'
};

function Dashboard() {
  const { metrics, data, persistPreference, loadPreference, dayjs } = useData();
  const navigate = useNavigate();
  const savedWidgets = loadPreference('dashboard-widgets', AVAILABLE_WIDGETS);
  const [widgets, setWidgets] = useState(savedWidgets);

  const addWidget = (widget) => {
    if (!widget) return;
    const next = Array.from(new Set([...widgets, widget]));
    setWidgets(next);
    persistPreference('dashboard-widgets', next);
  };

  const removeWidget = (widget) => {
    const next = widgets.filter((name) => name !== widget);
    setWidgets(next);
    persistPreference('dashboard-widgets', next);
  };

  const availableToAdd = useMemo(
    () => AVAILABLE_WIDGETS.filter((widget) => !widgets.includes(widget)),
    [widgets]
  );

  const WidgetActions = ({ widget, onDetail }) => (
    <>
      <select onChange={(event) => navigate(event.target.value)} defaultValue="">
        <option value="" disabled>
          Filtres rapides
        </option>
        <option value="/dashboard">Toutes périodes</option>
        <option value="/orders?period=30">30 derniers jours</option>
        <option value="/items?category=all">Toutes catégories</option>
      </select>
      <button type="button" className="primary" onClick={onDetail}>
        Voir le détail
      </button>
      <button type="button" onClick={() => removeWidget(widget)}>
        Retirer
      </button>
    </>
  );

  const renderWidget = (widget) => {
    switch (widget) {
      case 'stockByCategory':
        return (
          <WidgetCard
            title="Stock par catégorie"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/items')} />}
          >
            <div className="widget-list">
              {Object.entries(metrics.stockByCategory).map(([category, count]) => (
                <div key={category} className="table-row" style={{ gridTemplateColumns: '1fr auto' }}>
                  <span>{category}</span>
                  <span className="tag">{count} en stock</span>
                </div>
              ))}
            </div>
          </WidgetCard>
        );
      case 'pendingDeliveries':
        return (
          <WidgetCard
            title="Livraisons en attente"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/orders?status=Commande%20fournisseur%20faite')} />}
          >
            <p>{metrics.pendingDeliveries.length} commande(s) en attente de livraison.</p>
            <ul className="widget-list">
              {metrics.pendingDeliveries.map((order) => (
                <li key={order.id}>
                  <span>{order.internalRef}</span>
                  <span className="order-state" data-status={order.status}>
                    {dayjs(order.expectedDeliveryAt).format('DD/MM/YYYY')}
                  </span>
                </li>
              ))}
            </ul>
          </WidgetCard>
        );
      case 'warrantyAlerts':
        return (
          <WidgetCard
            title="Garanties à surveiller"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/items')} />}
          >
            <ul className="widget-list">
              {metrics.warrantyAlerts.slice(0, 5).map((serial) => (
                <li key={serial.id}>
                  <div>
                    <strong>{serial.serialNumber}</strong>
                    <p className="text-muted">
                      Expire le {dayjs(serial.warrantyEnd).format('DD/MM/YYYY')}
                    </p>
                  </div>
                  <span className="badge warning">{serial.status}</span>
                </li>
              ))}
            </ul>
          </WidgetCard>
        );
      case 'recentAssignments':
        return (
          <WidgetCard
            title="Attributions récentes"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/assignments')} />}
          >
            <ol className="widget-list">
              {metrics.recentAssignments.map((assignment) => {
                const serial = data.serials.find((s) => s.id === assignment.serialId);
                const user = data.users.find((u) => u.id === assignment.assigneeUserId);
                return (
                  <li key={assignment.id}>
                    <div>
                      <strong>{serial?.serialNumber}</strong>
                      <p className="text-muted">
                        {user?.displayName} · {dayjs(assignment.startDate).format('DD/MM/YYYY')}
                      </p>
                    </div>
                    <button
                      type="button"
                      className="link"
                      onClick={() => navigate(`/items/${serial?.itemId}`)}
                    >
                      Voir la fiche
                    </button>
                  </li>
                );
              })}
            </ol>
          </WidgetCard>
        );
      case 'stockValue':
        return (
          <WidgetCard
            title="Valeur du stock"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/items')} />}
          >
            <div className="stat-value">
              <strong style={{ fontSize: '2rem' }}>
                {new Intl.NumberFormat('fr-FR', {
                  style: 'currency',
                  currency: 'EUR'
                }).format(metrics.stockValue)}
              </strong>
              <p className="text-muted">Somme des prix d'achat enregistrés</p>
            </div>
          </WidgetCard>
        );
      case 'alerts':
        return (
          <WidgetCard
            title="Alertes"
            actions={<WidgetActions widget={widget} onDetail={() => navigate('/dashboard')} />}
          >
            <ul className="widget-list">
              {data.alerts.map((alert) => (
                <li key={alert.id}>
                  <div>
                    <strong>{alert.type}</strong>
                    <p className="text-muted">{alert.message}</p>
                  </div>
                  <span className={`badge ${alert.severity}`}>{alert.severity}</span>
                </li>
              ))}
            </ul>
          </WidgetCard>
        );
      default:
        return null;
    }
  };

  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-header">
          <h3>Widgets</h3>
          <div className="widget-actions">
            <select
              onChange={(event) => {
                addWidget(event.target.value);
                event.target.value = '';
              }}
              defaultValue=""
            >
              <option value="" disabled>
                Ajouter un widget
              </option>
              {availableToAdd.map((widget) => (
                <option key={widget} value={widget}>
                  {WIDGET_LABELS[widget]}
                </option>
              ))}
            </select>
          </div>
        </div>
        <p className="text-muted">
          Ajoutez, retirez et réorganisez les widgets pour suivre les indicateurs clés.
        </p>
      </div>
      <div className="widget-grid">
        {widgets.map((widget) => (
          <div key={widget}>{renderWidget(widget)}</div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
