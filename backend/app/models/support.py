from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP, Numeric
from .base import Base
from .mixins import AuditMixin, GeoMixin

class SOSEvent(Base, AuditMixin, GeoMixin):
    __tablename__ = "sos_event"

    sos_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"), nullable=False)
    triggered_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    triggered_at = Column(TIMESTAMP(timezone=True), nullable=False)
    resolved_at = Column(TIMESTAMP(timezone=True))


class SupportTicket(Base, AuditMixin):
    __tablename__ = "support_ticket"

    ticket_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))
    sos_id = Column(BigInteger, ForeignKey("sos_event.sos_id"))

    issue_type = Column(String(100))
    severity = Column(String(20))
    status = Column(String, ForeignKey("lu_support_ticket_status.status_code"), nullable=False)

    assigned_to = Column(BigInteger, ForeignKey("app_user.user_id"))
    assigned_at = Column(TIMESTAMP(timezone=True))


class SupportTicketConversation(Base, AuditMixin):
    __tablename__ = "support_ticket_conversation"

    message_id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("support_ticket.ticket_id"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    message_text = Column(String, nullable=False)
    sent_at = Column(TIMESTAMP(timezone=True), nullable=False)


class SupportTicketAssignmentHistory(Base, AuditMixin):
    __tablename__ = "support_ticket_assignment_history"

    history_id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("support_ticket.ticket_id"), nullable=False)
    assigned_to = Column(BigInteger, ForeignKey("app_user.user_id"))

    assigned_at = Column(TIMESTAMP(timezone=True), nullable=False)
    unassigned_at = Column(TIMESTAMP(timezone=True))


class LostItemReport(Base, AuditMixin):
    __tablename__ = "lost_item_report"

    report_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    description = Column(String, nullable=False)
    status = Column(String(50))
