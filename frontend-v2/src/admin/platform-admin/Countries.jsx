import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './Countries.css';

const Countries = () => {
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCountry, setEditingCountry] = useState(null);
  const [toast, setToast] = useState('');
  const [form, setForm] = useState({
    country_code: '', name: '', phone_code: '', default_timezone: '', default_currency: ''
  });

  useEffect(() => { loadCountries(); }, []);

  const loadCountries = async () => {
    try {
      setLoading(true);
      const data = await adminService.platformListCountries();
      setCountries(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const openCreate = () => {
    setEditingCountry(null);
    setForm({ country_code: '', name: '', phone_code: '', default_timezone: '', default_currency: '' });
    setShowModal(true);
  };

  const openEdit = (country) => {
    setEditingCountry(country);
    setForm({
      country_code: country.country_code,
      name: country.name,
      phone_code: country.phone_code,
      default_timezone: country.default_timezone,
      default_currency: country.default_currency
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCountry) {
        const { country_code, ...updateData } = form;
        await adminService.platformUpdateCountry(editingCountry.country_code, updateData);
        showToast('Country updated successfully');
      } else {
        await adminService.platformCreateCountry(form);
        showToast('Country created successfully');
      }
      setShowModal(false);
      loadCountries();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading countries...</div>;

  return (
    <div className="countries-container">
      {toast && <div className="success-toast">{toast}</div>}

      <div className="countries-header">
        <h1>Countries</h1>
        <button className="btn-primary" onClick={openCreate}>+ Add Country</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {countries.length === 0 ? (
        <div className="empty-state">
          <p>No countries configured</p>
          <button className="btn-primary" onClick={openCreate}>Add First Country</button>
        </div>
      ) : (
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Country Code</th>
                <th>Name</th>
                <th>Phone Code</th>
                <th>Default Currency</th>
                <th>Default Timezone</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {countries.map(c => (
                <tr key={c.country_code}>
                  <td><strong>{c.country_code}</strong></td>
                  <td>{c.name}</td>
                  <td>{c.phone_code}</td>
                  <td>{c.default_currency}</td>
                  <td>{c.default_timezone}</td>
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
            <h2>{editingCountry ? 'Edit Country' : 'Add Country'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Country Code (2 chars)</label>
                <input
                  value={form.country_code}
                  onChange={e => setForm({ ...form, country_code: e.target.value.toUpperCase() })}
                  maxLength={2}
                  required
                  disabled={!!editingCountry}
                  placeholder="IN"
                />
              </div>
              <div className="form-group">
                <label>Name</label>
                <input
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  required
                  placeholder="India"
                />
              </div>
              <div className="form-group">
                <label>Phone Code</label>
                <input
                  value={form.phone_code}
                  onChange={e => setForm({ ...form, phone_code: e.target.value })}
                  required
                  placeholder="+91"
                />
              </div>
              <div className="form-group">
                <label>Default Currency (3 chars)</label>
                <input
                  value={form.default_currency}
                  onChange={e => setForm({ ...form, default_currency: e.target.value.toUpperCase() })}
                  maxLength={3}
                  required
                  placeholder="INR"
                />
              </div>
              <div className="form-group">
                <label>Default Timezone</label>
                <input
                  value={form.default_timezone}
                  onChange={e => setForm({ ...form, default_timezone: e.target.value })}
                  required
                  placeholder="Asia/Kolkata"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">{editingCountry ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Countries;
