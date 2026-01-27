import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DriverLayout from '../layout/DriverLayout';
import driverService from '../../services/driver.service';
import './DriverAvailability.css';

export default function DriverAvailability() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  const [driverProfile, setDriverProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [availabilityEntries, setAvailabilityEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [notEligible, setNotEligible] = useState(false);

  const [formData, setFormData] = useState({
    date: '',
    is_available: true,
    note: ''
  });

  const [expandedDate, setExpandedDate] = useState(null);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchDriverProfile();
  }, [token, navigate]);

  const fetchDriverProfile = async () => {
    try {
      setProfileLoading(true);
      const profile = await driverService.getMyProfile(token);
      
      if (!profile) {
        navigate('/app/home');
        return;
      }

      if (profile.approval_status !== 'APPROVED') {
        navigate('/app/home');
        return;
      }

      setDriverProfile(profile);
      // Once profile is loaded, fetch availability
      fetchAvailability();
    } catch (err) {
      console.error('Failed to fetch driver profile:', err);
      navigate('/app/home');
    } finally {
      setProfileLoading(false);
    }
  };

  const fetchAvailability = async () => {
    try {
      setLoading(true);
      setError('');
      setNotEligible(false);
      const data = await driverService.getWorkAvailability(token);
      setAvailabilityEntries(data);
    } catch (err) {
      // 403 means driver is not part of a BUSINESS fleet
      // Check status code OR error message for fleet/approval issues
      const is403 = err.status === 403;
      const messageIndicatesNotEligible = err.message && (
        err.message.includes('BUSINESS fleet') || 
        err.message.includes('no active') ||
        err.message.includes('not approved')
      );
      
      if (is403 || messageIndicatesNotEligible) {
        setNotEligible(true);
        setError('');
      } else {
        setError(err.message || 'Failed to load availability');
      }
      setAvailabilityEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAddAvailability = async () => {
    if (!formData.date) {
      setError('Please select a date');
      return;
    }

    try {
      setSubmitting(true);
      setError('');

      await driverService.updateWorkAvailability(token, {
        date: formData.date,
        is_available: formData.is_available,
        note: formData.note
      });

      setFormData({ date: '', is_available: true, note: '' });
      setShowAddForm(false);
      await fetchAvailability();
    } catch (err) {
      setError(err.message || 'Failed to update availability');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleAvailability = async (entry) => {
    try {
      setError('');
      await driverService.updateWorkAvailability(token, {
        date: entry.date,
        is_available: !entry.is_available,
        note: entry.note
      });
      await fetchAvailability();
    } catch (err) {
      setError(err.message || 'Failed to update availability');
    }
  };

  const handleRemoveAvailability = async (date) => {
    if (!window.confirm('Remove this availability entry?')) return;

    try {
      setError('');
      // Backend does not support DELETE; mark as unavailable instead
      await driverService.updateWorkAvailability(token, { date, is_available: false, note: null });
      await fetchAvailability();
    } catch (err) {
      setError(err.message || 'Failed to remove availability');
    }
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const groupedByAvailability = {
    available: availabilityEntries.filter(e => e.is_available),
    unavailable: availabilityEntries.filter(e => !e.is_available)
  };

  // Show loading while fetching driver profile
  if (profileLoading) {
    return (
      <div className="page-loading">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="driver-availability-container">
        <div className="availability-header">
          <div className="header-content">
            <h1>Work Availability</h1>
            <p className="header-description">
              Plan your availability for upcoming days to help accept requests efficiently
            </p>
          </div>
          {!showAddForm && !notEligible && (
            <button
              className="btn-primary btn-add-availability"
              onClick={() => setShowAddForm(true)}
            >
              Add Availability
            </button>
          )}
        </div>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {notEligible && (
          <div className="info-banner">
            <div className="info-icon">ℹ️</div>
            <div className="info-content">
              <h3>Feature Not Available</h3>
              <p>
                Work Availability scheduling is only available for drivers who are part of a <strong>Business Fleet</strong>.
              </p>
              <p>
                As an independent driver, you can go online/offline anytime using the shift controls on your dashboard.
                If you want access to scheduled availability and other fleet benefits, consider joining a business fleet.
              </p>
              <button
                className="btn-secondary"
                onClick={() => navigate('/app/driver/fleets')}
              >
                Explore Fleets
              </button>
            </div>
          </div>
        )}

        {!notEligible && showAddForm && (
          <div className="add-availability-card">
            <h2>Add Availability Entry</h2>

            <div className="form-section">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleFormChange}
                  min={getMinDate()}
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_available"
                    checked={formData.is_available}
                    onChange={handleFormChange}
                  />
                  <span>I am available on this date</span>
                </label>
              </div>

              <div className="form-group">
                <label>Notes (optional)</label>
                <textarea
                  name="note"
                  value={formData.note}
                  onChange={handleFormChange}
                  placeholder="e.g., Available only in morning, working on other projects, etc."
                  rows="3"
                  maxLength="200"
                />
                <span className="char-count">
                  {formData.note.length}/200
                </span>
              </div>
            </div>

            <div className="form-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({ date: '', is_available: true, notes: '' });
                }}
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleAddAvailability}
                disabled={!formData.date || submitting}
              >
                {submitting ? 'Saving...' : 'Save Entry'}
              </button>
            </div>
          </div>
        )}

        {!notEligible && loading ? (
          <div className="loading-state">
            <p>Loading availability...</p>
          </div>
        ) : !notEligible && availabilityEntries.length === 0 && !showAddForm ? (
          <div className="empty-state">
            <p>No availability entries yet</p>
            <p className="empty-note">
              Add entries to help plan your work schedule and receive requests efficiently
            </p>
            <button
              className="btn-primary"
              onClick={() => setShowAddForm(true)}
            >
              Add First Entry
            </button>
          </div>
        ) : !notEligible && availabilityEntries.length > 0 ? (
          <div className="availability-content">
            <div className="availability-section">
              <h2 className="section-title">
                <span className="available-indicator"></span>
                Available ({groupedByAvailability.available.length})
              </h2>
              {groupedByAvailability.available.length === 0 ? (
                <div className="no-entries">No available dates</div>
              ) : (
                <div className="availability-list">
                  {groupedByAvailability.available.map(entry => (
                    <div key={entry.date} className="availability-entry available">
                      <div className="entry-header">
                        <div className="entry-date">
                          <span className="date-display">{formatDate(entry.date)}</span>
                          {entry.date === getTodayDate() && (
                            <span className="badge-today">Today</span>
                          )}
                        </div>
                        <button
                          className="btn-toggle"
                          onClick={() => handleToggleAvailability(entry)}
                          title="Mark as unavailable"
                        >
                          <span className="toggle-icon">✓</span>
                        </button>
                      </div>
                      {entry.notes && (
                        <div className="entry-notes">
                          <span className="notes-label">Notes:</span>
                          <span className="notes-text">{entry.notes}</span>
                        </div>
                      )}
                      <button
                        className="btn-remove"
                        onClick={() => handleRemoveAvailability(entry.date)}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="availability-section">
              <h2 className="section-title">
                <span className="unavailable-indicator"></span>
                Unavailable ({groupedByAvailability.unavailable.length})
              </h2>
              {groupedByAvailability.unavailable.length === 0 ? (
                <div className="no-entries">No unavailable dates</div>
              ) : (
                <div className="availability-list">
                  {groupedByAvailability.unavailable.map(entry => (
                    <div key={entry.date} className="availability-entry unavailable">
                      <div className="entry-header">
                        <div className="entry-date">
                          <span className="date-display">{formatDate(entry.date)}</span>
                          {entry.date === getTodayDate() && (
                            <span className="badge-today">Today</span>
                          )}
                        </div>
                        <button
                          className="btn-toggle"
                          onClick={() => handleToggleAvailability(entry)}
                          title="Mark as available"
                        >
                          <span className="toggle-icon">✗</span>
                        </button>
                      </div>
                      {entry.notes && (
                        <div className="entry-notes">
                          <span className="notes-label">Notes:</span>
                          <span className="notes-text">{entry.notes}</span>
                        </div>
                      )}
                      <button
                        className="btn-remove"
                        onClick={() => handleRemoveAvailability(entry.date)}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}

        <div className="availability-info-box">
          <h3>How Availability Works</h3>
          <ul>
            <li>Add entries to indicate which days you plan to work</li>
            <li>Mark dates as available to receive ride requests on those days</li>
            <li>Mark dates as unavailable if you plan to be offline</li>
            <li>You can add notes to explain your availability</li>
            <li>Edit or remove entries anytime</li>
          </ul>
        </div>
      </div>
    </DriverLayout>
  );
}
