"""
Weight Tracking Model

LEARNING NOTE:
This tracks the user's daily weight entries for progress visualization.
The Faultierdiät uses weight stalls (2+ weeks no progress) to signal
when to drop to the next level.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class WeightEntry(Base):
    """
    A single weight measurement.

    Users log their weight (ideally daily, same time each day).
    The app uses this to:
    - Show progress graphs
    - Detect stalls (no progress for 2+ weeks)
    - Suggest level drops
    """
    __tablename__ = "weight_entries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Which user this belongs to
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for fast user lookups
    )

    # The weight in kg
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)

    # When the measurement was taken (user-provided date)
    # LEARNING NOTE: We use Date (not DateTime) since we only care about the day
    measured_at: Mapped[date] = mapped_column(Date, nullable=False)

    # Optional notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # When this record was created in our system
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship back to user
    user: Mapped["User"] = relationship("User", back_populates="weight_entries")

    def __repr__(self) -> str:
        return f"<WeightEntry {self.weight_kg}kg on {self.measured_at}>"
