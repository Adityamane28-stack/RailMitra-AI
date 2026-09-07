from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.services.database import Base


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)

    # Passenger account information
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    # Passenger personal information
    passenger_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

    # Account creation time
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )