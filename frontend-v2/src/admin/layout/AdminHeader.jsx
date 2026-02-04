import React from 'react';
import './AdminHeader.css';

const AdminHeader = ({ adminData }) => {
  return (
    <div className="admin-header">
      <div className="admin-header-content">
        {/* Logo Section with SVG */}
        <div className="admin-logo-section">
          <svg 
            className="admin-logo-icon" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <h1 className="admin-header-title">Admin Panel</h1>
        </div>

        {/* User Section with SVG Avatar */}
        <div className="admin-header-user">
          <div className="admin-user-info">
            <span className="admin-user-name">{adminData.full_name}</span>
            <span className="admin-user-email">{adminData.email}</span>
          </div>
          <div className="admin-user-avatar">
            <svg 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminHeader;