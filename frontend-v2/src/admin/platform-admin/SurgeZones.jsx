import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import SurgeMapSelector from './SurgeMapSelector';
import './SurgeZones.css';

const SurgeZones = () => {
  // ---------- state ----------
  const [zones, setZones] = useState([]);
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');

  // filters
  const [filterCity, setFilterCity] = useState('');
  const [searchName, setSearchName] = useState('');

  // modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingZone, setEditingZone] = useState(null);
  const [showMapPreview, setShowMapPreview] = useState(null); // zone to preview

  // form state
  const emptyForm = {
    city_id: '',
    name: '',
    multiplier: '1.5',
    starts_at: '',
    ends_at: '',
    boundary_geojson: null,
    is_active: true,
  };
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // ---------- helpers ----------
  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const toLocalDT = (dt) => {
    if (!dt) return '';
    const d = new Date(dt);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  };

  const getStatus = (zone) => {
    const now = new Date();
    const starts = new Date(zone.starts_at);
    const ends = new Date(zone.ends_at);
    if (!zone.is_active) return 'DISABLED';
    if (now < starts) return 'SCHEDULED';
    if (now > ends) return 'EXPIRED';
    return 'ACTIVE';
  };

  const statusBadge = (status) => {
    const map = {
      ACTIVE: 'status-badge status-active',
      SCHEDULED: 'status-badge status-scheduled',
      EXPIRED: 'status-badge status-expired',
      DISABLED: 'status-badge status-disabled',
    };
    return <span className={map[status] || ''}>{status}</span>;
  };

  // ---------- data loading ----------
  useEffect(() => { loadInitial(); }, []);

  const loadInitial = async () => {
    try {
      setLoading(true);
      const [citiesData, zonesData] = await Promise.all([
        adminService.platformListCities(),
        adminService.surgeListZones(),
      ]);
      setCities(citiesData);
      setZones(zonesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadZones = async (cityId) => {
    try {
      const data = await adminService.surgeListZones(cityId || null);
      setZones(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // ---------- filter ----------
  const filteredZones = zones.filter((z) => {
    if (filterCity && String(z.city_id) !== String(filterCity)) return false;
    if (searchName && !z.name?.toLowerCase().includes(searchName.toLowerCase())) return false;
    return true;
  });

  const handleCityFilter = (cityId) => {
    setFilterCity(cityId);
    loadZones(cityId);
  };

  // ---------- create ----------
  const openCreate = () => {
    setEditingZone(null);
    setForm({ ...emptyForm, city_id: filterCity || '' });
    setFormError('');
    setShowCreateModal(true);
  };

  const validateForm = () => {
    if (!form.city_id) return 'City is required';
    if (!form.name?.trim()) return 'Name is required';
    const m = parseFloat(form.multiplier);
    if (isNaN(m) || m < 1.0 || m > 5.0) return 'Multiplier must be between 1.0 and 5.0';
    if (!form.starts_at) return 'Start time is required';
    if (!form.ends_at) return 'End time is required';
    if (new Date(form.ends_at) <= new Date(form.starts_at)) return 'End time must be after start time';
    if (!form.boundary_geojson) return 'You must draw a polygon on the map';
    return null;
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    const err = validateForm();
    if (err) { setFormError(err); return; }

    try {
      setSubmitting(true);
      setFormError('');
      await adminService.surgeCreateZone({
        city_id: Number(form.city_id),
        name: form.name.trim(),
        multiplier: parseFloat(form.multiplier),
        starts_at: new Date(form.starts_at).toISOString(),
        ends_at: new Date(form.ends_at).toISOString(),
        boundary_geojson: form.boundary_geojson,
        is_active: form.is_active,
      });
      setShowCreateModal(false);
      showToast('Surge zone created successfully');
      loadZones(filterCity);
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // ---------- edit ----------
  const openEdit = (zone) => {
    setEditingZone(zone);
    setForm({
      city_id: zone.city_id,
      name: zone.name || '',
      multiplier: zone.multiplier,
      starts_at: toLocalDT(zone.starts_at),
      ends_at: toLocalDT(zone.ends_at),
      boundary_geojson: zone.boundary_geojson,
      is_active: zone.is_active,
    });
    setFormError('');
    setShowEditModal(true);
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    const err = validateForm();
    if (err) { setFormError(err); return; }

    try {
      setSubmitting(true);
      setFormError('');
      await adminService.surgeUpdateZone(editingZone.surge_zone_id, {
        name: form.name.trim(),
        multiplier: parseFloat(form.multiplier),
        starts_at: new Date(form.starts_at).toISOString(),
        ends_at: new Date(form.ends_at).toISOString(),
        boundary_geojson: form.boundary_geojson,
        is_active: form.is_active,
      });
      setShowEditModal(false);
      setEditingZone(null);
      showToast('Surge zone updated successfully');
      loadZones(filterCity);
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // ---------- activate / deactivate ----------
  const handleToggleActive = async (zone) => {
    const newActive = !zone.is_active;
    // Optimistic update
    setZones((prev) =>
      prev.map((z) => (z.surge_zone_id === zone.surge_zone_id ? { ...z, is_active: newActive } : z))
    );
    try {
      await adminService.surgeActivateZone(zone.surge_zone_id, newActive);
      showToast(`Surge zone ${newActive ? 'activated' : 'deactivated'}`);
    } catch (err) {
      // Revert on failure
      setZones((prev) =>
        prev.map((z) => (z.surge_zone_id === zone.surge_zone_id ? { ...z, is_active: zone.is_active } : z))
      );
      setError(err.message);
    }
  };

  // ---------- delete ----------
  const handleDelete = async (zone) => {
    if (!window.confirm(`Are you sure you want to delete surge zone "${zone.name}"?`)) return;
    try {
      await adminService.surgeDeleteZone(zone.surge_zone_id);
      showToast('Surge zone deleted');
      loadZones(filterCity);
    } catch (err) {
      setError(err.message);
    }
  };

  // ---------- helpers ----------
  const getCityName = (cityId) => {
    const city = cities.find((c) => c.city_id === cityId);
    return city?.name || cityId;
  };

  const getCityBoundary = (cityId) => {
    const city = cities.find((c) => String(c.city_id) === String(cityId));
    return city?.boundary_geojson || null;
  };

  const fmt = (dt) => (dt ? new Date(dt).toLocaleString() : '—');

  // ---------- render ----------
  if (loading) return <div className="loading">Loading surge zones...</div>;

  const renderForm = (onSubmit, isEdit) => (
    <form onSubmit={onSubmit}>
      {formError && <div className="form-error">{formError}</div>}

      <div className="form-group">
        <label>City *</label>
        <select
          value={form.city_id}
          onChange={(e) => setForm({ ...form, city_id: e.target.value })}
          required
          disabled={isEdit}
        >
          <option value="">Select City</option>
          {cities.map((c) => (
            <option key={c.city_id} value={c.city_id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Surge Name *</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          maxLength={120}
          placeholder="e.g., Evening Peak, Stadium Event"
          required
        />
      </div>

      <div className="form-group">
        <label>Multiplier * <span className="hint">(1.0 – 5.0)</span></label>
        <input
          type="number"
          min="1.0"
          max="5.0"
          step="0.1"
          value={form.multiplier}
          onChange={(e) => setForm({ ...form, multiplier: e.target.value })}
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Start Time *</label>
          <input
            type="datetime-local"
            value={form.starts_at}
            onChange={(e) => setForm({ ...form, starts_at: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>End Time *</label>
          <input
            type="datetime-local"
            value={form.ends_at}
            onChange={(e) => setForm({ ...form, ends_at: e.target.value })}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label>Surge Boundary (Draw Polygon) *</label>
        <SurgeMapSelector
          key={isEdit ? `edit-${editingZone?.surge_zone_id}` : 'create'}
          initialGeoJson={form.boundary_geojson}
          onPolygonChange={(geoJson) => setForm({ ...form, boundary_geojson: geoJson })}
          cityBoundary={getCityBoundary(form.city_id)}
          height={350}
        />
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          Activate Immediately
        </label>
      </div>

      <div className="modal-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => { setShowCreateModal(false); setShowEditModal(false); setEditingZone(null); }}
        >
          Cancel
        </button>
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? 'Saving...' : isEdit ? 'Update Surge Zone' : 'Create Surge Zone'}
        </button>
      </div>
    </form>
  );

  return (
    <div className="surge-container">
      {toast && <div className="success-toast">{toast}</div>}

      {/* Header */}
      <div className="surge-header">
        <h1>⚡ Surge Zone Management</h1>
        <button className="btn-primary" onClick={openCreate}>+ Create Surge Zone</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Filters */}
      <div className="filters-row">
        <div className="filter-group">
          <label>City</label>
          <select value={filterCity} onChange={(e) => handleCityFilter(e.target.value)}>
            <option value="">All Cities</option>
            {cities.map((c) => (
              <option key={c.city_id} value={c.city_id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Search</label>
          <input
            type="text"
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
            placeholder="Search by name..."
          />
        </div>
      </div>

      {/* Table */}
      {filteredZones.length === 0 ? (
        <div className="empty-state">
          <p>No surge zones found</p>
          <button className="btn-primary" onClick={openCreate}>Create Surge Zone</button>
        </div>
      ) : (
        <div className="admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>City</th>
                <th>Multiplier</th>
                <th>Time Window</th>
                <th>Status</th>
                <th>Map</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredZones.map((z) => {
                const zoneStatus = getStatus(z);
                return (
                  <tr key={z.surge_zone_id}>
                    <td><strong>{z.name || '(Unnamed)'}</strong></td>
                    <td>{getCityName(z.city_id)}</td>
                    <td>
                      <span className="multiplier-badge">{Number(z.multiplier).toFixed(1)}x</span>
                    </td>
                    <td>
                      <div className="time-window">
                        <div>{fmt(z.starts_at)}</div>
                        <div className="time-separator">→</div>
                        <div>{fmt(z.ends_at)}</div>
                      </div>
                    </td>
                    <td>{statusBadge(zoneStatus)}</td>
                    <td>
                      <button
                        className="btn-action btn-map"
                        onClick={() => setShowMapPreview(z)}
                        title="View on map"
                      >
                        🗺️
                      </button>
                    </td>
                    <td className="actions-cell">
                      <button className="btn-action btn-edit" onClick={() => openEdit(z)}>Edit</button>
                      <button
                        className={`btn-action ${z.is_active ? 'btn-deactivate' : 'btn-activate'}`}
                        onClick={() => handleToggleActive(z)}
                      >
                        {z.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button className="btn-action btn-delete" onClick={() => handleDelete(z)}>Delete</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content surge-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create Surge Zone</h2>
            {renderForm(handleCreate, false)}
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <div className="modal-overlay" onClick={() => { setShowEditModal(false); setEditingZone(null); }}>
          <div className="modal-content surge-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Edit Surge Zone</h2>
            {renderForm(handleEdit, true)}
          </div>
        </div>
      )}

      {/* Map Preview Modal */}
      {showMapPreview && (
        <div className="modal-overlay" onClick={() => setShowMapPreview(null)}>
          <div className="modal-content surge-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Surge Zone: {showMapPreview.name}</h2>
            <div style={{ marginBottom: 12 }}>
              <strong>Multiplier:</strong> {Number(showMapPreview.multiplier).toFixed(1)}x &nbsp;|&nbsp;
              <strong>Status:</strong> {statusBadge(getStatus(showMapPreview))}
            </div>
            <SurgeMapSelector
              key={`preview-${showMapPreview.surge_zone_id}`}
              initialGeoJson={showMapPreview.boundary_geojson}
              cityBoundary={getCityBoundary(showMapPreview.city_id)}
              height={400}
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowMapPreview(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SurgeZones;
