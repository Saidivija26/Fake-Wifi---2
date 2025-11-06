from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NetworkBase(BaseModel):
    ssid: str
    signal_strength: int
    security_type: str
    risk_score: float
    is_suspicious: bool
    detection_reason: str

class NetworkCreate(NetworkBase):
    pass

class Network(NetworkBase):
    id: int
    scan_timestamp: datetime
    
    class Config:
        from_attributes = True

class FakeNetworkCreate(BaseModel):
    ssid: str
    security_type: str
    signal_strength: int

class ScanHistory(BaseModel):
    id: int
    scan_timestamp: datetime
    networks_found: int
    suspicious_count: int
    average_risk: float
    
    class Config:
        from_attributes = True