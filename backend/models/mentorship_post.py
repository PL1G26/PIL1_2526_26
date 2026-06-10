from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, func
from database import Base


class MentorshipPost(Base):
    __tablename__ = "mentorship_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(10), nullable=False)  # 'offer' or 'request'
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    mode = Column(String(10), nullable=False)  # 'online', 'offline', 'both'
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MentorshipPost id={self.id} type={self.type} skill_id={self.skill_id}>"