from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, create_tables, NetworkScan, ScanHistory, FakeWifi
from typing import List, Optional
import pywifi
import time
from fastapi.staticfiles import StaticFiles
import schemas
from pydantic import BaseModel
from fastapi.responses import RedirectResponse


app = FastAPI()

# Serve static files (HTML, CSS, JS) from the 'frontend' directory under /static
app.mount("/static", StaticFiles(directory="../frontend", html=True), name="static")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint -> redirect to the web UI
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/scan-wifi/")
def scan_wifi(db: Session = Depends(get_db)):
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]  # Assuming the first interface is the correct one

        iface.scan()
        time.sleep(5)  # Give the card some time to scan

        scan_results = iface.scan_results()

        networks_found = 0
        suspicious_count = 0
        total_risk_score = 0.0

        for network in scan_results:
            networks_found += 1
            ssid = network.ssid
            signal_strength = network.signal

            # Basic fake Wi-Fi detection logic (can be expanded)
            is_suspicious = False
            detection_reason = ""
            risk_score = 0.0

            # Example: Detect networks with no security (open networks)
            if network.akm == [] and network.auth == [] and network.cipher == []: # Open network
                is_suspicious = True
                detection_reason = "Open network with no security."
                risk_score += 3.0
            
            # Example: Very low signal strength could indicate a distant or spoofed AP
            if signal_strength < -80: # dBm
                risk_score += 1.0
                if not is_suspicious:
                    detection_reason = "Very low signal strength."
                    is_suspicious = True
                else:
                    detection_reason += " Very low signal strength."

            db_network_scan = NetworkScan(
                ssid=ssid,
                signal_strength=signal_strength,
                security_type="Open" if not network.akm else ", ".join([str(a) for a in network.akm]),
                risk_score=risk_score,
                is_suspicious=is_suspicious,
                detection_reason=detection_reason,
            )
            db.add(db_network_scan)
            if is_suspicious:
                suspicious_count += 1
            total_risk_score += risk_score
        
        db.commit()

        # Record scan history
        average_risk = total_risk_score / networks_found if networks_found > 0 else 0.0
        db_scan_history = ScanHistory(
            networks_found=networks_found,
            suspicious_count=suspicious_count,
            average_risk=average_risk,
        )
        db.add(db_scan_history)
        db.commit()
        db.refresh(db_scan_history)

        return {"message": "Wi-Fi scan completed successfully", "scan_id": db_scan_history.id}

    except pywifi.PyWiFiError as e:
        raise HTTPException(status_code=500, detail=f"Wi-Fi scanning error: {e}. Please ensure your Wi-Fi adapter is enabled and drivers are installed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans/", response_model=List[schemas.NetworkScan])
def get_scans(db: Session = Depends(get_db)):
    scans = db.query(NetworkScan).order_by(NetworkScan.scan_timestamp.desc()).all()
    return scans

@app.get("/scans/{scan_id}", response_model=schemas.NetworkScan)
def get_scan_details(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(NetworkScan).filter(NetworkScan.id == scan_id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.get("/scan-history/", response_model=List[schemas.ScanHistory])
def get_scan_history(db: Session = Depends(get_db)):
    history = db.query(ScanHistory).order_by(ScanHistory.scan_timestamp.desc()).all()
    return history

@app.get("/fake-wifis/", response_model=List[schemas.FakeWifi])
def get_fake_wifis(db: Session = Depends(get_db)):
    fake_wifis = db.query(FakeWifi).all()
    return fake_wifis

class CreateFakeWifiRequest(BaseModel):
    ssid: str
    password: Optional[str] = None

@app.post("/create-fake-wifi/")
def create_fake_wifi(
    payload: CreateFakeWifiRequest,
    db: Session = Depends(get_db)
):
    try:
        db_fake_wifi = FakeWifi(
            ssid=payload.ssid,
            password=payload.password,
            is_active=True
        )
        db.add(db_fake_wifi)
        db.commit()
        db.refresh(db_fake_wifi)

        return {"message": f"Fake Wi-Fi '{payload.ssid}' created (simulated) successfully!", "fake_wifi_id": db_fake_wifi.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
