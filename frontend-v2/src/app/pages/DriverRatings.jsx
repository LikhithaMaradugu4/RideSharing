import { useState, useEffect } from 'react';
import DriverLayout from '../layout/DriverLayout';
import StarRating from '../../components/StarRating';
import ratingService from '../../services/rating.service';
import driverService from '../../services/driver.service';
import Icons from '../../components/Icons';
import './DriverRatings.css';

function DriverRatings() {
  const [driverProfile, setDriverProfile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [feedbackData, setFeedbackData] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [error, setError] = useState(null);

  const LIMIT = 10;

  useEffect(() => {
    loadProfile();
  }, []);

  useEffect(() => {
    if (driverProfile) {
      loadData();
    }
  }, [driverProfile, page]);

  const loadProfile = async () => {
    try {
      const profile = await driverService.getMyProfile(null);
      setDriverProfile(profile);
    } catch (err) {
      setError('Failed to load driver profile');
    }
  };

  const loadData = async () => {
    try {
      if (page === 1) setLoading(true);
      else setFeedbackLoading(true);

      const [summaryRes, feedbackRes] = await Promise.all([
        page === 1 ? ratingService.getRatingSummary('me') : Promise.resolve(summary),
        ratingService.getFeedbackList('me', page, LIMIT),
      ]);

      if (page === 1) setSummary(summaryRes);
      setFeedbackData(feedbackRes);
    } catch (err) {
      setError('Failed to load ratings data');
    } finally {
      setLoading(false);
      setFeedbackLoading(false);
    }
  };

  const totalPages = feedbackData ? Math.ceil(feedbackData.total / LIMIT) : 0;

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const renderStars = (count) => {
    return (
      <span style={{ display: 'inline-flex', gap: '2px' }}>
        {[1, 2, 3, 4, 5].map((s) => (
          <span key={s}>
            {s <= count
              ? <Icons.StarFilled size={16} color="#fbbf24" />
              : <Icons.Star size={16} color="#d1d5db" />}
          </span>
        ))}
      </span>
    );
  };

  if (!driverProfile || driverProfile.approval_status !== 'APPROVED') {
    return null;
  }

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="driver-ratings-page">
        <h1 className="page-title">
          <Icons.StarFilled size={24} color="#fbbf24" style={{ verticalAlign: 'middle', marginRight: '8px' }} />
          Ratings &amp; Feedback
        </h1>

        {error && (
          <div className="error-banner">
            <Icons.Warning size={16} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
            {error}
            <button onClick={() => setError(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', fontWeight: '700' }}>×</button>
          </div>
        )}

        {loading ? (
          <div className="loading-state">Loading ratings...</div>
        ) : (
          <>
            {/* ── Summary Card ───────────────────────────── */}
            {summary && (
              <div className="summary-card">
                <div className="summary-left">
                  <div className="big-rating">
                    {summary.average_rating.toFixed(1)}
                  </div>
                  <StarRating value={Math.round(summary.average_rating)} readOnly size={28} />
                  <div className="total-count">
                    {summary.total_ratings} rating{summary.total_ratings !== 1 ? 's' : ''}
                  </div>
                </div>

                <div className="summary-right">
                  {[5, 4, 3, 2, 1].map((star) => {
                    const count = summary.breakdown[String(star)] || 0;
                    const pct = summary.total_ratings > 0
                      ? (count / summary.total_ratings) * 100
                      : 0;
                    return (
                      <div className="breakdown-row" key={star}>
                        <span className="breakdown-label">{star}★</span>
                        <div className="breakdown-bar-bg">
                          <div
                            className="breakdown-bar-fill"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="breakdown-count">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ── Feedback List ──────────────────────────── */}
            <h2 className="section-title">Recent Feedback</h2>

            {feedbackLoading ? (
              <div className="loading-state">Loading feedback...</div>
            ) : feedbackData && feedbackData.items.length > 0 ? (
              <>
                <div className="feedback-list">
                  {feedbackData.items.map((item, idx) => (
                    <div className="feedback-card" key={idx}>
                      <div className="feedback-header">
                        {renderStars(item.rating)}
                        <span className="feedback-rating-num">{item.rating}.0</span>
                        <span className="feedback-role">
                          {item.rater_role === 'RIDER' ? 'From Rider' : 'From Driver'}
                        </span>
                      </div>
                      {item.feedback && (
                        <p className="feedback-text">"{item.feedback}"</p>
                      )}
                      <div className="feedback-meta">
                        <span className="feedback-date">{formatDate(item.created_at)}</span>
                        <span className="feedback-trip">Trip #{item.trip_id}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="pagination">
                    <button
                      disabled={page <= 1}
                      onClick={() => setPage((p) => p - 1)}
                      className="page-btn"
                    >
                      ← Prev
                    </button>
                    <span className="page-info">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      disabled={page >= totalPages}
                      onClick={() => setPage((p) => p + 1)}
                      className="page-btn"
                    >
                      Next →
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="empty-state">
                <Icons.Star size={48} color="#d1d5db" />
                <p>No feedback received yet</p>
              </div>
            )}
          </>
        )}
      </div>
    </DriverLayout>
  );
}

export default DriverRatings;
