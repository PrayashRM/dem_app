import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { isAdmin } from '../utils/helpers';

const AdminRoute = () => {
  const { user, loading } = useAuth();

  if (loading) return <div className="page-container">Loading...</div>;

  return user && isAdmin(user) ? <Outlet /> : <Navigate to="/dashboard" replace />;
};

export default AdminRoute;
