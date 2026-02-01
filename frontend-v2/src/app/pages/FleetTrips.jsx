import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
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
      if (err.status === 404 || err.status === 403) {
        navigate('/rider-dashboard');
        return;
      }
      setError(err.message || 'Failed to load trips');
    } finally {
      setLoading(false);
    }
  }, [navigate, skip]);

  useEffect(() => {
    loadTrips();
  }, [loadTrips]);

  // Get status badge
  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="badge badge-success">Completed</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-info">In Progress</span>;
      case 'CANCELLED':
        return <span className="badge badge-danger">Cancelled</span>;
      case 'REQUESTED':
        return <span className="badge badge-warning">Requested</span>;
      default:
        return <span className="badge badge-default">{status}</span>;
    }
  };

  // Format fare
  const formatFare = (amount) => {
    if (!amount) return '₹0';
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  };

  // Calculate total earnings
  const totalEarnings = trips
    .filter(t => t.status === 'COMPLETED')
    .reduce((sum, t) => sum + (parseFloat(t.fare_amount) || 0), 0);

  if (loading && trips.length === 0) {
    return (
      <div className="fleet-trips">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading trips...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fleet-trips">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          ← Back
        </button>
        <h1>Fleet Trips</h1>
        <div style={{ width: '60px' }}></div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Summary Stats */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-value">{total}</span>
          <span className="stat-label">Total Trips</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{trips.filter(t => t.status === 'COMPLETED').length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card earnings">
          <span className="stat-value">{formatFare(totalEarnings)}</span>
          <span className="stat-label">Page Earnings</span>
        </div>
      </div>

      {/* Trips List */}
      <div className="section">
        <h2>Trip History</h2>
        {trips.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📋</span>
            <p>No trips yet</p>
            <p className="hint">Trips completed by your fleet drivers will appear here</p>
          </div>
        ) : (
          <>
            <div className="trips-list">
              {trips.map((trip) => (
                <div key={trip.trip_id} className="trip-card">
                  <div className="trip-header">
                    <span className="trip-id">Trip #{trip.trip_id}</span>
                    {getStatusBadge(trip.status)}
                  </div>
                  <div className="trip-details">
                    <div className="trip-row">
                      <span className="label">Driver:</span>
                      <span className="value">{trip.driver_name || 'N/A'}</span>
                    </div>
                    <div className="trip-row">
                      <span className="label">Vehicle:</span>
                      <span className="value">
                        {trip.vehicle_registration || 'N/A'}
                        {trip.vehicle_category && ` (${trip.vehicle_category})`}
                      </span>
                    </div>
                    <div className="trip-row">
                      <span className="label">Fare:</span>
                      <span className="value fare">{formatFare(trip.fare_amount)}</span>
                    </div>
                    <div className="trip-row">
                      <span className="label">Requested:</span>
                      <span className="value">{formatDate(trip.requested_at)}</span>
                    </div>
                    {trip.completed_at && (
                      <div className="trip-row">
                        <span className="label">Completed:</span>
                        <span className="value">{formatDate(trip.completed_at)}</span>
                      </div>
                    )}
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
                  ← Previous
                </button>
                <span className="page-info">
                  {skip + 1} - {Math.min(skip + limit, total)} of {total}
                </span>
                <button
                  className="btn-page"
                  onClick={() => setSkip(skip + limit)}
                  disabled={skip + limit >= total || loading}
                >
                  Next →
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
