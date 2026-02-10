import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import tokenStorage from '../../services/tokenStorage';
import Icons from '../../components/Icons';
import './FleetCities.css';

function FleetCities() {
  const navigate = useNavigate();
  const token = tokenStorage.get('jwt_token');
  
  const [cities, setCities] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Add city form
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    city_id: '',
    address: ''
  });

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
      
      const [citiesData, availableData] = await Promise.all([
        fleetService.listCities(),
        fleetService.getAvailableCities()
      ]);
      
      setCities(citiesData.cities || []);
      setAvailableCities(availableData.cities || []);
    } catch (err) {
      if (err.status === 403) {
        navigate('/fleet-dashboard');
        return;
      }
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    if (!formData.city_id) {
      setError('Please select a city');
      return;
    }

    try {
      setSubmitting(true);
      await fleetService.addCity(Number(formData.city_id), formData.address || null);
      
      setSuccess('City added successfully!');
      resetForm();
      fetchData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveCity = async (cityId) => {
    if (!window.confirm('Are you sure you want to remove this city?')) return;
    
    try {
      setError(null);
      await fleetService.removeCity(cityId);
      setSuccess('City removed successfully');
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const resetForm = () => {
    setShowAddForm(false);
    setFormData({ city_id: '', address: '' });
  };

  if (loading) {
    return (
      <div className="fleet-cities">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading cities...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="fleet-cities">
      <header className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          ← Back
        </button>
        <h1><Icons.MapPin size={24} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Fleet Cities</h1>
        <button 
          className="btn-add" 
          onClick={() => setShowAddForm(true)}
          disabled={availableCities.length === 0}
        >
          + Add City
        </button>
      </header>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Add City Form */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Add City</h2>
              <button className="btn-close" onClick={resetForm}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="add-city-form">
              <div className="form-group">
                <label htmlFor="city_id">Select City *</label>
                <select
                  id="city_id"
                  name="city_id"
                  value={formData.city_id}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">-- Select a city --</option>
                  {availableCities.map(city => (
                    <option key={city.city_id} value={city.city_id}>
                      {city.city_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="address">Fleet Office Address (Optional)</label>
                <textarea
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  placeholder="Enter your fleet office address in this city"
                  rows={3}
                />
                <span className="form-hint">
                  This address will be visible to drivers who want to join your fleet.
                </span>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={resetForm} disabled={submitting}>
                  Cancel
                </button>
                <button type="submit" className="btn-submit" disabled={submitting}>
                  {submitting ? 'Adding...' : 'Add City'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Cities List */}
      <div className="cities-list">
        {cities.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon"><Icons.MapPin size={48} /></span>
            <h2>No cities added yet</h2>
            <p>Add cities where your fleet operates</p>
            {availableCities.length > 0 && (
              <button className="btn-primary" onClick={() => setShowAddForm(true)}>
                Add Your First City
              </button>
            )}
          </div>
        ) : (
          cities.map(city => (
            <div key={city.city_id} className="city-card">
              <div className="city-info">
                <span className="city-name">{city.city_name}</span>
                {city.address && (
                  <span className="city-address"><Icons.MapPin size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} />{city.address}</span>
                )}
              </div>
              <div className="city-actions">
                <button 
                  className="btn-remove"
                  onClick={() => handleRemoveCity(city.city_id)}
                  title="Remove city"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Info Note */}
      {cities.length > 0 && (
        <div className="info-note">
          <strong><Icons.Lightbulb size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Tip:</strong> Add addresses to help drivers find your fleet offices. 
          Addresses are visible to drivers in the "Discover Fleets" section.
        </div>
      )}
    </div>
  );
}

export default FleetCities;
