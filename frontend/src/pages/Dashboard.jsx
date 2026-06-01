import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { User, Mail, Calendar, Shield, Package } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="page-wrapper">
      <Navbar />
      <div className="page-container animate-fade-in">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Welcome back, {user.full_name.split(' ')[0]}!</p>
        </div>

        <div className="dashboard-grid">
          <div className="profile-card glass-panel">
            <h2>Profile Information</h2>
            
            <div className="profile-info-list">
              <div className="profile-info-item">
                <div className="info-icon"><User size={20} /></div>
                <div className="info-content">
                  <span className="info-label">Full Name</span>
                  <span className="info-value">{user.full_name}</span>
                </div>
              </div>
              
              <div className="profile-info-item">
                <div className="info-icon"><Mail size={20} /></div>
                <div className="info-content">
                  <span className="info-label">Email Address</span>
                  <span className="info-value">{user.email}</span>
                </div>
              </div>

              <div className="profile-info-item">
                <div className="info-icon"><Shield size={20} /></div>
                <div className="info-content">
                  <span className="info-label">Account Role</span>
                  <span className="info-value role-badge">{user.role}</span>
                </div>
              </div>

              <div className="profile-info-item">
                <div className="info-icon"><Calendar size={20} /></div>
                <div className="info-content">
                  <span className="info-label">Member Since</span>
                  <span className="info-value">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric'
                    })}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="activity-card glass-panel">
            <h2>Quick Actions</h2>
            <div className="empty-state" style={{ flexDirection: 'column', gap: '16px' }}>
              <Package size={48} color="var(--accent-primary)" />
              <p>Explore the product catalog or manage inventory.</p>
              <Link to="/products" className="btn-primary">
                Browse Products
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
