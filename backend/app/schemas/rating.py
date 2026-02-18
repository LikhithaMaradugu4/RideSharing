"""
Pydantic schemas for trip ratings and feedback.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
from datetime import datetime


class SubmitRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, max_length=500, description="Optional feedback text")

    @validator('feedback')
    def sanitize_feedback(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 500:
                raise ValueError('Feedback must be 500 characters or less')
        return v


class SubmitRatingResponse(BaseModel):
    message: str
    rating_id: int
    trip_id: int
    rating: int
    role_type: str


class RatingSummaryResponse(BaseModel):
    average_rating: float
    total_ratings: int
    breakdown: Dict[str, int]  # {"5": 60, "4": 12, ...}


class FeedbackItem(BaseModel):
    rating: int
    feedback: Optional[str]
    trip_id: int
    created_at: datetime
    rater_role: Optional[str] = None


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItem]
    total: int
    page: int
    limit: int


class TripRatingStatus(BaseModel):
    """Whether the current user has already rated this trip."""
    can_rate: bool
    has_rated: bool
    trip_id: int
    reason: Optional[str] = None
