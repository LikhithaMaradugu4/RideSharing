"""
Rating Service — business logic for trip ratings and feedback.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.ratings import TripRating, DriverRatingSummary, RiderRatingSummary
from app.models.trips import Trip


class RatingService:

    @staticmethod
    def submit_rating(
        db: Session,
        trip_id: int,
        rater_user_id: int,
        rating: int,
        feedback: str | None = None,
    ) -> TripRating:
        """
        Submit a rating for a completed & fully-settled trip.

        Validates:
          - Trip exists and status == COMPLETED (or PAID)
          - payment_status is SUCCESS / PAID
          - settlement_status is settled / SUCCESS
          - Rater is either the rider or driver of the trip
          - Rater is not rating themselves
          - Rating does not already exist
        """

        # 1. Fetch trip
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        # 2. Validate trip is completed
        if trip.status not in ("COMPLETED", "PAID"):
            raise HTTPException(
                status_code=400,
                detail="Rating is only allowed after trip completion",
            )

        # 3. Validate rider payment
        payment_ok = (trip.payment_status or "").upper() in (
            "SUCCESS", "PAID", "COMPLETED",
        )
        if not payment_ok:
            raise HTTPException(
                status_code=400,
                detail="Rating is only allowed after successful rider payment",
            )

        # 4. Validate driver settlement
        settlement_ok = (trip.settlement_status or "").lower() in (
            "settled", "success", "completed",
        )
        if not settlement_ok:
            raise HTTPException(
                status_code=400,
                detail="Rating is only allowed after driver settlement is complete",
            )

        # 5. Rater must be rider or driver of the trip
        if rater_user_id == trip.rider_id:
            rated_user_id = trip.driver_id
            role_type = "RIDER"
        elif rater_user_id == trip.driver_id:
            rated_user_id = trip.rider_id
            role_type = "DRIVER"
        else:
            raise HTTPException(
                status_code=403,
                detail="Only the rider or driver of this trip can submit a rating",
            )

        # 6. Cannot rate yourself
        if rater_user_id == rated_user_id:
            raise HTTPException(
                status_code=400, detail="Cannot rate yourself"
            )

        # 7. Prevent duplicate
        existing = (
            db.query(TripRating)
            .filter(
                TripRating.trip_id == trip_id,
                TripRating.rater_user_id == rater_user_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="You have already rated this trip",
            )

        # 8. Insert rating
        new_rating = TripRating(
            trip_id=trip_id,
            rater_user_id=rater_user_id,
            rated_user_id=rated_user_id,
            rating=rating,
            feedback=feedback,
            role_type=role_type,
        )
        db.add(new_rating)
        db.flush()

        # 9. Update summary table
        RatingService._update_summary(db, rated_user_id, role_type)

        db.commit()
        db.refresh(new_rating)
        return new_rating

    # ------------------------------------------------------------------
    # Rating summary
    # ------------------------------------------------------------------

    @staticmethod
    def get_rating_summary(db: Session, user_id: int) -> dict:
        """Return average rating, total count, and star breakdown for a user."""

        # Aggregate from trip_ratings where rated_user_id = user_id
        total = (
            db.query(func.count(TripRating.id))
            .filter(TripRating.rated_user_id == user_id)
            .scalar()
        ) or 0

        avg = (
            db.query(func.avg(TripRating.rating))
            .filter(TripRating.rated_user_id == user_id)
            .scalar()
        )
        avg = round(float(avg), 2) if avg else 0.0

        # Breakdown
        rows = (
            db.query(TripRating.rating, func.count(TripRating.id))
            .filter(TripRating.rated_user_id == user_id)
            .group_by(TripRating.rating)
            .all()
        )
        breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for star, count in rows:
            breakdown[str(star)] = count

        return {
            "average_rating": avg,
            "total_ratings": total,
            "breakdown": breakdown,
        }

    # ------------------------------------------------------------------
    # Feedback list (paginated)
    # ------------------------------------------------------------------

    @staticmethod
    def get_feedback_list(
        db: Session, user_id: int, page: int = 1, limit: int = 10
    ) -> dict:
        """Return paginated feedback for a user (newest first)."""

        query = (
            db.query(TripRating)
            .filter(TripRating.rated_user_id == user_id)
            .order_by(TripRating.created_at.desc())
        )

        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "items": [
                {
                    "rating": r.rating,
                    "feedback": r.feedback,
                    "trip_id": r.trip_id,
                    "created_at": r.created_at,
                    "rater_role": r.role_type,
                }
                for r in items
            ],
            "total": total,
            "page": page,
            "limit": limit,
        }

    # ------------------------------------------------------------------
    # Check if user can still rate a trip
    # ------------------------------------------------------------------

    @staticmethod
    def get_rating_status(db: Session, trip_id: int, user_id: int) -> dict:
        """Check if a user can rate a specific trip."""

        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            return {"can_rate": False, "has_rated": False, "trip_id": trip_id, "reason": "Trip not found"}

        # Must be participant
        if user_id not in (trip.rider_id, trip.driver_id):
            return {"can_rate": False, "has_rated": False, "trip_id": trip_id, "reason": "Not a participant"}

        # Must be completed
        if trip.status not in ("COMPLETED", "PAID"):
            return {"can_rate": False, "has_rated": False, "trip_id": trip_id, "reason": "Trip not completed"}

        # Payment must be successful
        payment_ok = (trip.payment_status or "").upper() in ("SUCCESS", "PAID", "COMPLETED")
        if not payment_ok:
            return {"can_rate": False, "has_rated": False, "trip_id": trip_id, "reason": "Payment not completed"}

        # Settlement must be done
        settlement_ok = (trip.settlement_status or "").lower() in ("settled", "success", "completed")
        if not settlement_ok:
            return {"can_rate": False, "has_rated": False, "trip_id": trip_id, "reason": "Settlement pending"}

        # Already rated?
        existing = (
            db.query(TripRating)
            .filter(TripRating.trip_id == trip_id, TripRating.rater_user_id == user_id)
            .first()
        )
        if existing:
            return {"can_rate": False, "has_rated": True, "trip_id": trip_id, "reason": "Already rated"}

        return {"can_rate": True, "has_rated": False, "trip_id": trip_id, "reason": None}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _update_summary(db: Session, rated_user_id: int, rater_role_type: str):
        """
        Incrementally update the summary table after a new rating.
        rater_role_type tells us WHO rated — if RIDER rated, update DriverRatingSummary;
        if DRIVER rated, update RiderRatingSummary.
        """

        # Compute fresh aggregates (simple & safe)
        agg = (
            db.query(
                func.avg(TripRating.rating),
                func.count(TripRating.id),
            )
            .filter(TripRating.rated_user_id == rated_user_id)
            .first()
        )
        avg_val = round(float(agg[0]), 2) if agg[0] else 0
        total_val = agg[1] or 0

        if rater_role_type == "RIDER":
            # Rider rated → driver was rated
            summary = (
                db.query(DriverRatingSummary)
                .filter(DriverRatingSummary.driver_id == rated_user_id)
                .first()
            )
            if summary:
                summary.avg_rating = avg_val
                summary.total_ratings = total_val
            else:
                db.add(DriverRatingSummary(
                    driver_id=rated_user_id,
                    avg_rating=avg_val,
                    total_ratings=total_val,
                ))
        elif rater_role_type == "DRIVER":
            # Driver rated → rider was rated
            summary = (
                db.query(RiderRatingSummary)
                .filter(RiderRatingSummary.rider_id == rated_user_id)
                .first()
            )
            if summary:
                summary.avg_rating = avg_val
                summary.total_ratings = total_val
            else:
                db.add(RiderRatingSummary(
                    rider_id=rated_user_id,
                    avg_rating=avg_val,
                    total_ratings=total_val,
                ))
