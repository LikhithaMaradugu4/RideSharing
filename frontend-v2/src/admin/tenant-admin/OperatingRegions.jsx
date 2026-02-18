import React, { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './OperatingRegions.css';

const OperatingRegions = () => {
  const [countries, setCountries] = useState([]);
  const [cities, setCities] = useState([]);
  const [availableCountries, setAvailableCountries] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [selectedCountryForCity, setSelectedCountryForCity] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('countries');
  const [addingCountry, setAddingCountry] = useState(false);
  const [addingCity, setAddingCity] = useState(false);
  const [selectedCountryId, setSelectedCountryId] = useState('');
  const [selectedCityId, setSelectedCityId] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedCountryForCity) {
      loadAvailableCities(selectedCountryForCity);
    }
  }, [selectedCountryForCity]);

const loadData = async () => {
  try {
    setLoading(true);
    setError(null); // Clear previous errors

    const [countriesData, citiesData, availCountriesData] = await Promise.all([
      adminService.getTenantCountries(),
      adminService.getTenantCities(),
      adminService.getAvailableCountries()
    ]);

    // admin.service.js already returns the arrays directly
    setCountries(countriesData || []);
    setCities(citiesData || []);
    setAvailableCountries(availCountriesData || []);

  } catch (err) {
    console.error('Data loading error:', err);
    // Error message is already extracted in the service
    const errorMessage = err.message || 'Failed to load operating regions';
    setError(errorMessage);
  } finally {
    setLoading(false);
  }
};

  const loadAvailableCities = async (countryCode) => {
    try {
      const citiesData = await adminService.getAvailableCities(countryCode);
      setAvailableCities(citiesData || []);
    } catch (err) {
      console.error('Failed to load cities:', err);
      setAvailableCities([]);
    }
  };

  const handleAddCountry = async () => {
  if (!selectedCountryId) return;
  try {
    setAddingCountry(true);
    // Removed parseInt because your backend wants a string country_code
    await adminService.addTenantCountry(selectedCountryId); 
    await loadData();
    setSelectedCountryId('');
  } catch (err) {
    setError(err.response?.data?.detail || 'Failed to add country');
  } finally {
    setAddingCountry(false);
  }
};

  const handleRemoveCountry = async (countryId) => {
    if (!window.confirm('Are you sure you want to remove this country? This will also remove all associated cities.')) {
      return;
    }
    try {
      await adminService.removeTenantCountry(countryId);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove country');
    }
  };

  const handleAddCity = async () => {
    if (!selectedCityId) return;
    try {
      setAddingCity(true);
      await adminService.addTenantCity(parseInt(selectedCityId));
      await loadData();
      setSelectedCityId('');
      setSelectedCountryForCity('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add city');
    } finally {
      setAddingCity(false);
    }
  };

  const handleRemoveCity = async (cityId) => {
    if (!window.confirm('Are you sure you want to remove this city?')) {
      return;
    }
    try {
      await adminService.removeTenantCity(cityId);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove city');
    }
  };

  if (loading) {
    return (
      <div className="operating-regions-view">
        <div className="loading-state">
          <p>Loading operating regions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="operating-regions-view">
      <div className="page-header">
        <h1>Operating Regions</h1>
        <p className="page-subtitle">Manage countries and cities where your tenant operates</p>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{error}</span>
          <button onClick={() => setError(null)} className="dismiss-btn">×</button>
        </div>
      )}

      <div className="tabs-container">
        <button
          className={`tab-btn ${activeTab === 'countries' ? 'active' : ''}`}
          onClick={() => setActiveTab('countries')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
          Countries ({countries.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'cities' ? 'active' : ''}`}
          onClick={() => setActiveTab('cities')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="4" y="2" width="16" height="20" rx="2" />
            <path d="M9 22V10h6v12M12 6v.01" />
          </svg>
          Cities ({cities.length})
        </button>
      </div>

      {activeTab === 'countries' && (
        <div className="section-content">
          <div className="add-form">
            <h3>Add Operating Country</h3>
            <div className="form-row">
              <select
                value={selectedCountryId}
                onChange={(e) => setSelectedCountryId(e.target.value)}
                className="form-select"
              >
                <option value="">Select a country...</option>
                {availableCountries.map(country => (
                  <option key={country.country_code} value={country.country_code}>
                    {country.country_name} ({country.country_code})
                  </option>
                ))}
              </select>
              <button
                onClick={handleAddCountry}
                disabled={!selectedCountryId || addingCountry}
                className="btn-add"
              >
                {addingCountry ? (
                  'Adding...'
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19" />
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    Add Country
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="items-list">
            {countries.length === 0 ? (
              <div className="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <p>No operating countries configured</p>
                <span>Add a country to start operating in a region</span>
              </div>
            ) : (
              countries.map(country => (
                <div key={country.country_code} className="item-card">
                  <div className="item-icon country-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M2 12h20" />
                    </svg>
                  </div>
                  <div className="item-info">
                    <h4>{country.country_name}</h4>
                    <span className="item-code">{country.country_code}</span>
                  </div>
                  <div className="item-meta">
                    <span className="badge active">Active</span>
                    {country.added_at && (
                      <span className="added-date">
                        Added {new Date(country.added_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveCountry(country.country_code)}
                    className="btn-remove"
                    title="Remove country"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3,6 5,6 21,6" />
                      <path d="M19,6V20a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'cities' && (
        <div className="section-content">
          <div className="add-form">
            <h3>Add Operating City</h3>
            <div className="form-row dual">
              <select
                value={selectedCountryForCity}
                onChange={(e) => setSelectedCountryForCity(e.target.value)}
                className="form-select"
              >
                <option value="">Select a country first...</option>
                {countries.map(country => (
                  <option key={country.country_code} value={country.country_code}>
                    {country.country_name}
                  </option>
                ))}
              </select>
              <select
                value={selectedCityId}
                onChange={(e) => setSelectedCityId(e.target.value)}
                className="form-select"
                disabled={!selectedCountryForCity}
              >
                <option value="">Select a city...</option>
                {availableCities.map(city => (
                  <option key={city.city_id} value={city.city_id}>
                    {city.city_name}
                  </option>
                ))}
              </select>
              <button
                onClick={handleAddCity}
                disabled={!selectedCityId || addingCity}
                className="btn-add"
              >
                {addingCity ? (
                  'Adding...'
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19" />
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    Add City
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="items-list">
            {cities.length === 0 ? (
              <div className="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="4" y="2" width="16" height="20" rx="2" />
                  <path d="M9 22V10h6v12M12 6v.01" />
                </svg>
                <p>No operating cities configured</p>
                <span>Add cities where your services will be available</span>
              </div>
            ) : (
              cities.map(city => (
                <div key={city.city_id} className="item-card">
                  <div className="item-icon city-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="4" y="2" width="16" height="20" rx="2" />
                      <path d="M9 22V10h6v12" />
                    </svg>
                  </div>
                  <div className="item-info">
                    <h4>{city.city_name}</h4>
                    <span className="item-code">{city.country_name}</span>
                  </div>
                  <div className="item-meta">
                    <span className="badge active">Active</span>
                    {city.added_at && (
                      <span className="added-date">
                        Added {new Date(city.added_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveCity(city.city_id)}
                    className="btn-remove"
                    title="Remove city"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3,6 5,6 21,6" />
                      <path d="M19,6V20a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OperatingRegions;
