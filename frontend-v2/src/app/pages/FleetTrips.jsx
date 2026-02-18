import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import Icons from '../../components/Icons';
import './FleetTrips.css';

function FleetTrips() {
  const navigate = useNavigate();
  
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [trips, setTrips] = useState([]);
  const [total, setTotal] = useState(0);
  
  // Pagination
  const [skip, setSkip] = useState(0);
  const limit = 20;

  // Load trips
  const loadTrips = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fleetService.listTrips(skip, limit);
      
      setTrips(response.trips || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Load trips error:', err);
      // Optional: Redirect if unauthorized
      // if (err.response?.status === 403) navigate('/rider-dashboard');
      setError(err.message || 'Failed to load trips');
    } finally {
      setLoading(false);
    }
  }, [skip]);

  useEffect(() => {
    loadTrips();
  }, [loadTrips]);

  // Helper Functions
  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED': return <span className="badge badge-success">Completed</span>;
      case 'IN_PROGRESS': return <span className="badge badge-info">In Progress</span>;
      case 'CANCELLED': return <span className="badge badge-danger">Cancelled</span>;
      case 'REQUESTED': return <span className="badge badge-warning">Requested</span>;
      default: return <span className="badge badge-default">{status}</span>;
    }
  };

  const formatFare = (amount) => {
    if (!amount) return '₹0.00';
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString('en-IN', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  // Calculate earnings for current page
  const pageEarnings = trips
    .filter(t => t.status === 'COMPLETED')
    .reduce((sum, t) => sum + (parseFloat(t.fare_amount) || 0), 0);

  if (loading && trips.length === 0) {
    return (
      <div className="fleet-trips-container">
        <div style={{padding: '50px', textAlign: 'center', color: '#666'}}>Loading trips...</div>
      </div>
    );
  }

  return (
    <div className="fleet-trips-container">
      {/* 1. Header */}
      <header className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          <span>←</span> Back
        </button>
        <h1>Fleet Trips</h1>
        <div style={{ width: '60px' }}></div>
      </header>

      {error && <div className="alert alert-error">{error}</div>}

      {/* 2. Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-value">{total}</span>
          <span className="stat-label">Total Trips</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{trips.filter(t => t.status === 'COMPLETED').length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card earnings">
          <span className="stat-value">{formatFare(pageEarnings)}</span>
          <span className="stat-label">Page Earnings</span>
        </div>
      </div>

      {/* 3. Trips List */}
      <div className="section">
        <h2 className="section-title">Trip History</h2>
        
        {trips.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon"><Icons.Clipboard size={48} /></span>
            <p>No trips found.</p>
          </div>
        ) : (
          <>
            <div className="trips-list">
              {trips.map((trip) => (
                <div key={trip.trip_id} className="trip-card">
                  
                  {/* Card Header */}
                  <div className="trip-card-header">
                    <span className="trip-id">#{trip.trip_id}</span>
                    {getStatusBadge(trip.status)}
                  </div>

                  {/* Card Body */}
                  <div className="trip-card-body">
                    <div className="trip-row">
                      <span className="row-label">Driver</span>
                      <span className="row-value">{trip.driver_name || 'N/A'}</span>
                    </div>
                    
                    <div className="trip-row">
                      <span className="row-label">Vehicle</span>
                      <span className="row-value">
                        {trip.vehicle_registration || 'N/A'} 
                        {trip.vehicle_category ? ` • ${trip.vehicle_category}` : ''}
                      </span>
                    </div>

                    <div className="trip-row">
                      <span className="row-label">Requested</span>
                      <span className="row-value">{formatDate(trip.requested_at)}</span>
                    </div>

                    {trip.completed_at && (
                      <div className="trip-row">
                        <span className="row-label">Completed</span>
                        <span className="row-value">{formatDate(trip.completed_at)}</span>
                      </div>
                    )}

                    <div className="trip-row" style={{marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed #eee'}}>
                      <span className="row-label">Fare Amount</span>
                      <span className="row-value fare">{formatFare(trip.fare_amount)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {total > limit && (
              <div className="pagination">
                <button
                  className="btn-page"
                  onClick={() => setSkip(Math.max(0, skip - limit))}
                  disabled={skip === 0 || loading}
                >
                  Previous
                </button>
                <span className="page-info">
                  Showing {skip + 1} - {Math.min(skip + limit, total)} of {total}
                </span>
                <button
                  className="btn-page"
                  onClick={() => setSkip(skip + limit)}
                  disabled={skip + limit >= total || loading}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default FleetTrips;