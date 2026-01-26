import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import profileService from '../../services/profile.service';
import './Profile.css';

function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    gender: '',
    city_id: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('jwt_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        navigate('/login');
        return;
      }

      const data = await profileService.getProfile(token);
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        gender: data.gender || '',
        city_id: data.city_id || ''
      });
    } catch (err) {
      setError(err.message || 'Failed to load profile');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    try {
      setError(null);
      setSuccess(null);

      const token = localStorage.getItem('jwt_token');
      const updateData = {
        full_name: formData.full_name,
        gender: formData.gender,
        city_id: formData.city_id ? parseInt(formData.city_id) : null
      };

      const data = await profileService.updateProfile(token, updateData);
      setProfile(data);
      setIsEditing(false);
      setSuccess('Profile updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      console.error('Error:', err);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      full_name: profile?.full_name || '',
      gender: profile?.gender || '',
      city_id: profile?.city_id || ''
    });
  };

  if (loading) {
    return <div className="profile-container"><p>Loading profile...</p></div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h1>My Profile</h1>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {profile && (
          <div className="profile-form">
            {!isEditing ? (
              <div className="profile-view">
                <div className="profile-field">
                  <label>Full Name</label>
                  <p>{profile.full_name}</p>
                </div>
                <div className="profile-field">
                  <label>Phone</label>
                  <p>{profile.phone}</p>
                </div>
                <div className="profile-field">
                  <label>Gender</label>
                  <p>{profile.gender || 'Not specified'}</p>
                </div>
                <div className="profile-field">
                  <label>City ID</label>
                  <p>{profile.city_id || 'Not specified'}</p>
                </div>
                <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                  Edit Profile
                </button>
              </div>
            ) : (
              <div className="profile-edit">
                <div className="form-group">
                  <label htmlFor="full_name">Full Name *</label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="gender">Gender</label>
                  <select
                    id="gender"
                    name="gender"
                    value={formData.gender}
                    onChange={handleInputChange}
                  >
                    <option value="">Select Gender</option>
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="city_id">City ID</label>
                  <input
                    type="number"
                    id="city_id"
                    name="city_id"
                    value={formData.city_id}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="button-group">
                  <button className="btn btn-primary" onClick={handleSave}>
                    Save
                  </button>
                  <button className="btn btn-secondary" onClick={handleCancel}>
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
