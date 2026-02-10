import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import Icons from '../../components/Icons';
import './FleetDrivers.css';

function FleetDrivers() {
  const navigate = useNavigate();
  
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Drivers and invites
  const [drivers, setDrivers] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  
  // Search state
  const [searchPhone, setSearchPhone] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  
  // Invite state
  const [inviting, setInviting] = useState(false);

  // Load drivers and pending invites
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      const [driversRes, invitesRes] = await Promise.all([
        fleetService.listDrivers(),
        fleetService.listPendingInvites()
      ]);
      
      setDrivers(driversRes.drivers || []);
      setPendingInvites(invitesRes.invites || []);
    } catch (err) {
      console.error('Load data error:', err);
      if (err.response?.status === 404 || err.response?.status === 403) {
        navigate('/rider-dashboard');
        return;
      }
      setError(err.response?.data?.detail || 'Failed to load drivers');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Search for driver by phone
  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchPhone.trim()) {
      setSearchError('Please enter a phone number');
      return;
    }
    
    try {
      setSearching(true);
      setSearchError('');
      setSearchResult(null);
      
      const result = await fleetService.searchDriverByPhone(searchPhone.trim());
      setSearchResult(result);
    } catch (err) {
      console.error('Search error:', err);
      setSearchError(err.response?.data?.detail || 'Driver not found');
    } finally {
      setSearching(false);
    }
  };

  // Invite driver
  const handleInvite = async () => {
    if (!searchResult) return;
    
    try {
      setInviting(true);
      setError('');
      
      await fleetService.inviteDriver(searchResult.driver_id);
      
      setSuccess(`Invitation sent to ${searchResult.full_name}`);
      setSearchResult(null);
      setSearchPhone('');
      
      // Reload to get updated invites
      await loadData();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Invite error:', err);
      setError(err.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  // Remove driver from fleet
  const handleRemoveDriver = async (driverId, driverName) => {
    if (!window.confirm(`Are you sure you want to remove ${driverName} from the fleet?`)) {
      return;
    }
    
    try {
      setError('');
      await fleetService.removeDriver(driverId);
      setSuccess(`${driverName} has been removed from the fleet`);
      await loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Remove error:', err);
      setError(err.response?.data?.detail || 'Failed to remove driver');
    }
  };

  // Get status badge
  const getStatusBadge = (status) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-warning">Pending</span>;
      case 'ACCEPTED':
        return <span className="badge badge-success">Accepted</span>;
      case 'REJECTED':
        return <span className="badge badge-danger">Rejected</span>;
      case 'CANCELLED':
        return <span className="badge badge-default">Cancelled</span>;
      default:
        return <span className="badge badge-default">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="fleet-drivers">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading drivers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fleet-drivers">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          ← Back
        </button>
        <h1>Fleet Drivers</h1>
        <div style={{ width: '60px' }}></div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Search Driver Section */}
      <div className="search-section">
        <h2>Invite Driver</h2>
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="tel"
              placeholder="Enter driver's phone number"
              value={searchPhone}
              onChange={(e) => setSearchPhone(e.target.value)}
              disabled={searching}
            />
            <button type="submit" className="btn-search" disabled={searching}>
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
          {searchError && <p className="search-error">{searchError}</p>}
        </form>

        {/* Search Result */}
        {searchResult && (
          <div className="search-result">
            <div className="driver-found">
              <div className="driver-avatar">
                {searchResult.full_name?.charAt(0)?.toUpperCase() || 'D'}
              </div>
              <div className="driver-info">
                <h3>{searchResult.full_name}</h3>
                <p>{searchResult.phone}</p>
                <p className="categories">
                  Categories: {searchResult.allowed_vehicle_categories?.join(', ') || 'N/A'}
                </p>
              </div>
              <button 
                className="btn-invite" 
                onClick={handleInvite}
                disabled={inviting}
              >
                {inviting ? 'Sending...' : 'Send Invite'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Pending Invites */}
      {pendingInvites.length > 0 && (
        <div className="section">
          <h2>Pending Invites ({pendingInvites.filter(i => i.status === 'PENDING').length})</h2>
          <div className="invites-list">
            {pendingInvites.map((invite) => (
              <div key={invite.invite_id} className="invite-card">
                <div className="invite-info">
                  <span className="invite-name">{invite.driver_name}</span>
                  <span className="invite-phone">{invite.driver_phone}</span>
                </div>
                <div className="invite-meta">
                  {getStatusBadge(invite.status)}
                  <span className="invite-date">
                    {new Date(invite.invited_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Fleet Drivers */}
      <div className="section">
        <h2>Active Drivers ({drivers.length})</h2>
        {drivers.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon"><Icons.Users size={48} /></span>
            <p>No drivers in your fleet yet</p>
            <p className="hint">Search for drivers by phone number and send invites</p>
          </div>
        ) : (
          <div className="drivers-list">
            {drivers.map((driver) => (
              <div key={driver.driver_id} className="driver-card">
                <div className="driver-avatar">
                  {driver.full_name?.charAt(0)?.toUpperCase() || 'D'}
                </div>
                <div className="driver-info">
                  <h3>{driver.full_name}</h3>
                  <p>{driver.phone}</p>
                  <p className="joined-date">
                    Joined: {driver.start_date ? new Date(driver.start_date).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
                <button 
                  className="btn-remove"
                  onClick={() => handleRemoveDriver(driver.driver_id, driver.full_name)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default FleetDrivers;
