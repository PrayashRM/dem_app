import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LogOut, User, Box } from 'lucide-react';
import { isAdmin } from '../utils/helpers';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="navbar glass-panel">
      <div className="navbar-brand">
        <Link to="/dashboard" className="navbar-logo">
          <Box size={24} />
          <span>BasicApp</span>
        </Link>
      </div>
      <div className="navbar-links">
        <Link to="/products" className="navbar-link">Products</Link>
        <div className="navbar-user">
          <User size={18} />
          <span>{user.full_name}</span>
        </div>
        <button onClick={handleLogout} className="btn-secondary btn-sm">
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
