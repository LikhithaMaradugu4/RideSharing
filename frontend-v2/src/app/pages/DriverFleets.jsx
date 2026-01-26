import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../../services/driver.service';
import DriverLayout from '../layout/DriverLayout';
import './DriverFleets.css';

function DriverFleets() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [driverProfile, setDriverProfile] = useState(null);
  const [activeFleet, setActiveFleet] = useState(null);
  const [invites, setInvites] = useState([]);
  const [availableFleets, setAvailableFleets] = useState([]);
  const [processingFleetId, setProcessingFleetId] = useState(null);
  const [activeTab, setActiveTab] = useState('current');

  const token = localStorage.getItem('jwt_token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [token, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch driver profile
      const profile = await driverService.getMyProfile(token);
      if (!profile || profile.approval_status !== 'APPROVED') {
        navigate('/app/home');
        return;
      }
      setDriverProfile(profile);

      // TODO: Fetch active fleet once backend API is ready
      setActiveFleet(null);

      // Fetch invites
      try {
        const result = await driverService.getFleetInvites(token);
        setInvites(result.invites || []);
      } catch {
        setInvites([]);
      }

      // Discover available fleets (pass tenantId when available)
      try {
        const result = await driverService.discoverFleets(token, { tenantId: profile.tenant_id });
        setAvailableFleets(result.fleets || []);
      } catch {
        setAvailableFleets([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to load page');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvite = async (fleetId) => {
    try {
      setProcessingFleetId(fleetId);
      setError(null);
      await driverService.acceptFleetInvite(token, fleetId);
      // Refetch data
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to accept invite');
    } finally {
      setProcessingFleetId(null);
    }
  };

  const handleRejectInvite = async (fleetId) => {
    try {
      setProcessingFleetId(fleetId);
      setError(null);
      await driverService.rejectFleetInvite(token, fleetId);
      // Refetch data
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to reject invite');
    } finally {
      setProcessingFleetId(null);
    }
  };

  if (loading) {
    return (
      <DriverLayout driverProfile={driverProfile}>
        <div className="fleets-container">
          <div className="loading-state">Loading fleets...</div>
        </div>
      </DriverLayout>
    );
  }

  if (!driverProfile) {
    return null;
  }

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="fleets-container">
        <div className="page-header">
          <h1>Fleet Management</h1>
          <p className="page-subtitle">Manage your fleet associations and pending invites</p>
        </div>

        {error && (
          <div className="error-banner">
            <span>⚠️</span>
            <span>{error}</span>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'current' ? 'active' : ''}`}
            onClick={() => setActiveTab('current')}
          >
            Current Fleet
          </button>
          <button
            className={`tab-btn ${activeTab === 'invites' ? 'active' : ''}`}
            onClick={() => setActiveTab('invites')}
          >
            Pending Invites {invites.length > 0 && `(${invites.length})`}
          </button>
          <button
            className={`tab-btn ${activeTab === 'discover' ? 'active' : ''}`}
            onClick={() => setActiveTab('discover')}
          >
            Discover Fleets
          </button>
        </div>

        {/* Current Fleet Tab */}
        {activeTab === 'current' && (
          <div className="tab-content">
            {activeFleet ? (
              <div className="fleet-card">
                <div className="fleet-header">
                  <h2>{activeFleet.name}</h2>
                  <span className="fleet-type-badge" style={{
                    backgroundColor: activeFleet.type === 'INDIVIDUAL' ? '#e3f2fd' : '#f3e5f5',
                    color: activeFleet.type === 'INDIVIDUAL' ? '#1976d2' : '#7b1fa2'
                  }}>
                    {activeFleet.type}
                  </span>
                </div>
                <div className="fleet-details">
                  <div className="detail-item">
                    <span className="label">Fleet ID</span>
                    <span className="value">{activeFleet.id}</span>
                  </div>
                  {activeFleet.type === 'BUSINESS' && (
                    <>
                      <div className="detail-item">
                        <span className="label">Contact</span>
                        <span className="value">{activeFleet.contact || 'N/A'}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Operating Cities</span>
                        <span className="value">
                          {activeFleet.cities && activeFleet.cities.length > 0
                            ? activeFleet.cities.join(', ')
                            : 'N/A'}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🏢</div>
                <h2>No active fleet</h2>
                <p>You will be assigned an INDIVIDUAL fleet upon driver approval.</p>
              </div>
            )}
          </div>
        )}

        {/* Pending Invites Tab */}
        {activeTab === 'invites' && (
          <div className="tab-content">
            {invites.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📨</div>
                <h2>No pending invites</h2>
                <p>Invitations will appear here when fleet owners invite you</p>
              </div>
            ) : (
              <>
                <div className="invites-warning">
                  <strong>Note:</strong> Accepting an invite will end your current fleet association.
                </div>
                <div className="invites-list">
                  {invites.map((invite) => (
                    <div key={invite.fleet_id} className="invite-card">
                      <div className="invite-header">
                        <h3>{invite.fleet_name}</h3>
                        <span className="invited-at">
                          Invited {new Date(invite.invited_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="invite-details">
                        {invite.city_name && (
                          <div className="detail-item">
                            <span className="label">City</span>
                            <span className="value">{invite.city_name}</span>
                          </div>
                        )}
                        {invite.contact_phone && (
                          <div className="detail-item">
                            <span className="label">Contact</span>
                            <span className="value">{invite.contact_phone}</span>
                          </div>
                        )}
                      </div>
                      <div className="invite-actions">
                        <button
                          className="btn btn-accept"
                          onClick={() => handleAcceptInvite(invite.fleet_id)}
                          disabled={processingFleetId === invite.fleet_id}
                        >
                          {processingFleetId === invite.fleet_id ? 'Processing...' : 'Accept'}
                        </button>
                        <button
                          className="btn btn-reject"
                          onClick={() => handleRejectInvite(invite.fleet_id)}
                          disabled={processingFleetId === invite.fleet_id}
                        >
                          {processingFleetId === invite.fleet_id ? 'Processing...' : 'Reject'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* Discover Fleets Tab */}
        {activeTab === 'discover' && (
          <div className="tab-content">
            {availableFleets.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <h2>No fleets available</h2>
                <p>Check back later for business fleet opportunities</p>
              </div>
            ) : (
              <div className="fleets-grid">
                {availableFleets.map((fleet) => (
                  <div key={fleet.fleet_id} className="fleet-discovery-card">
                    <div className="fleet-info">
                      <h3>{fleet.fleet_name}</h3>
                      {fleet.city_name && (
                        <p className="city-label">📍 {fleet.city_name}</p>
                      )}
                      {fleet.contact_phone && (
                        <p className="contact-label">📞 {fleet.contact_phone}</p>
                      )}
                    </div>
                    <p className="info-note">Fleet information only. Wait for an invite to join.</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </DriverLayout>
  );
}

export default DriverFleets;
