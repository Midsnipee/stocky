import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext.jsx';
import FilterBar from '../components/filters/FilterBar.jsx';

function Items() {
  const { data } = useData();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [site, setSite] = useState('all');

  const filteredItems = useMemo(() => {
    return data.items
      .filter((item) => (category === 'all' ? true : item.category === category))
      .filter((item) => (site === 'all' ? true : item.site === site))
      .filter((item) => {
        if (!search) return true;
        const haystack = `${item.name} ${item.internalRef}`.toLowerCase();
        return haystack.includes(search.toLowerCase());
      })
      .map((item) => {
        const serials = data.serials.filter((serial) => serial.itemId === item.id);
        const inStock = serials.filter((serial) => serial.status === 'En stock').length;
        const assigned = serials.filter((serial) => serial.status === 'Attribué').length;
        return { ...item, serials, inStock, assigned };
      });
  }, [data.items, data.serials, category, site, search]);

  return (
    <div className="items">
      <div className="card">
        <div className="card-header">
          <h3>Catalogue matériels</h3>
          <div className="actions">
            <button type="button" className="primary">
              Nouveau matériel
            </button>
            <button type="button">Importer</button>
            <button type="button">Exporter</button>
          </div>
        </div>
        <FilterBar
          filters={[
            {
              name: 'search',
              label: 'Recherche',
              type: 'search',
              value: search,
              placeholder: 'Rechercher un matériel...'
            },
            {
              name: 'category',
              label: 'Catégorie',
              type: 'select',
              value: category,
              options: [
                { value: 'all', label: 'Toutes les catégories' },
                ...Array.from(new Set(data.items.map((item) => item.category))).map((cat) => ({
                  value: cat,
                  label: cat
                }))
              ]
            },
            {
              name: 'site',
              label: 'Site',
              type: 'select',
              value: site,
              options: [
                { value: 'all', label: 'Tous les sites' },
                ...Array.from(new Set(data.items.map((item) => item.site))).map((location) => ({
                  value: location,
                  label: location
                }))
              ]
            }
          ]}
          onChange={(name, value) => {
            if (name === 'search') setSearch(value);
            if (name === 'category') setCategory(value);
            if (name === 'site') setSite(value);
          }}
        />
      </div>
      <div className="card">
        <div className="table-header" style={{ gridTemplateColumns: '1.2fr 1fr 0.8fr 0.8fr 1fr 1fr' }}>
          <span>Nom</span>
          <span>Référence</span>
          <span>En stock</span>
          <span>Attribués</span>
          <span>Fournisseur</span>
          <span>Actions</span>
        </div>
        {filteredItems.map((item) => {
          const supplier = data.suppliers.find((entry) => entry.id === item.defaultSupplierId);
          return (
            <div
              key={item.id}
              className="table-row"
              style={{ gridTemplateColumns: '1.2fr 1fr 0.8fr 0.8fr 1fr 1fr' }}
            >
              <div>
                <strong>{item.name}</strong>
                <div className="text-muted">{item.category}</div>
              </div>
              <span>{item.internalRef}</span>
              <span>{item.inStock}</span>
              <span>{item.assigned}</span>
              <span>{supplier?.name || '—'}</span>
              <div className="actions">
                <button type="button" onClick={() => navigate(`/items/${item.id}`)}>
                  Détails
                </button>
                <button type="button">Imprimer</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Items;
