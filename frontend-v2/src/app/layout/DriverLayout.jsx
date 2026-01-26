import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './DriverLayout.css';

function DriverLayout({ children, driverProfile }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const isActive = (path) => location.pathname === path ? 'active' : '';

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    navigate('/login');
  };

  if (!driverProfile || driverProfile.approval_status !== 'APPROVED') {
    return null;
  }

  return (
    <div className="driver-layout">
      {/* Sidebar Navigation */}
      <aside className={`driver-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>Driver Portal</h2>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            title="Toggle sidebar"
          >
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <Link 
            to="/app/driver/dashboard" 
            className={`nav-link ${isActive('/app/driver/dashboard')}`}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Dashboard</span>
          </Link>

          <Link 
            to="/app/driver/dispatches" 
            className={`nav-link ${isActive('/app/driver/dispatches')}`}
          >
            <span className="nav-icon">📋</span>
            <span className="nav-label">Dispatches</span>
          </Link>

          <Link 
            to="/app/driver/vehicles" 
            className={`nav-link ${isActive('/app/driver/vehicles')}`}
          >
            <span className="nav-icon">🚗</span>
            <span className="nav-label">Vehicles</span>
          </Link>

          <Link 
            to="/app/driver/availability" 
            className={`nav-link ${isActive('/app/driver/availability')}`}
          >
            <span className="nav-icon">📅</span>
            <span className="nav-label">Availability</span>
          </Link>

          <Link 
            to="/app/driver/fleets" 
            className={`nav-link ${isActive('/app/driver/fleets')}`}
          >
            <span className="nav-icon">🏢</span>
            <span className="nav-label">Fleets</span>
          </Link>

          <Link 
            to="/app/profile" 
            className={`nav-link ${isActive('/app/profile')}`}
          >
            <span className="nav-icon">👤</span>
            <span className="nav-label">Profile</span>
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="driver-main">
        {children}
      </main>
    </div>
  );
}

export default DriverLayout;
