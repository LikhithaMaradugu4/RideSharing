import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './TenantDocuments.css';

const DOCUMENT_TYPES = [
  'Company Registration',
  'GST Certificate',
  'Partnership Agreement',
  'Operating License',
  'Tax ID',
  'Other'
];

const TenantDocuments = () => {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadData, setUploadData] = useState({
    document_type: 'Company Registration',
    file: null
  });

  useEffect(() => {
    loadDocuments();
  }, [tenantId]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await adminService.listTenantDocuments(tenantId);
      setDocuments(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setUploadData({
      ...uploadData,
      file: e.target.files[0]
    });
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadData.file) {
      setError('Please select a file');
      return;
    }

    setError('');
    setUploading(true);

    try {
      await adminService.uploadTenantDocument(
        tenantId,
        uploadData.document_type,
        uploadData.file
      );
      setShowUploadForm(false);
      setUploadData({ document_type: 'Company Registration', file: null });
      loadDocuments();
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (documentId, fileName) => {
    try {
      const { blob, filename } = await adminService.downloadTenantDocument(tenantId, documentId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message || 'Failed to download document');
    }
  };

  const handleDelete = async (documentId, fileName) => {
    if (!window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return;
    }

    try {
      await adminService.deleteTenantDocument(tenantId, documentId);
      loadDocuments();
    } catch (err) {
      alert(err.message || 'Failed to delete document');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Loading documents...</div>;
  }

  return (
    <div className="tenant-documents-container">
      <div className="documents-header">
        <h1>Tenant Documents</h1>
        <div className="header-actions">
          <button 
            className="btn-secondary"
            onClick={() => navigate(`/admin/platform/tenants/${tenantId}`)}
          >
            Back to Tenant
          </button>
          <button 
            className="btn-primary"
            onClick={() => setShowUploadForm(!showUploadForm)}
          >
            {showUploadForm ? 'Cancel Upload' : '+ Upload Document'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {showUploadForm && (
        <div className="upload-form-card">
          <h2>Upload New Document</h2>
          <form onSubmit={handleUpload}>
            <div className="form-group">
              <label htmlFor="document_type">Document Type *</label>
              <select
                id="document_type"
                value={uploadData.document_type}
                onChange={(e) => setUploadData({ ...uploadData, document_type: e.target.value })}
                disabled={uploading}
                required
              >
                {DOCUMENT_TYPES.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="file">Select File *</label>
              <input
                type="file"
                id="file"
                onChange={handleFileChange}
                disabled={uploading}
                required
              />
              {uploadData.file && (
                <div className="file-info">
                  Selected: <strong>{uploadData.file.name}</strong> ({(uploadData.file.size / 1024).toFixed(2)} KB)
                </div>
              )}
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                className="btn-cancel"
                onClick={() => {
                  setShowUploadForm(false);
                  setUploadData({ document_type: 'Company Registration', file: null });
                }}
                disabled={uploading}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn-submit"
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload Document'}
              </button>
            </div>
          </form>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="empty-state">
          <p>No documents uploaded yet</p>
          <button 
            className="btn-primary"
            onClick={() => setShowUploadForm(true)}
          >
            Upload First Document
          </button>
        </div>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <div key={doc.tenant_document_id} className="document-card">
              <div className="document-icon">📄</div>
              <div className="document-info">
                <h3 className="document-type">{doc.document_type}</h3>
                <p className="document-filename">{doc.file_name}</p>
                <p className="document-date">Uploaded: {formatDate(doc.created_on)}</p>
              </div>
              <div className="document-actions">
                <button
                  className="btn-action btn-download"
                  onClick={() => handleDownload(doc.tenant_document_id, doc.file_name)}
                >
                  Download
                </button>
                <button
                  className="btn-action btn-delete"
                  onClick={() => handleDelete(doc.tenant_document_id, doc.file_name)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TenantDocuments;
