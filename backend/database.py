from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from datetime import datetime
import os

# Read DB config from environment with sensible defaults
DB_USER = os.getenv("DB_USER", "username")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "fake_wifi_detector")

# Allow a full DATABASE_URL override (recommended for production)
# Default to local SQLite to avoid external DB setup during development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db",
)

# Engine with pool_pre_ping to avoid stale connections
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NetworkScan(Base):
    __tablename__ = "network_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    ssid = Column(String(255), nullable=False)
    signal_strength = Column(Integer)
    security_type = Column(String(50))
    risk_score = Column(Float)
    is_suspicious = Column(Boolean, default=False)
    detection_reason = Column(Text)
    scan_timestamp = Column(DateTime, default=datetime.utcnow)

class ScanHistory(Base):
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_timestamp = Column(DateTime, default=datetime.utcnow)
    networks_found = Column(Integer)
    suspicious_count = Column(Integer)
    average_risk = Column(Float)

class FakeWifi(Base):
    __tablename__ = "fake_access_points"

    id = Column(Integer, primary_key=True, index=True)
    ssid = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    mac_address = Column(String(17), unique=True)  # MAC addresses are 17 chars (e.g., "00:11:22:33:44:55")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def test_connection():
    """Quickly test DB connectivity. Returns True on success, False on failure.

    This attempts a trivial query (SELECT 1). Useful to verify the DB is reachable
    and credentials are correct.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError as e:
        # OperationalError is common for connectivity/auth issues
        print(f"OperationalError when connecting to DB: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error when testing DB connection: {e}")
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Simple CLI test: runs when this file is executed directly
    ok = test_connection()
    if ok:
        print("DB connection OK")
    else:
        print("DB connection FAILED")