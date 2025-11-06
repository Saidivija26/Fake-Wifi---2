from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NetworkScanBase(BaseModel):
    ssid: str
    signal_strength: Optional[int] = None
    security_type: Optional[str] = None
    risk_score: Optional[float] = None
    is_suspicious: Optional[bool] = False
    detection_reason: Optional[str] = None

    class Config:
        from_attributes = True

class NetworkScan(NetworkScanBase):
    id: int
    scan_timestamp: datetime

class ScanHistoryBase(BaseModel):
    networks_found: int
    suspicious_count: int
    average_risk: float

    class Config:
        from_attributes = True

class ScanHistory(ScanHistoryBase):
    id: int
    scan_timestamp: datetime

class FakeWifiBase(BaseModel):
    ssid: str
    password: Optional[str] = None

    class Config:
        from_attributes = True

class FakeWifi(FakeWifiBase):
    id: int
    mac_address: Optional[str] = None
    is_active: bool
    created_at: datetime
