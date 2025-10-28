import { useMemo, useState } from 'react';
import { useData } from '../context/DataContext.jsx';
import FilterBar from '../components/filters/FilterBar.jsx';

function Assignments() {
  const { data, addAssignment, dayjs } = useData();
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('all');

  const assignments = useMemo(() => {
    return data.assignments
      .map((assignment) => {
        const serial = data.serials.find((entry) => entry.id === assignment.serialId);
        const user = data.users.find((entry) => entry.id === assignment.assigneeUserId);
        return { ...assignment, serial, user };
      })
      .filter((entry) => (department === 'all' ? true : entry.user?.department === department))
      .filter((entry) => {
        if (!search) return true;
        const haystack = `${entry.user?.displayName ?? ''} ${entry.serial?.serialNumber ?? ''}`.toLowerCase();
        return haystack.includes(search.toLowerCase());
      })
      .sort((a, b) => new Date(b.startDate) - new Date(a.startDate));
  }, [data.assignments, data.serials, data.users, department, search]);

  const handleCreate = () => {
    const firstSerial = data.serials.find((serial) => serial.status === 'En stock');
    const firstUser = data.users[0];
    if (!firstSerial || !firstUser) return;
    addAssignment({
      id: `assign-${Date.now()}`,
      serialId: firstSerial.id,
      assigneeUserId: firstUser.id,
      startDate: new Date().toISOString(),
      expectedReturnDate: dayjs().add(60, 'day').toISOString(),
      endDate: null,
      documentFile: null,
      notes: 'Attribution rapide'
    });
  };

  return (
    <div className="assignments">
      <div className="card">
        <div className="card-header">
          <h3>Attributions utilisateurs</h3>
          <button type="button" className="primary" onClick={handleCreate}>
            Nouvelle attribution
          </button>
        </div>
        <FilterBar
          filters={[
            {
              name: 'search',
              label: 'Recherche',
              type: 'search',
              value: search,
              placeholder: 'Utilisateur, matériel...'
            },
            {
              name: 'department',
              label: 'Service',
              type: 'select',
              value: department,
              options: [
                { value: 'all', label: 'Tous les services' },
                ...Array.from(new Set(data.users.map((user) => user.department))).map((dept) => ({
                  value: dept,
                  label: dept
                }))
              ]
            }
          ]}
          onChange={(name, value) => {
            if (name === 'search') setSearch(value);
            if (name === 'department') setDepartment(value);
          }}
        />
      </div>
      <div className="card">
        <div className="table-header" style={{ gridTemplateColumns: '1fr 1fr 1fr 1fr 0.8fr' }}>
          <span>Utilisateur</span>
          <span>Série</span>
          <span>Début</span>
          <span>Retour prévu</span>
          <span>Actions</span>
        </div>
        {assignments.map((assignment) => (
          <div
            key={assignment.id}
            className="table-row"
            style={{ gridTemplateColumns: '1fr 1fr 1fr 1fr 0.8fr' }}
          >
            <div>
              <strong>{assignment.user?.displayName}</strong>
              <p className="text-muted">{assignment.user?.department}</p>
            </div>
            <div>
              <strong>{assignment.serial?.serialNumber}</strong>
              <p className="text-muted">{assignment.serial?.itemId}</p>
            </div>
            <span>{dayjs(assignment.startDate).format('DD/MM/YYYY')}</span>
            <span>{dayjs(assignment.expectedReturnDate).format('DD/MM/YYYY')}</span>
            <div className="actions">
              <button type="button">Clôturer</button>
              <button type="button">Exporter PDF</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Assignments;
