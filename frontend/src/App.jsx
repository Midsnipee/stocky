import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Orders from './pages/Orders.jsx';
import Items from './pages/Items.jsx';
import ItemDetail from './pages/ItemDetail.jsx';
import Assignments from './pages/Assignments.jsx';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/items" element={<Items />} />
        <Route path="/items/:itemId" element={<ItemDetail />} />
        <Route path="/assignments" element={<Assignments />} />
      </Routes>
    </Layout>
  );
}

export default App;
