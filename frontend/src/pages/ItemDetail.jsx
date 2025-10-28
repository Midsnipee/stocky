import { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useData } from '../context/DataContext.jsx';

function ItemDetail() {
  const { itemId } = useParams();
  const { data, dayjs } = useData();
  const item = data.items.find((entry) => entry.id === itemId);

  const serials = useMemo(
    () => data.serials.filter((serial) => serial.itemId === itemId),
    [data.serials, itemId]
  );

  const timeline = useMemo(() => {
    const logs = data.activity.filter(
      (event) => event.entityType === 'item' && event.entityId === itemId
    );
    const assignmentHistory = data.assignments
      .filter((assignment) => serials.some((serial) => serial.id === assignment.serialId))
      .map((assignment) => ({
        id: `assign-${assignment.id}`,
        title: 'Attribution',
        description: `Attribué à ${data.users.find((user) => user.id === assignment.assigneeUserId)?.displayName}`,
        date: assignment.startDate
      }));
    return [...logs.map((log) => ({
      id: log.id,
      title: log.action,
      description: `Par ${data.users.find((user) => user.id === log.actorUserId)?.displayName ?? 'Système'}`,
      date: log.at
    })), ...assignmentHistory].sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [data.activity, data.assignments, data.users, itemId, serials]);

  if (!item) {
    return (
      <div className="card">
        <h3>Matériel introuvable</h3>
        <p>Le matériel demandé n'existe pas dans la base de démonstration.</p>
      </div>
    );
  }

  const supplier = data.suppliers.find((entry) => entry.id === item.defaultSupplierId);
  const inStock = serials.filter((serial) => serial.status === 'En stock');
  const assigned = serials.filter((serial) => serial.status === 'Attribué');

  return (
    <div className="item-detail">
      <div className="card">
        <div className="card-header">
          <h3>{item.name}</h3>
          <div className="tags">
            <span className="tag">{item.category}</span>
            <span className="tag">Site {item.site}</span>
          </div>
        </div>
        <div className="grid-two-columns">
          <div>
            <h4>Informations</h4>
            <p>Référence interne : {item.internalRef}</p>
            <p>Fournisseur par défaut : {supplier?.name || '—'}</p>
            <p>Prix d'achat par défaut : {item.defaultUnitPrice} €</p>
            <p>Seuil d'alerte : {item.lowStockThreshold}</p>
            <p>Notes : {item.notes}</p>
          </div>
          <div>
            <h4>Stock</h4>
            <p>Unités en stock : {inStock.length}</p>
            <p>Unités attribuées : {assigned.length}</p>
            <p>Total séries : {serials.length}</p>
            <button type="button" className="primary">Générer code-barres</button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Numéros de série</h3>
          <div className="actions">
            <button type="button">Créer série</button>
            <button type="button">Import CSV</button>
          </div>
        </div>
        <div className="table-header" style={{ gridTemplateColumns: '1.2fr repeat(4, 1fr)' }}>
          <span>Numéro</span>
          <span>Livraison</span>
          <span>Garantie</span>
          <span>Statut</span>
          <span>Assigné à</span>
        </div>
        {serials.map((serial) => {
          const assignee = data.users.find((user) => user.id === serial.currentAssigneeUserId);
          return (
            <div
              key={serial.id}
              className="table-row"
              style={{ gridTemplateColumns: '1.2fr repeat(4, 1fr)' }}
            >
              <span>{serial.serialNumber}</span>
              <span>{dayjs(serial.deliveryDate).format('DD/MM/YYYY')}</span>
              <span>
                {serial.warrantyEnd
                  ? dayjs(serial.warrantyEnd).format('DD/MM/YYYY')
                  : '—'}
              </span>
              <span className="badge warning">{serial.status}</span>
              <span>{assignee?.displayName || '—'}</span>
            </div>
          );
        })}
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Timeline</h3>
        </div>
        <div className="timeline">
          {timeline.map((event) => (
            <div key={event.id} className="timeline-entry">
              <h4>{event.title}</h4>
              <p className="text-muted">{event.description}</p>
              <small>{dayjs(event.date).format('DD/MM/YYYY')}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ItemDetail;
