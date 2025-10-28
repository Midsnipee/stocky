import { useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useData } from '../context/DataContext.jsx';
import FilterBar from '../components/filters/FilterBar.jsx';

const ORDER_STATES = [
  'Demandé',
  'Commande dans le circuit interne',
  'Commande fournisseur faite',
  'Livré'
];

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function Orders() {
  const { data, updateOrderStatus, dayjs } = useData();
  const query = useQuery();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState(query.get('status') || 'all');
  const [supplier, setSupplier] = useState('all');

  const filteredOrders = useMemo(() => {
    return data.orders
      .filter((order) => (status === 'all' ? true : order.status === status))
      .filter((order) => (supplier === 'all' ? true : order.supplierId === supplier))
      .filter((order) => {
        if (!search) return true;
        const haystack = `${order.internalRef} ${order.status}`.toLowerCase();
        return haystack.includes(search.toLowerCase());
      });
  }, [data.orders, search, status, supplier]);

  return (
    <div className="orders">
      <div className="card">
        <div className="card-header">
          <h3>Commandes & devis</h3>
          <button type="button" className="primary">
            Nouveau devis
          </button>
        </div>
        <p className="text-muted">
          Gérez le cycle complet des commandes : devis, réception, livraisons partielles et factures.
        </p>
        <FilterBar
          filters={[
            {
              name: 'search',
              label: 'Recherche',
              type: 'search',
              value: search,
              placeholder: 'Rechercher une commande...',
              onChange: setSearch
            },
            {
              name: 'status',
              label: 'Statut',
              type: 'select',
              value: status,
              options: [
                { value: 'all', label: 'Tous les statuts' },
                ...ORDER_STATES.map((state) => ({ value: state, label: state }))
              ],
              onChange: setStatus
            },
            {
              name: 'supplier',
              label: 'Fournisseur',
              type: 'select',
              value: supplier,
              options: [
                { value: 'all', label: 'Tous les fournisseurs' },
                ...data.suppliers.map((supplierItem) => ({
                  value: supplierItem.id,
                  label: supplierItem.name
                }))
              ],
              onChange: setSupplier
            }
          ]}
          onChange={(name, value) => {
            switch (name) {
              case 'search':
                setSearch(value);
                break;
              case 'status':
                setStatus(value);
                break;
              case 'supplier':
                setSupplier(value);
                break;
              default:
                break;
            }
          }}
        />
      </div>
      <div className="card">
        <div className="table-header">
          <span>Référence</span>
          <span>Fournisseur</span>
          <span>Statut</span>
          <span>Montant</span>
          <span>Échéance</span>
          <span>Actions</span>
        </div>
        {filteredOrders.map((order) => {
          const supplierEntry = data.suppliers.find((entry) => entry.id === order.supplierId);
          const total = order.lines.reduce(
            (acc, line) => acc + line.qty * line.unitPrice * (1 + line.taxRate),
            0
          );
          return (
            <div className="table-row" key={order.id}>
              <span>{order.internalRef}</span>
              <span>{supplierEntry?.name}</span>
              <span className="order-state" data-status={order.status}>
                {order.status}
              </span>
              <span>
                {new Intl.NumberFormat('fr-FR', {
                  style: 'currency',
                  currency: 'EUR'
                }).format(total)}
              </span>
              <span>{dayjs(order.expectedDeliveryAt).format('DD/MM/YYYY')}</span>
              <div className="actions">
                <select
                  className="status-select"
                  value={order.status}
                  onChange={(event) => updateOrderStatus(order.id, event.target.value)}
                >
                  {ORDER_STATES.map((state) => (
                    <option key={state} value={state}>
                      {state}
                    </option>
                  ))}
                </select>
                <button type="button">Partager</button>
                <button type="button">Exporter</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Orders;
