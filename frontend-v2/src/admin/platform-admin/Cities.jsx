import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './Countries.css'; /* shares the same admin table / modal styles */

const Cities = () => {
  const [cities, setCities] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCity, setEditingCity] = useState(null);
  const [toast, setToast] = useState('');
  const [filterCountry, setFilterCountry] = useState('');
  const [form, setForm] = useState({
    country_code: '', name: '', timezone: '', currency: '', boundary_geojson: '{}', is_active: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [citiesData, countriesData] = await Promise.all([
        adminService.platformListCities(),
        adminService.platformListCountries()
      ]);
      setCities(citiesData);
      setCountries(countriesData);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadCities = async (countryCode) => {
    try {
      const data = await adminService.platformListCities(countryCode || null);
      setCities(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const openCreate = () => {
    setEditingCity(null);
    setForm({ country_code: filterCountry || '', name: '', timezone: '', currency: '', boundary_geojson: '{}', is_active: true });
    setShowModal(true);
  };

  const openEdit = (city) => {
    setEditingCity(city);
    setForm({
      country_code: city.country_code,
      name: city.name,
      timezone: city.timezone,
      currency: city.currency,
      boundary_geojson: city.boundary_geojson || '{}',
      is_active: city.is_active
    });
    setShowModal(true);
  };

  const handleFilterChange = (code) => {
    setFilterCountry(code);
    loadCities(code);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCity) {
        const { country_code, ...updateData } = form;
        await adminService.platformUpdateCity(editingCity.city_id, updateData);
        showToast('City updated successfully');
      } else {
        await adminService.platformCreateCity(form);
        showToast('City created successfully');
      }
      setShowModal(false);
      loadCities(filterCountry);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading cities...</div>;

  return (
    <div className="countries-container">
      {toast && <div className="success-toast">{toast}</div>}

      <div className="countries-header">
        <h1>Cities</h1>
        <button className="btn-primary" onClick={openCreate}>+ Add City</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="filters-row">
        <div className="filter-group">
          <label>Country</label>
          <select value={filterCountry} onChange={e => handleFilterChange(e.target.value)}>
            <option value="">All Countries</option>
            {countries.map(c => <option key={c.country_code} value={c.country_code}>{c.name}</option>)}
          </select>
        </div>
      </div>

      {cities.length === 0 ? (
        <div className="empty-state">
          <p>No cities found</p>
          <button className="btn-primary" onClick={openCreate}>Add First City</button>
        </div>
      ) : (
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>City Name</th>
                <th>Country</th>
                <th>Currency</th>
                <th>Timezone</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cities.map(c => (
                <tr key={c.city_id}>
                  <td>{c.city_id}</td>
                  <td><strong>{c.name}</strong></td>
                  <td>{c.country_code}</td>
                  <td>{c.currency}</td>
                  <td>{c.timezone}</td>
                  <td>
                    <span className={c.is_active ? 'status-active' : 'status-inactive'}>
                      {c.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <button className="btn-action btn-edit" onClick={() => openEdit(c)}>Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>{editingCity ? 'Edit City' : 'Add City'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Country</label>
                <select
                  value={form.country_code}
                  onChange={e => setForm({ ...form, country_code: e.target.value })}
                  required
                  disabled={!!editingCity}
                >
                  <option value="">Select Country</option>
                  {countries.map(c => <option key={c.country_code} value={c.country_code}>{c.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>City Name</label>
                <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required placeholder="Mumbai" />
              </div>
              <div className="form-group">
                <label>Currency (3 chars)</label>
                <input
                  value={form.currency}
                  onChange={e => setForm({ ...form, currency: e.target.value.toUpperCase() })}
                  maxLength={3}
                  required
                  placeholder="INR"
                />
              </div>
              <div className="form-group">
                <label>Timezone</label>
                <input value={form.timezone} onChange={e => setForm({ ...form, timezone: e.target.value })} required placeholder="Asia/Kolkata" />
              </div>
              <div className="form-group">
                <label>Boundary GeoJSON</label>
                <textarea
                  value={form.boundary_geojson}
                  onChange={e => setForm({ ...form, boundary_geojson: e.target.value })}
                  rows={4}
                  placeholder='{"type":"Polygon","coordinates":[...]}'
                />
              </div>
              {editingCity && (
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={form.is_active}
                      onChange={e => setForm({ ...form, is_active: e.target.checked })}
                      style={{ marginRight: 8 }}
                    />
                    Active
                  </label>
                </div>
              )}
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">{editingCity ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cities;
