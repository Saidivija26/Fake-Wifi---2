document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refreshButton');
    const overallRiskScoreSpan = document.getElementById('overallRiskScore');
    const scanResultsTableBody = document.getElementById('scanResultsTableBody');
    const createFakeWifiForm = document.getElementById('createFakeWifiForm');
    const fakeSsidInput = document.getElementById('fakeSsid');
    const fakePasswordInput = document.getElementById('fakePassword');
    const fakeWifiStatusDiv = document.getElementById('fakeWifiStatus');
    const createdFakeWifiList = document.getElementById('createdFakeWifiList');

    const API_BASE_URL = 'http://127.0.0.1:8000'; // Assuming your FastAPI runs on this address

    // Function to fetch and display scan results
    async function fetchScanResults() {
        scanResultsTableBody.innerHTML = '<tr><td colspan="7">Scanning for networks...</td></tr>';
        overallRiskScoreSpan.textContent = 'Scanning...';

        try {
            // Initiate a new scan on the backend
            const scanResponse = await fetch(`${API_BASE_URL}/scan-wifi/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const scanData = await scanResponse.json();
            console.log('Scan initiated:', scanData);

            // Fetch all scan results after the new scan
            const response = await fetch(`${API_BASE_URL}/scans/`);
            const scans = await response.json();

            scanResultsTableBody.innerHTML = '';
            if (scans.length === 0) {
                scanResultsTableBody.innerHTML = '<tr><td colspan="7">No scan results yet. Click "Refresh Scan" to start.</td></tr>';
                overallRiskScoreSpan.textContent = 'N/A';
                return;
            }

            let totalRisk = 0;
            let suspiciousCount = 0;

            // Display only the latest scan results for unique SSIDs
            const latestScans = {};
            scans.forEach(scan => {
                if (!latestScans[scan.ssid] || new Date(scan.scan_timestamp) > new Date(latestScans[scan.ssid].scan_timestamp)) {
                    latestScans[scan.ssid] = scan;
                }
            });

            Object.values(latestScans).forEach(scan => {
                const row = scanResultsTableBody.insertRow();
                row.insertCell(0).textContent = scan.ssid;
                row.insertCell(1).textContent = scan.signal_strength ? `${scan.signal_strength} dBm` : 'N/A';
                row.insertCell(2).textContent = scan.security_type || 'N/A';
                row.insertCell(3).textContent = scan.risk_score !== null ? scan.risk_score.toFixed(2) : 'N/A';
                const suspiciousCell = row.insertCell(4);
                suspiciousCell.textContent = scan.is_suspicious ? 'Yes' : 'No';
                if (scan.is_suspicious) {
                    suspiciousCell.classList.add('suspicious');
                }
                row.insertCell(5).textContent = scan.detection_reason || 'N/A';
                row.insertCell(6).textContent = new Date(scan.scan_timestamp).toLocaleString();

                totalRisk += scan.risk_score || 0;
                if (scan.is_suspicious) {
                    suspiciousCount++;
                }
            });

            overallRiskScoreSpan.textContent = (totalRisk / Object.values(latestScans).length).toFixed(2);

        } catch (error) {
            console.error('Error fetching scan results:', error);
            scanResultsTableBody.innerHTML = '<tr><td colspan="7" style="color: red;">Error fetching scan results. Please ensure the backend is running.</td></tr>';
            overallRiskScoreSpan.textContent = 'Error';
        }
    }

    // Function to fetch and display created fake Wi-Fi networks
    async function fetchFakeWifiNetworks() {
        createdFakeWifiList.innerHTML = '<li>Loading fake Wi-Fi networks...</li>';
        try {
            const response = await fetch(`${API_BASE_URL}/fake-wifis/`);
            const fakeWifis = await response.json();

            createdFakeWifiList.innerHTML = '';
            if (fakeWifis.length === 0) {
                createdFakeWifiList.innerHTML = '<li>No fake Wi-Fi networks created yet.</li>';
                return;
            }

            fakeWifis.forEach(wifi => {
                const listItem = document.createElement('li');
                listItem.textContent = `SSID: ${wifi.ssid}, Password: ${wifi.password || 'N/A'}, Active: ${wifi.is_active ? 'Yes' : 'No'}`;
                createdFakeWifiList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error fetching fake Wi-Fi networks:', error);
            createdFakeWifiList.innerHTML = '<li>Error loading fake Wi-Fi networks.</li>';
        }
    }

    // Event listener for refresh button
    refreshButton.addEventListener('click', fetchScanResults);

    // Event listener for creating fake Wi-Fi
    createFakeWifiForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        fakeWifiStatusDiv.textContent = 'Creating fake Wi-Fi...';
        try {
            const ssid = fakeSsidInput.value;
            const password = fakePasswordInput.value;

            const response = await fetch(`${API_BASE_URL}/create-fake-wifi/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ssid, password })
            });

            const result = await response.json();
            if (response.ok) {
                fakeWifiStatusDiv.textContent = result.message;
                fakeSsidInput.value = '';
                fakePasswordInput.value = '';
                fetchFakeWifiNetworks(); // Refresh the list of fake Wi-Fi networks
            } else {
                fakeWifiStatusDiv.textContent = `Error: ${result.detail || result.message}`;
            }
        } catch (error) {
            console.error('Error creating fake Wi-Fi:', error);
            fakeWifiStatusDiv.textContent = 'Error creating fake Wi-Fi.';
        }
    });

    // Initial load
    fetchScanResults();
    fetchFakeWifiNetworks();
});