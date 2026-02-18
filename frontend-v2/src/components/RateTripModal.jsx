import { useState } from 'react';
import StarRating from './StarRating';
import ratingService from '../services/rating.service';
import Icons from './Icons';

/**
 * Modal overlay for rating a trip after payment completion.
 *
 * Props:
 *   tripId    – the trip to rate
 *   onClose   – close callback
 *   onSuccess – called after successful submission
 */
function RateTripModal({ tripId, onClose, onSuccess }) {
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }
    try {
      setSubmitting(true);
      setError(null);
      await ratingService.submitRating(tripId, rating, feedback || null);
      setSubmitted(true);
      onSuccess?.();
    } catch (err) {
      setError(err.message || 'Failed to submit rating');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '16px',
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '32px 28px',
        maxWidth: '420px',
        width: '100%',
        textAlign: 'center',
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
      }}>
        {submitted ? (
          /* ── Success State ────────────────────────── */
          <>
            <div style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
            }}>
              <Icons.CheckCircle size={36} color="white" />
            </div>

            <h2 style={{ margin: '0 0 8px', fontSize: '22px', color: '#1f2937' }}>
              Rating Submitted!
            </h2>

            <p style={{ margin: '0 0 24px', color: '#6b7280', fontSize: '14px' }}>
              Thank you for your feedback
            </p>

            <button
              onClick={onClose}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
              }}
            >
              Done
            </button>
          </>
        ) : (
          /* ── Rating Form ──────────────────────────── */
          <>
            <div style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
            }}>
              <Icons.StarFilled size={36} color="white" />
            </div>

            <h2 style={{ margin: '0 0 8px', fontSize: '22px', color: '#1f2937' }}>
              Rate Your Experience
            </h2>

            <p style={{ margin: '0 0 24px', color: '#6b7280', fontSize: '14px' }}>
              How was your trip?
            </p>

            {/* Star Selector */}
            <div style={{ marginBottom: '20px' }}>
              <StarRating value={rating} onChange={setRating} size={40} />
              {rating > 0 && (
                <div style={{ marginTop: '8px', color: '#6b7280', fontSize: '13px' }}>
                  {rating === 5 && 'Excellent!'}
                  {rating === 4 && 'Great!'}
                  {rating === 3 && 'Good'}
                  {rating === 2 && 'Fair'}
                  {rating === 1 && 'Poor'}
                </div>
              )}
            </div>

            {/* Feedback Textarea */}
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Share your experience (optional, max 500 chars)"
              maxLength={500}
              rows={3}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '10px',
                border: '1px solid #e2e8f0',
                fontSize: '14px',
                resize: 'vertical',
                fontFamily: 'inherit',
                marginBottom: '4px',
                boxSizing: 'border-box',
              }}
            />
            <div style={{ textAlign: 'right', fontSize: '12px', color: '#94a3b8', marginBottom: '16px' }}>
              {feedback.length}/500
            </div>

            {error && (
              <div style={{
                background: '#fef2f2',
                color: '#dc2626',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                marginBottom: '16px',
              }}>
                {error}
              </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={onClose}
                style={{
                  flex: 1,
                  padding: '14px',
                  background: '#f1f5f9',
                  color: '#64748b',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                Skip
              </button>

              <button
                onClick={handleSubmit}
                disabled={submitting || rating === 0}
                style={{
                  flex: 2,
                  padding: '14px',
                  background: rating === 0
                    ? '#e2e8f0'
                    : 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                  color: rating === 0 ? '#94a3b8' : 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontWeight: '600',
                  cursor: rating === 0 ? 'not-allowed' : 'pointer',
                  opacity: submitting ? 0.7 : 1,
                }}
              >
                {submitting ? 'Submitting...' : 'Submit Rating'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default RateTripModal;
