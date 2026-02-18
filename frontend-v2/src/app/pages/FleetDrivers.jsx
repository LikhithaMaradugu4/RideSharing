import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import Icons from '../../components/Icons'; // Ensure this path is correct for your project
import './FleetDrivers.css';

function FleetDrivers() {
  const navigate = useNavigate();
  
  // State Management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [drivers, setDrivers] = useState([]);
  const [pendingInvites, setPendingInvites] = useState([]);
  
  // Search State
  const [searchPhone, setSearchPhone] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [searching, setSearching] = useState(false);
  const [inviting, setInviting] = useState(false);

  // Assignment Modal State
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [dates, setDates] = useState({ start: '', end: '' });
  const [assigning, setAssigning] = useState(false);

  // --- Data Loading ---
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
      console.error('Load error:', err);
      // Optional: Redirect if unauthorized
      // if (err.response?.status === 403) navigate('/rider-dashboard');
      setError(err.response?.data?.detail || 'Failed to load fleet data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // --- Handlers ---

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchPhone.trim()) return;
    
    setSearching(true);
    setSearchResult(null);
    try {
      const result = await fleetService.searchDriverByPhone(searchPhone.trim());
      setSearchResult(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Driver not found');
      setTimeout(() => setError(''), 3000);
    } finally {
      setSearching(false);
    }
  };

  const handleInvite = async () => {
    if (!searchResult) return;
    setInviting(true);
    try {
      await fleetService.inviteDriver(searchResult.driver_id);
      setSuccess(`Invitation sent to ${searchResult.full_name}`);
      setSearchResult(null);
      setSearchPhone('');
      await loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invite failed');
    } finally {
      setInviting(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedDriver || !dates.start || !dates.end) return;
    setAssigning(true);
    try {
      await fleetService.assignDriverByDuration(selectedDriver.driver_id, dates.start, dates.end);
      setSuccess('Driver assigned successfully');
      setShowAssignModal(false);
      await loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Assignment failed');
    } finally {
      setAssigning(false);
    }
  };

  const handleRemove = async (driverId, name) => {
    if (!window.confirm(`Remove ${name} from fleet?`)) return;
    try {
      await fleetService.removeDriver(driverId);
      setSuccess(`${name} removed`);
      await loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to remove driver');
    }
  };

  // --- Helpers ---
  const getBadge = (status) => {
    const map = {
      'PENDING': <span className="badge badge-warning">Pending</span>,
      'ACCEPTED': <span className="badge badge-success">Accepted</span>,
      'REJECTED': <span className="badge badge-danger">Rejected</span>,
      'CANCELLED': <span className="badge badge-default">Cancelled</span>,
    };
    return map[status] || <span className="badge badge-default">{status}</span>;
  };

  const getAssignmentStatus = (driver) => {
    if (!driver.start_date || !driver.end_date) return null;
    const isExpired = new Date(driver.end_date) < new Date();
    return isExpired ? 
      <span className="badge badge-danger">Expired</span> : 
      <span className="badge badge-success">Active</span>;
  };

  if (loading) return <div className="fleet-drivers-container"><div style={{padding:'50px', textAlign:'center', color:'#666'}}>Loading drivers...</div></div>;

  return (
    <div className="fleet-drivers-container">
      {/* 1. Page Header */}
      <header className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          <span>←</span> Back
        </button>
        <h1>Fleet Drivers</h1>
        <div style={{width: 60}}></div> {/* Spacer to balance flex */}
      </header>

      {/* Alerts */}
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* 2. Search Section */}
      <section className="search-section">
        <h2 className="section-title">Invite New Driver</h2>
        <form onSubmit={handleSearch} className="search-form">
          <input
            className="search-input"
            type="tel"
            placeholder="Enter driver phone number..."
            value={searchPhone}
            onChange={(e) => setSearchPhone(e.target.value)}
          />
          <button type="submit" className="btn-primary" disabled={searching}>
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {searchResult && (
          <div className="search-result">
            <div className="driver-mini-profile">
              <div className="avatar">{searchResult.full_name[0]}</div>
              <div className="driver-details">
                <h3>{searchResult.full_name}</h3>
                <p>{searchResult.phone}</p>
              </div>
            </div>
            <button className="btn-primary" onClick={handleInvite} disabled={inviting}>
              {inviting ? 'Sending...' : 'Send Invite'}
            </button>
          </div>
        )}
      </section>

      {/* 3. Pending Invites List */}
      {pendingInvites.length > 0 && (
        <section className="content-section">
          <h2 className="section-title">Pending Invites</h2>
          <div className="card-list">
            {pendingInvites.map(invite => (
              <div key={invite.invite_id} className="card">
                {/* Header within Card */}
                <div className="card-header">
                  <div className="card-header-left">
                     <div className="avatar" style={{background: '#9ca3af'}}>{invite.driver_name[0]}</div>
                     <div>
                        <h3 className="card-title">{invite.driver_name}</h3>
                        <p className="card-subtitle">{invite.driver_phone}</p>
                     </div>
                  </div>
                  {getBadge(invite.status)}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 4. Active Drivers List */}
      <section className="content-section">
        <h2 className="section-title">Active Drivers ({drivers.length})</h2>
        {drivers.length === 0 ? (
          <div className="empty-state">No drivers in your fleet.</div>
        ) : (
          <div className="card-list">
            {drivers.map(driver => (
              <div key={driver.driver_id} className="card">
                
                {/* This is the "Header" area for the driver card */}
                <div className="card-header">
                  <div className="card-header-left">
                    <div className="avatar">{driver.full_name[0]}</div>
                    <div>
                      <h3 className="card-title">{driver.full_name}</h3>
                      <p className="card-subtitle">{driver.phone}</p>
                    </div>
                  </div>
                  {/* Status Badge in Header */}
                  {getAssignmentStatus(driver) || <span className="badge badge-default">No Assignment</span>}
                </div>

                <div className="card-body">
                  <div className="data-row">
                    <span className="data-label">Vehicle Categories:</span>
                    <div className="tag-container">
                      {driver.allowed_vehicle_categories?.length 
                        ? driver.allowed_vehicle_categories.map(c => <span key={c} className="tag">{c}</span>)
                        : <span className="text-gray-400 text-sm">None</span>
                      }
                    </div>
                  </div>

                  <div className="data-row">
                    <span className="data-label">Assignment Period:</span>
                    <span className="data-value">
                      {driver.start_date 
                        ? `${new Date(driver.start_date).toLocaleDateString()} — ${new Date(driver.end_date).toLocaleDateString()}`
                        : 'Not set'
                      }
                    </span>
                  </div>
                </div>

                <div className="card-actions">
                  <button 
                    className="btn-outline"
                    onClick={() => {
                      setSelectedDriver(driver);
                      setDates({start: '', end: ''});
                      setShowAssignModal(true);
                    }}
                  >
                    Manage Assignment
                  </button>
                  <button 
                    className="btn-danger-outline"
                    onClick={() => handleRemove(driver.driver_id, driver.full_name)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* 5. Modal */}
      {showAssignModal && (
        <div className="modal-overlay" onClick={() => setShowAssignModal(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h2>Assign Dates</h2>
            <div className="form-group">
              <label>Start Date</label>
              <input type="date" className="form-input" 
                value={dates.start} onChange={e => setDates({...dates, start: e.target.value})} />
            </div>
            <div className="form-group">
              <label>End Date</label>
              <input type="date" className="form-input" 
                value={dates.end} onChange={e => setDates({...dates, end: e.target.value})} />
            </div>
            <div className="modal-footer">
              <button className="btn-outline" onClick={() => setShowAssignModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleAssign} disabled={assigning}>
                {assigning ? 'Saving...' : 'Confirm Assignment'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FleetDrivers;