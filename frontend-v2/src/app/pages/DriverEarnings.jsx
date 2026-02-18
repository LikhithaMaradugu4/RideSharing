/**
 * DriverEarnings.jsx
 * 
 * Driver Earnings & Settlement Page
 * 
 * Features:
 * - Wallet summary (balance showing amount owed)
 * - Earnings summary from completed trips
 * - Unsettled trips table with checkboxes
 * - Settle button to pay back commission
 * - Settlement history
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../../services/driver.service';
import authService from '../../services/auth.service';
import Icons from '../../components/Icons';
import './DriverEarnings.css';

const DriverEarnings = () => {
  const navigate = useNavigate();
  
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Wallet & Earnings data
  const [wallet, setWallet] = useState(null);
  const [earnings, setEarnings] = useState(null);
  const [unsettledTrips, setUnsettledTrips] = useState([]);
  const [payoutHistory, setPayoutHistory] = useState([]);
  
  // Selection state
  const [selectedTripIds, setSelectedTripIds] = useState([]);
  const [settling, setSettling] = useState(false);
  
  // Active tab
  const [activeTab, setActiveTab] = useState('unsettled'); // 'unsettled' | 'earnings' | 'history'

  // Load all data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = await authService.getValidToken();
      if (!token) {
        navigate('/login');
        return;
      }

      // Fetch all data in parallel
      const [walletData, earningsData, unsettledData, historyData] = await Promise.all([
        driverService.getWallet(token).catch(() => null),
        driverService.getEarnings(token).catch(() => null),
        driverService.getUnsettledTrips(token).catch(() => ({ trips: [] })),
        driverService.getPayoutHistory(token).catch(() => ({ payouts: [] }))
      ]);

      setWallet(walletData);
      setEarnings(earningsData);
      setUnsettledTrips(unsettledData?.trips || []);
      setPayoutHistory(historyData?.payouts || []);
      
    } catch (err) {
      console.error('Error loading earnings data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle trip selection
  const handleTripSelect = (tripId) => {
    setSelectedTripIds(prev => {
      if (prev.includes(tripId)) {
        return prev.filter(id => id !== tripId);
      } else {
        return [...prev, tripId];
      }
    });
  };

  // Select all trips
  const handleSelectAll = () => {
    if (selectedTripIds.length === unsettledTrips.length) {
      setSelectedTripIds([]);
    } else {
      setSelectedTripIds(unsettledTrips.map(t => t.trip_id));
    }
  };

  // Calculate selected amount
  const getSelectedAmount = () => {
    return unsettledTrips
      .filter(t => selectedTripIds.includes(t.trip_id))
      .reduce((sum, t) => sum + (t.total_commission || 0), 0);
  };

  // Handle settlement
  const handleSettle = async () => {
    if (selectedTripIds.length === 0) {
      setError('Please select at least one trip to settle');
      return;
    }

    try {
      setSettling(true);
      setError(null);
      setSuccessMessage(null);

      const token = await authService.getValidToken();
      const result = await driverService.settleTrips(token, selectedTripIds);

      setSuccessMessage(
        `Settlement successful! Amount: ₹${result.settlement_amount?.toFixed(2) || 0}. ` +
        `${result.trips_settled || 0} trips settled. New balance: ₹${result.new_balance?.toFixed(2) || 0}`
      );

      // Clear selection and reload data
      setSelectedTripIds([]);
      await loadData();

    } catch (err) {
      console.error('Settlement error:', err);
      setError(err.message || 'Settlement failed');
    } finally {
      setSettling(false);
    }
  };

  // Format currency
  const formatCurrency = (amount, currency = 'INR') => {
    const symbol = currency === 'INR' ? '₹' : currency;
    return `${symbol}${(amount || 0).toFixed(2)}`;
  };

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="driver-earnings-page">
        <div className="loading-state">Loading...</div>
      </div>
    );
  }

  return (
    <div className="driver-earnings-page">
      <header className="earnings-header">
        <h1><Icons.MoneyBag size={22} style={{verticalAlign: 'middle', marginRight: '6px'}} />Earnings & Settlement</h1>
        <button className="refresh-btn" onClick={loadData} disabled={loading}>
          <Icons.Refresh size={14} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Refresh
        </button>
      </header>

      {/* Messages */}
      {error && (
        <div className="alert alert-error">
          <Icons.XCircle size={14} style={{verticalAlign: 'middle', marginRight: '4px'}} /> {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
      {successMessage && (
        <div className="alert alert-success">
          <Icons.CheckCircle size={14} style={{verticalAlign: 'middle', marginRight: '4px'}} /> {successMessage}
          <button onClick={() => setSuccessMessage(null)}>×</button>
        </div>
      )}

      {/* Wallet Summary Card */}
      <div className="wallet-card">
        <h2>Wallet Summary</h2>
        <div className="wallet-grid">
          <div className="wallet-item">
            <label>Current Balance</label>
            <span className={`balance ${(wallet?.balance || 0) < 0 ? 'negative' : 'positive'}`}>
              {formatCurrency(wallet?.balance)}
            </span>
            <small>
              {(wallet?.balance || 0) < 0 
                ? <><Icons.Warning size={14} style={{verticalAlign: 'middle', marginRight: '2px'}} /> You owe this amount to platform</>
                : <><Icons.CheckCircle size={14} style={{verticalAlign: 'middle', marginRight: '2px'}} /> No outstanding dues</>}
            </small>
          </div>
          <div className="wallet-item">
            <label>Total Earnings</label>
            <span className="amount">
              {formatCurrency(earnings?.summary?.total_earnings)}
            </span>
            <small>From {earnings?.trip_count || 0} completed trips</small>
          </div>
          <div className="wallet-item">
            <label>Total Commission</label>
            <span className="amount commission">
              {formatCurrency(earnings?.summary?.total_commission)}
            </span>
            <small>Platform + Tenant + Fleet</small>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'unsettled' ? 'active' : ''}`}
          onClick={() => setActiveTab('unsettled')}
        >
          Unsettled Trips ({unsettledTrips.length})
        </button>
        <button 
          className={`tab ${activeTab === 'earnings' ? 'active' : ''}`}
          onClick={() => setActiveTab('earnings')}
        >
          Earnings Details
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Settlement History
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        
        {/* Unsettled Trips Tab */}
        {activeTab === 'unsettled' && (
          <div className="unsettled-section">
            {unsettledTrips.length === 0 ? (
              <div className="empty-state">
                <p><Icons.Party size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> No unsettled trips! You're all settled up.</p>
              </div>
            ) : (
              <>
                {/* Settlement Actions */}
                <div className="settlement-actions">
                  <div className="selection-info">
                    <span>
                      Selected: {selectedTripIds.length} trips | 
                      Amount: {formatCurrency(getSelectedAmount())}
                    </span>
                  </div>
                  <div className="action-buttons">
                    <button 
                      className="btn-secondary"
                      onClick={handleSelectAll}
                    >
                      {selectedTripIds.length === unsettledTrips.length ? 'Deselect All' : 'Select All'}
                    </button>
                    <button 
                      className="btn-primary settle-btn"
                      onClick={handleSettle}
                      disabled={settling || selectedTripIds.length === 0}
                    >
                      {settling ? 'Processing...' : `Settle ₹${getSelectedAmount().toFixed(2)}`}
                    </button>
                  </div>
                </div>

                {/* Trips Table */}
                <div className="trips-table-container">
                  <table className="trips-table">
                    <thead>
                      <tr>
                        <th>
                          <input 
                            type="checkbox"
                            checked={selectedTripIds.length === unsettledTrips.length && unsettledTrips.length > 0}
                            onChange={handleSelectAll}
                          />
                        </th>
                        <th>Trip ID</th>
                        <th>Date</th>
                        <th>Fare</th>
                        <th>Your Earning</th>
                        <th>Commission</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {unsettledTrips.map(trip => (
                        <tr 
                          key={trip.trip_id}
                          className={selectedTripIds.includes(trip.trip_id) ? 'selected' : ''}
                          onClick={() => handleTripSelect(trip.trip_id)}
                        >
                          <td>
                            <input 
                              type="checkbox"
                              checked={selectedTripIds.includes(trip.trip_id)}
                              onChange={() => handleTripSelect(trip.trip_id)}
                              onClick={e => e.stopPropagation()}
                            />
                          </td>
                          <td>#{trip.trip_id}</td>
                          <td>{formatDate(trip.completed_at)}</td>
                          <td>{formatCurrency(trip.fare_amount)}</td>
                          <td className="earning">{formatCurrency(trip.driver_earning)}</td>
                          <td className="commission">{formatCurrency(trip.total_commission)}</td>
                          <td>
                            <span className="badge unsettled">Unsettled</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}

        {/* Earnings Details Tab */}
        {activeTab === 'earnings' && (
          <div className="earnings-section">
            <div className="earnings-summary">
              <div className="summary-row">
                <span>Total Fare Collected:</span>
                <span>{formatCurrency(earnings?.summary?.total_fare)}</span>
              </div>
              <div className="summary-row">
                <span>Platform Fee:</span>
                <span className="deduction">-{formatCurrency(earnings?.summary?.total_platform_fee)}</span>
              </div>
              <div className="summary-row">
                <span>Tenant Commission:</span>
                <span className="deduction">-{formatCurrency(earnings?.summary?.total_tenant_commission)}</span>
              </div>
              <div className="summary-row">
                <span>Fleet Commission:</span>
                <span className="deduction">-{formatCurrency(earnings?.summary?.total_fleet_commission)}</span>
              </div>
              <div className="summary-row total">
                <span>Your Net Earnings:</span>
                <span className="earning">{formatCurrency(earnings?.summary?.total_earnings)}</span>
              </div>
            </div>

            {/* Recent Trips */}
            <h3>Recent Completed Trips</h3>
            <div className="trips-table-container">
              <table className="trips-table">
                <thead>
                  <tr>
                    <th>Trip ID</th>
                    <th>Date</th>
                    <th>Fare</th>
                    <th>Your Earning</th>
                    <th>Platform</th>
                    <th>Tenant</th>
                    <th>Fleet</th>
                    <th>Payment</th>
                    <th>Settlement</th>
                  </tr>
                </thead>
                <tbody>
                  {(earnings?.trips || []).map(trip => (
                    <tr key={trip.trip_id}>
                      <td>#{trip.trip_id}</td>
                      <td>{formatDate(trip.completed_at)}</td>
                      <td>{formatCurrency(trip.fare_amount)}</td>
                      <td className="earning">{formatCurrency(trip.driver_earning)}</td>
                      <td>{formatCurrency(trip.platform_fee)}</td>
                      <td>{formatCurrency(trip.tenant_commission)}</td>
                      <td>{formatCurrency(trip.fleet_commission)}</td>
                      <td>
                        <span className={`badge ${trip.payment_status === 'paid' ? 'paid' : 'pending'}`}>
                          {trip.payment_status || 'pending'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${trip.settlement_status === 'settled' ? 'settled' : 'unsettled'}`}>
                          {trip.settlement_status || 'unsettled'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Settlement History Tab */}
        {activeTab === 'history' && (
          <div className="history-section">
            {payoutHistory.length === 0 ? (
              <div className="empty-state">
                <p>No settlement history yet.</p>
              </div>
            ) : (
              <div className="history-list">
                {payoutHistory.map(payout => (
                  <div key={payout.id} className="history-item">
                    <div className="history-header">
                      <span className="payout-id">Settlement #{payout.id}</span>
                      <span className={`status ${payout.status}`}>{payout.status}</span>
                    </div>
                    <div className="history-details">
                      <div>
                        <label>Amount:</label>
                        <span>{formatCurrency(payout.total_amount)}</span>
                      </div>
                      <div>
                        <label>Date:</label>
                        <span>{formatDate(payout.processed_on || payout.created_on)}</span>
                      </div>
                      <div>
                        <label>Type:</label>
                        <span>{payout.payout_type}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DriverEarnings;
