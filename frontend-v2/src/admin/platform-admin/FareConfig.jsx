import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './Countries.css';

const VEHICLE_CATEGORIES = ['BIKE', 'AUTO', 'CAB', 'XL'];

const FareConfig = () => {
  const [configs, setConfigs] = useState([]);
  const [countries, setCountries] = useState([]);
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [toast, setToast] = useState('');

  const [filterCountry, setFilterCountry] = useState('');
  const [filterCity, setFilterCity] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  const [form, setForm] = useState({
    city_id: '', vehicle_category: '', currency: '', base_fare: '', per_km_rate: '',
    per_min_rate: '', minimum_fare: '', booking_fee: '', surge_allowed: true,
    night_charge_pct: '', effective_from: '', effective_to: ''
  });

  useEffect(() => { loadInitial(); }, []);

  const loadInitial = async () => {
    try {
      setLoading(true);
      const [countriesData, citiesData, configsData] = await Promise.all([
        adminService.platformListCountries(),
        adminService.platformListCities(),
        adminService.platformListFareConfigs(null, null)
      ]);
      setCountries(countriesData);
      setCities(citiesData);
      setConfigs(configsData);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadConfigs = async (cityId, category) => {
    try {
      const data = await adminService.platformListFareConfigs(cityId || null, category || null);
      setConfigs(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const handleCountryChange = async (code) => {
    setFilterCountry(code);
    setFilterCity('');
    if (code) {
      const data = await adminService.platformListCities(code);
      setCities(data);
    } else {
      const data = await adminService.platformListCities();
      setCities(data);
    }
    loadConfigs('', filterCategory);
  };

  const handleCityChange = (cityId) => {
    setFilterCity(cityId);
    loadConfigs(cityId, filterCategory);
  };

  const handleCategoryChange = (cat) => {
    setFilterCategory(cat);
    loadConfigs(filterCity, cat);
  };

  const openCreate = () => {
    setEditingConfig(null);
    const selectedCity = cities.find(c => String(c.city_id) === String(filterCity));
    setForm({
      city_id: filterCity || '',
      vehicle_category: filterCategory || '',
      currency: selectedCity?.currency || '',
      base_fare: '', per_km_rate: '', per_min_rate: '',
      minimum_fare: '', booking_fee: '', surge_allowed: true,
      night_charge_pct: '', effective_from: '', effective_to: ''
    });
    setShowModal(true);
  };

  const openEdit = (config) => {
    setEditingConfig(config);
    const toLocal = (dt) => {
      if (!dt) return '';
      const d = new Date(dt);
      d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
      return d.toISOString().slice(0, 16);
    };
    setForm({
      city_id: config.city_id,
      vehicle_category: config.vehicle_category,
      currency: config.currency || '',
      base_fare: config.base_fare ?? '',
      per_km_rate: config.per_km_rate ?? '',
      per_min_rate: config.per_min_rate ?? '',
      minimum_fare: config.minimum_fare ?? '',
      booking_fee: config.booking_fee ?? '',
      surge_allowed: config.surge_allowed ?? true,
      night_charge_pct: config.night_charge_pct ?? '',
      effective_from: toLocal(config.effective_from),
      effective_to: toLocal(config.effective_to)
    });
    setShowModal(true);
  };

  const handleDeactivate = async (id) => {
    if (!window.confirm('Deactivate this fare config? This will set effective_to to now().')) return;
    try {
      await adminService.platformDeactivateFareConfig(id);
      showToast('Fare config deactivated');
      loadConfigs(filterCity, filterCategory);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingConfig) {
        const payload = {
          base_fare: Number(form.base_fare),
          per_km_rate: Number(form.per_km_rate),
          per_min_rate: Number(form.per_min_rate),
          minimum_fare: form.minimum_fare ? Number(form.minimum_fare) : null,
          booking_fee: form.booking_fee ? Number(form.booking_fee) : null,
          night_charge_pct: form.night_charge_pct ? Number(form.night_charge_pct) : null,
          surge_allowed: form.surge_allowed,
          effective_from: form.effective_from || null,
          effective_to: form.effective_to || null,
        };
        await adminService.platformUpdateFareConfig(editingConfig.fare_config_id, payload);
        showToast('Fare config updated successfully');
      } else {
        const payload = {
          ...form,
          city_id: Number(form.city_id),
          base_fare: Number(form.base_fare),
          per_km_rate: Number(form.per_km_rate),
          per_min_rate: Number(form.per_min_rate),
          minimum_fare: form.minimum_fare ? Number(form.minimum_fare) : null,
          booking_fee: form.booking_fee ? Number(form.booking_fee) : null,
          night_charge_pct: form.night_charge_pct ? Number(form.night_charge_pct) : null,
          effective_to: form.effective_to || null,
        };
        await adminService.platformCreateFareConfig(payload);
        showToast('Fare config created successfully');
      }
      setShowModal(false);
      setEditingConfig(null);
      loadConfigs(filterCity, filterCategory);
    } catch (err) {
      setError(err.message);
    }
  };

  const fmt = (dt) => dt ? new Date(dt).toLocaleString() : '—';

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="countries-container">
      {toast && <div className="success-toast">{toast}</div>}

      <div className="countries-header">
        <h1>Fare Config</h1>
        <button className="btn-primary" onClick={openCreate}>+ Add Fare Config</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="filters-row">
        <div className="filter-group">
          <label>Country</label>
          <select value={filterCountry} onChange={e => handleCountryChange(e.target.value)}>
            <option value="">All</option>
            {countries.map(c => <option key={c.country_code} value={c.country_code}>{c.name}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>City</label>
          <select value={filterCity} onChange={e => handleCityChange(e.target.value)}>
            <option value="">All Cities</option>
            {cities.map(c => <option key={c.city_id} value={c.city_id}>{c.name}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>Vehicle Category</label>
          <select value={filterCategory} onChange={e => handleCategoryChange(e.target.value)}>
            <option value="">All</option>
            {VEHICLE_CATEGORIES.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      {configs.length === 0 ? (
        <div className="empty-state">
          <p>No fare configs found</p>
          <button className="btn-primary" onClick={openCreate}>Add Fare Config</button>
        </div>
      ) : (
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Base Fare</th>
                <th>Per KM</th>
                <th>Per Min</th>
                <th>Min Fare</th>
                <th>Booking Fee</th>
                <th>Night %</th>
                <th>Surge</th>
                <th>Effective From</th>
                <th>Effective To</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map(c => (
                <tr key={c.fare_config_id}>
                  <td><strong>{c.vehicle_category}</strong></td>
                  <td>{c.currency} {Number(c.base_fare).toFixed(2)}</td>
                  <td>{Number(c.per_km_rate).toFixed(2)}</td>
                  <td>{Number(c.per_min_rate).toFixed(2)}</td>
                  <td>{c.minimum_fare ? Number(c.minimum_fare).toFixed(2) : '—'}</td>
                  <td>{c.booking_fee ? Number(c.booking_fee).toFixed(2) : '—'}</td>
                  <td>{c.night_charge_pct ? `${Number(c.night_charge_pct)}%` : '—'}</td>
                  <td>{c.surge_allowed ? 'Yes' : 'No'}</td>
                  <td>{fmt(c.effective_from)}</td>
                  <td>{fmt(c.effective_to)}</td>
                  <td>
                    <button className="btn-action btn-edit" onClick={() => openEdit(c)}>Edit</button>
                    {!c.effective_to && (
                      <button className="btn-action btn-deactivate" onClick={() => handleDeactivate(c.fare_config_id)}>
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => { setShowModal(false); setEditingConfig(null); }}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>{editingConfig ? 'Edit Fare Config' : 'Add Fare Config'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>City</label>
                <select value={form.city_id} onChange={e => {
                  const city = cities.find(c => String(c.city_id) === e.target.value);
                  setForm({ ...form, city_id: e.target.value, currency: city?.currency || form.currency });
                }} required disabled={!!editingConfig}>
                  <option value="">Select City</option>
                  {cities.map(c => <option key={c.city_id} value={c.city_id}>{c.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Vehicle Category</label>
                <select value={form.vehicle_category} onChange={e => setForm({ ...form, vehicle_category: e.target.value })} required disabled={!!editingConfig}>
                  <option value="">Select</option>
                  {VEHICLE_CATEGORIES.map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Currency</label>
                <input value={form.currency} onChange={e => setForm({ ...form, currency: e.target.value.toUpperCase() })} maxLength={3} required readOnly />
              </div>
              <div className="form-group">
                <label>Base Fare</label>
                <input type="number" step="0.01" value={form.base_fare} onChange={e => setForm({ ...form, base_fare: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Per KM Rate</label>
                <input type="number" step="0.01" value={form.per_km_rate} onChange={e => setForm({ ...form, per_km_rate: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Per Minute Rate</label>
                <input type="number" step="0.01" value={form.per_min_rate} onChange={e => setForm({ ...form, per_min_rate: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Minimum Fare</label>
                <input type="number" step="0.01" value={form.minimum_fare} onChange={e => setForm({ ...form, minimum_fare: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Booking Fee</label>
                <input type="number" step="0.01" value={form.booking_fee} onChange={e => setForm({ ...form, booking_fee: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Night Charge (%)</label>
                <input type="number" step="0.01" value={form.night_charge_pct} onChange={e => setForm({ ...form, night_charge_pct: e.target.value })} />
              </div>
              <div className="form-group">
                <label>
                  <input type="checkbox" checked={form.surge_allowed} onChange={e => setForm({ ...form, surge_allowed: e.target.checked })} style={{ marginRight: 8 }} />
                  Surge Allowed
                </label>
              </div>
              <div className="form-group">
                <label>Effective From</label>
                <input type="datetime-local" value={form.effective_from} onChange={e => setForm({ ...form, effective_from: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Effective To (optional)</label>
                <input type="datetime-local" value={form.effective_to} onChange={e => setForm({ ...form, effective_to: e.target.value })} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => { setShowModal(false); setEditingConfig(null); }}>Cancel</button>
                <button type="submit" className="btn-primary">{editingConfig ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FareConfig;
