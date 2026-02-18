import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './Countries.css';

const VEHICLE_CATEGORIES = ['BIKE', 'AUTO', 'CAB', 'XL'];

const CommissionConfig = () => {
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
    city_id: '', vehicle_category: '', commission_type: 'PERCENTAGE',
    fixed_amount: '', percentage: '', currency: '',
    effective_from: '', effective_to: ''
  });

  useEffect(() => { loadInitial(); }, []);

  const loadInitial = async () => {
    try {
      setLoading(true);
      const [countriesData, citiesData, configsData] = await Promise.all([
        adminService.platformListCountries(),
        adminService.platformListCities(),
        adminService.platformListCommissionConfigs(null, null)
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
      const data = await adminService.platformListCommissionConfigs(cityId || null, category || null);
      setConfigs(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const handleCountryChange = async (code) => {
    setFilterCountry(code);
    setFilterCity('');
    const data = code ? await adminService.platformListCities(code) : await adminService.platformListCities();
    setCities(data);
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
      commission_type: 'PERCENTAGE',
      fixed_amount: '', percentage: '',
      currency: selectedCity?.currency || '',
      effective_from: '', effective_to: ''
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
      commission_type: config.commission_type || 'PERCENTAGE',
      fixed_amount: config.fixed_amount ?? '',
      percentage: config.percentage ?? '',
      currency: config.currency || '',
      effective_from: toLocal(config.effective_from),
      effective_to: toLocal(config.effective_to)
    });
    setShowModal(true);
  };

  const handleDeactivate = async (id) => {
    if (!window.confirm('Deactivate this commission config?')) return;
    try {
      await adminService.platformDeactivateCommissionConfig(id);
      showToast('Commission config deactivated');
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
          commission_type: form.commission_type,
          fixed_amount: form.commission_type === 'FIXED' ? Number(form.fixed_amount) : null,
          percentage: form.commission_type === 'PERCENTAGE' ? Number(form.percentage) : null,
          effective_from: form.effective_from || null,
          effective_to: form.effective_to || null,
        };
        await adminService.platformUpdateCommissionConfig(editingConfig.id, payload);
        showToast('Commission config updated successfully');
      } else {
        const payload = {
          city_id: Number(form.city_id),
          vehicle_category: form.vehicle_category,
          commission_type: form.commission_type,
          fixed_amount: form.commission_type === 'FIXED' ? Number(form.fixed_amount) : null,
          percentage: form.commission_type === 'PERCENTAGE' ? Number(form.percentage) : null,
          currency: form.currency,
          effective_from: form.effective_from,
          effective_to: form.effective_to || null,
        };
        await adminService.platformCreateCommissionConfig(payload);
        showToast('Commission config created successfully');
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
        <h1>Commission Config</h1>
        <button className="btn-primary" onClick={openCreate}>+ Add Commission Config</button>
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
          <p>No commission configs found</p>
          <button className="btn-primary" onClick={openCreate}>Add Commission Config</button>
        </div>
      ) : (
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Type</th>
                <th>Fixed Amount</th>
                <th>Percentage</th>
                <th>Currency</th>
                <th>Active</th>
                <th>Effective From</th>
                <th>Effective To</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map(c => (
                <tr key={c.id}>
                  <td><strong>{c.vehicle_category}</strong></td>
                  <td>{c.commission_type}</td>
                  <td>{c.commission_type === 'FIXED' ? `${c.currency} ${Number(c.fixed_amount).toFixed(2)}` : '—'}</td>
                  <td>{c.commission_type === 'PERCENTAGE' ? `${(Number(c.percentage) * 100).toFixed(2)}%` : '—'}</td>
                  <td>{c.currency}</td>
                  <td>
                    <span className={c.is_active ? 'status-active' : 'status-inactive'}>
                      {c.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>{fmt(c.effective_from)}</td>
                  <td>{fmt(c.effective_to)}</td>
                  <td>
                    <button className="btn-action btn-edit" onClick={() => openEdit(c)}>Edit</button>
                    {c.is_active && !c.effective_to && (
                      <button className="btn-action btn-deactivate" onClick={() => handleDeactivate(c.id)}>
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
            <h2>{editingConfig ? 'Edit Commission Config' : 'Add Commission Config'}</h2>
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
                <label>Commission Type</label>
                <select value={form.commission_type} onChange={e => setForm({ ...form, commission_type: e.target.value })} required>
                  <option value="FIXED">FIXED</option>
                  <option value="PERCENTAGE">PERCENTAGE</option>
                </select>
              </div>
              {form.commission_type === 'FIXED' && (
                <div className="form-group">
                  <label>Fixed Amount</label>
                  <input type="number" step="0.01" value={form.fixed_amount} onChange={e => setForm({ ...form, fixed_amount: e.target.value })} required />
                </div>
              )}
              {form.commission_type === 'PERCENTAGE' && (
                <div className="form-group">
                  <label>Percentage (decimal, e.g. 0.20 = 20%)</label>
                  <input type="number" step="0.0001" min="0" max="1" value={form.percentage} onChange={e => setForm({ ...form, percentage: e.target.value })} required />
                </div>
              )}
              <div className="form-group">
                <label>Currency</label>
                <input value={form.currency} readOnly />
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

export default CommissionConfig;
