from app.services.database import engine, Base
from app.models.complaint import Complaint

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")