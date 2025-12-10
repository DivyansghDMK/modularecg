# ECG Monitor Application

Single-application README with setup, usage, and current technical details for the 12‑lead ECG monitor and dashboard.

## Overview
- 12‑lead real-time ECG display (PyQt5 + PyQtGraph)
- Metrics: HR (10–300 bpm), PR, QRS, QT/QTc (Bazett), QRS axis, ST
- Expanded lead view with PQRST markers and per-lead metrics
- Lead derivation from 8‑channel packet input; live baseline centering
- PDF report generation and recent-report list
- Rolling display window: 10 seconds at 25 mm/s (scaled by wave speed)

## Quick Start
1) Python 3.10+ recommended  
2) Install deps:  
```bash
pip install -r requirements.txt
```
3) Run:  
```bash
python src/main.py
```

## Controls & UI
- Top cards: HR, PR, QRS, Axis, ST, QT/QTc, Time
- Buttons: Start / Stop / Ports / Generate Report / 12:1 / 6:2 / Back
- Lead clicks: open Expanded Lead View for detailed single-lead analysis
- Wave speed/gain from control panel; window length scales with speed (10 s at 25 mm/s)

## Data & Signals
- Input: serial 8-channel packets → mapped to 12 leads
  - Limb: I=L1, II=Lead2, III=II−I
  - Augmented: aVR=−(I+II)/2, aVL=(I−III)/2, aVF=(II+III)/2
  - Precordial: V1–V6 direct from packet channels
- Sampling: defaults to 250 Hz (serial) or 500 Hz for display calculations where needed
- Filters: band-pass 0.5–40 Hz before R-peak work

## Heart Rate (HR) Calculation
- Source: Lead II from rolling window
- R-peak detection: `scipy.signal.find_peaks` with three strategies
  - Conservative: distance 0.5s
  - Normal: distance 0.3s
  - Tight: distance 0.2s
- RR intervals: keep 200–6000 ms (10–300 bpm), HR = 60000 / median(RR)
- Guards: clamp 10–300 bpm; reject implausible high BPM when peak count is too low; low-BPM smoothing buffer longer (7 samples) and update threshold 3 bpm under 40 BPM

## Other Metrics
- PR interval: scan 40–250 ms before R in Lead II; defaults to 150 ms if not found
- QRS duration: ±80 ms around R; valid 40–200 ms
- QRS axis: atan2(aVF, I) in degrees
- ST: measure at J+60 ms after estimating J at R+40 ms; normalized to local std
- QT: Q before R (≤40 ms), T-end near baseline within 500 ms post-R; valid 200–600 ms
- QTc: Bazett (QT / sqrt(RR))

## Rolling Window & Display
- Baseline window: 10 s at 25 mm/s; scales with wave speed
  - 12.5 mm/s → ~20 s
  - 50 mm/s → ~5 s
- Buffer lengths sized from `seconds_to_show` for both main and overlay views

## Expanded Lead View
- Matplotlib waveform, amplification controls, history slider
- Per-lead metrics: HR, RR, PR, QRS, QT/QTc, ST, arrhythmia text
- PQRST detection uses 0.5–40 Hz filter and Pan-Tompkins style steps

## Lead Detachment / Flat-Line
- Flat-line/lead-detach alert on 12-lead view with styled popup
- Flat-line checks use percentile-based thresholds and frequent polling

## Reports
- Generate PDF from dashboard; stored to chosen path and recent list

## Running & Scripts
- Windows launchers: `launch_app.bat`, `launch_app.ps1`
- Direct: `python src/main.py`

## Project Structure (trimmed)
```
modularecg/
├─ src/
│  ├─ main.py            # Entry point, login/register, nav
│  ├─ dashboard/         # Dashboard UI and metrics binding
│  ├─ ecg/               # 12-lead logic, expanded view, sampling helpers
│  ├─ utils/             # helpers (localization, settings, etc.)
├─ assets/               # images, GIFs
├─ requirements.txt
```

## Notes & Limits
- Educational/research use; not FDA-cleared
- HR range enforced 10–300 bpm; low-BPM smoothing tightened for stability
- Uses Lead II for HR; depends on signal quality and valid peak detection

## Support
- GitHub Issues (if hosted) or contact maintainer

## License
MIT License (see LICENSE)

## Disclaimer
Not for clinical diagnosis. Use under guidance of qualified professionals.