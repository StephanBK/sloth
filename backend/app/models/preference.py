"""
User Preferences Model

LEARNING NOTE:
This tracks which meal plans users like or dislike.
Over time, the app learns to suggest plans the user will enjoy
and hide the ones they don't like.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class PreferenceType(str, enum.Enum):
    """User's opinion of a meal plan"""
    LIKED = "liked"
    DISLIKED = "disliked"
    NEUTRAL = "neutral"


class UserPreference(Base):
    """
    User's preference (like/dislike) for a specific meal plan.

    LEARNING NOTE:
    The UniqueConstraint ensures a user can only have ONE preference
    per meal plan. If they change their mind, we update the existing record.
    """
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    meal_plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    preference: Mapped[PreferenceType] = mapped_column(
        SQLEnum(PreferenceType),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # CONSTRAINT: One preference per user per meal plan
    __table_args__ = (
        UniqueConstraint('user_id', 'meal_plan_id', name='uq_user_meal_preference'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreference user={self.user_id[:8]} plan={self.meal_plan_id[:8]} {self.preference.value}>"
