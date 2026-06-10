from sqlalchemy import Column, Integer, String, DateTime, Text, func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    profile_photo = Column(Text, nullable=True)  # URL or Base64, NULL if no photo
    field_of_study = Column(String(50), nullable=False)  # IA, IM, GL, SE&IoT, SI
    level = Column(String(20), nullable=False)  # L1, L2, L3, M1, M2
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User id={self.id} name={self.first_name} {self.last_name}>"