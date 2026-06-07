from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, func
from database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_post_id = Column(Integer, ForeignKey("mentorship_posts.id"), nullable=True)
    request_post_id = Column(Integer, ForeignKey("mentorship_posts.id"), nullable=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    score = Column(Numeric(5, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Match id={self.id} mentor_id={self.mentor_id} mentee_id={self.mentee_id} score={self.score}>"