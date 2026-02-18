"""
Rating API Router — v2 endpoints for trip ratings and feedback.

Endpoints:
  POST /trips/{trip_id}/rate        — Submit a rating
  GET  /trips/{trip_id}/rating-status — Check if user can rate
  GET  /users/{user_id}/rating-summary — Rating summary for a user
  GET  /users/{user_id}/feedback     — Paginated feedback list
  GET  /users/me/rating-summary      — Current user's own rating summary
  GET  /users/me/feedback            — Current user's own feedback list
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.schemas.rating import (
    SubmitRatingRequest,
    SubmitRatingResponse,
    RatingSummaryResponse,
    FeedbackListResponse,
    TripRatingStatus,
)
from app.services.rating_service import RatingService

router = APIRouter(tags=["ratings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Submit Rating ──────────────────────────────────────────────────────────

@router.post("/trips/{trip_id}/rate", response_model=SubmitRatingResponse)
def submit_rating(
    trip_id: int,
    body: SubmitRatingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submit a 1–5 star rating with optional feedback for a completed trip."""
    user_id = current_user.get("user_id")

    new_rating = RatingService.submit_rating(
        db=db,
        trip_id=trip_id,
        rater_user_id=user_id,
        rating=body.rating,
        feedback=body.feedback,
    )

    return SubmitRatingResponse(
        message="Rating submitted successfully",
        rating_id=new_rating.id,
        trip_id=new_rating.trip_id,
        rating=new_rating.rating,
        role_type=new_rating.role_type,
    )


# ─── Rating eligibility check ──────────────────────────────────────────────

@router.get("/trips/{trip_id}/rating-status", response_model=TripRatingStatus)
def get_rating_status(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Check whether the current user can rate a particular trip."""
    user_id = current_user.get("user_id")
    return RatingService.get_rating_status(db, trip_id, user_id)


# ─── User Rating Summary ───────────────────────────────────────────────────

@router.get("/users/me/rating-summary", response_model=RatingSummaryResponse)
def get_my_rating_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get rating summary for the currently authenticated user."""
    user_id = current_user.get("user_id")
    return RatingService.get_rating_summary(db, user_id)


@router.get("/users/{user_id}/rating-summary", response_model=RatingSummaryResponse)
def get_user_rating_summary(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    """Get rating summary for any user (public-ish, requires auth)."""
    return RatingService.get_rating_summary(db, user_id)


# ─── Feedback List ──────────────────────────────────────────────────────────

@router.get("/users/me/feedback", response_model=FeedbackListResponse)
def get_my_feedback(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get paginated feedback list for the current user."""
    user_id = current_user.get("user_id")
    return RatingService.get_feedback_list(db, user_id, page, limit)


@router.get("/users/{user_id}/feedback", response_model=FeedbackListResponse)
def get_user_feedback(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    """Get paginated feedback list for any user (requires auth)."""
    return RatingService.get_feedback_list(db, user_id, page, limit)
