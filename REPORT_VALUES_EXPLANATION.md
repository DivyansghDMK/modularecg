# ECG Report Values: Calculated vs Hard-Coded

This document explains which values in the PDF reports are **calculated from live ECG data** and which are **hard-coded/placeholder values**.

---

## 📊 **Report Sections Breakdown**

### **1. Patient Information** ✅ **LIVE DATA**
All patient information is entered by the user and dynamically included:
- **Name**: From patient input form
- **Age**: From patient input form
- **Gender**: From patient input form
- **Date/Time**: Current timestamp when report is generated

---

### **2. ECG Waveform Graphs** ✅ **LIVE DATA**
All 12-lead ECG graphs display **real-time captured data**:
- **Leads I, II, III, aVR, aVL, aVF, V1-V6**: Last 10 seconds of live ECG data
- Graphs are captured from the running ECG test page
- Sampling rate: 250 Hz (or configured rate)
- Display: Medical-grade ECG grid with proper scaling

---

### **3. Primary ECG Metrics**

#### ✅ **CALCULATED FROM LIVE DATA:**

| Metric | Source | Calculation Method |
|--------|--------|-------------------|
| **HR** (Heart Rate) | Live Lead II data | R-peak detection using Pan-Tompkins algorithm |
| **PR Interval** | Live Lead II data | Derivative-based P-wave to R-wave detection |
| **QRS Duration** | Live Lead II data | Q-onset to S-end detection |
| **QT Interval** | Live Lead II data | Q-onset to T-end detection |
| **QTc Interval** | Calculated from QT & HR | Bazett's formula: QTc = QT / √(RR interval) |
| **ST Segment** | Live Lead II data | J-point elevation/depression at J+60ms |
| **RR Interval** | Calculated from HR | RR = 60000 / HR (in milliseconds) |

#### ⚠️ **PARTIALLY HARD-CODED:**

| Metric | Status | Notes |
|--------|--------|-------|
| **HR_max** | Hard-coded: 136 bpm | Should track actual max HR during session |
| **HR_min** | Hard-coded: 74 bpm | Should track actual min HR during session |
| **Total Heartbeats** | Hard-coded: 4833 | Should count actual beats during session |

---

### **4. Advanced ECG Parameters**

#### ✅ **NOW CALCULATED FROM LIVE DATA:**

| Parameter | Calculation Method | Meaning |
|-----------|-------------------|---------|
| **P/QRS/T** | Measured from Lead II waveforms | P-wave, QRS, and T-wave amplitudes in mm (1mV = 10mm) |
| **RV5** | Measured from Lead V5 R-wave amplitude | R-wave amplitude in V5 lead (in mV) |
| **SV1** | Measured from Lead V1 S-wave amplitude | S-wave amplitude in V1 lead (in mV) |
| **RV5+SV1** | Sum of RV5 and SV1 | Combined amplitude for LVH (Left Ventricular Hypertrophy) detection |

#### ❌ **STILL HARD-CODED:**

| Parameter | Current Value | Meaning |
|-----------|--------------|---------|
| **QTCF** | `0.049` | QT correction factor (placeholder) |
| **VCG Angle** | `75.53°` | Vectorcardiogram angle (placeholder) |
| **TAT** | `42.04 ms` | Total activation time (placeholder) |
| **QRS Axis** | Partially calculated | Currently shows degrees but needs verification |

---

### **5. Conclusions** ✅ **LIVE ANALYSIS**

Conclusions are **dynamically generated** based on live metrics:

- **Heart Rate Analysis**: Checks for tachycardia (>100 bpm) or bradycardia (<60 bpm)
- **PR Interval Analysis**: Detects prolonged (>200ms) or short (<120ms) PR intervals
- **QRS Analysis**: Identifies wide QRS (>120ms) or borderline duration (>100ms)
- **HRV/Stress Level**: Analyzes heart rate variability for stress indication

**Example Live Conclusions:**
- ✅ "Normal heart rate - Within healthy range (60-100 BPM)"
- ⚠️ "Prolonged PR interval - Possible first-degree heart block"
- 🔴 "Wide QRS complex - Possible bundle branch block"

---

## 🎯 **Summary Table**

| Report Element | Status | Data Source |
|----------------|--------|-------------|
| **Patient Info** | ✅ Live | User input form |
| **12-Lead Graphs** | ✅ Live | Last 10 seconds of ECG acquisition |
| **Heart Rate** | ✅ Live | Calculated from Lead II R-peaks |
| **PR Interval** | ✅ Live | P-wave to R-wave timing |
| **QRS Duration** | ✅ Live | QRS complex width |
| **QT Interval** | ✅ Live | Q-onset to T-end |
| **QTc Interval** | ✅ Live | Bazett's formula |
| **ST Segment** | ✅ Live | J-point measurement |
| **RR Interval** | ✅ Live | Calculated from HR |
| **HR Max/Min** | ❌ Hard-coded | 136 / 74 bpm (placeholders) |
| **Total Beats** | ❌ Hard-coded | 4833 (placeholder) |
| **P/QRS/T Amplitudes** | ✅ Live | Measured from Lead II waveforms |
| **RV5/SV1** | ✅ Live | Measured from V5 and V1 leads |
| **RV5+SV1** | ✅ Live | Calculated sum for LVH detection |
| **QTCF** | ❌ Hard-coded | `0.049` (placeholder) |
| **VCG Angle** | ❌ Hard-coded | `75.53°` (placeholder) |
| **TAT** | ❌ Hard-coded | `42.04 ms` (placeholder) |
| **Conclusions** | ✅ Live | Auto-generated from metrics |

---

## 🔧 **What Still Needs Implementation**

### **High Priority:**
1. **HR Max/Min Tracking**: Track actual max/min heart rate during session
2. **Total Heartbeat Counter**: Count actual R-peaks detected during session

### **Medium Priority:**
3. **QRS Axis**: Currently showing "0" - needs proper calculation from Leads I and aVF

### **Low Priority (Advanced Metrics):**
4. **VCG Angle**: Vectorcardiogram spatial angle calculation
5. **TAT (Total Activation Time)**: QRS onset to peak calculation
6. **QTCF (QT Correction Factor)**: Alternative QT correction methods

### **✅ Recently Completed:**
- ~~P/QRS/T Wave Amplitudes~~: **NOW CALCULATED** from Lead II waveforms
- ~~RV5 and SV1 Amplitudes~~: **NOW CALCULATED** from V5 and V1 leads
- ~~RV5+SV1 Sum~~: **NOW CALCULATED** for LVH detection

---

## 📝 **Notes for Developers**

### **Current Data Flow:**
```
Live ECG Data (12 leads)
    ↓
Lead II Analysis (primary)
    ↓
Signal Processing (bandpass filter, baseline correction)
    ↓
Feature Detection (R-peaks, P-waves, Q/S/T waves)
    ↓
Metric Calculation (HR, PR, QRS, QT, ST)
    ↓
Dashboard Display
    ↓
PDF Report Generation ← Extracts current values
```

### **Key Files:**
- **Metric Calculation**: `src/ecg/twelve_lead_test.py` (lines 1580-2000)
- **Dashboard Data Extraction**: `src/dashboard/dashboard.py` (lines 1516-1545)
- **Report Generation**: `src/ecg/ecg_report_generator.py` (lines 461-1350)
- **Conclusion Generation**: `src/dashboard/dashboard.py` (lines 2028-2127)

### **How to Verify Live vs Hard-coded:**
1. **Start ECG monitoring** with demo mode
2. **Change demo BPM** (e.g., from 60 to 90)
3. **Generate two reports** at different BPM settings
4. **Compare values**:
   - Values that **change** = Live calculated ✅
   - Values that **stay the same** = Hard-coded ❌

---

## ✅ **Recent Improvements**

### **What Was Fixed:**
- ✅ Conclusions now properly extracted from HTML content in dashboard
- ✅ RR interval dynamically calculated from heart rate
- ✅ Live conclusions forced to update before report generation
- ✅ HTML parsing for conclusion text (not just plain text)
- ✅ Debug logging for conclusion extraction
- ✅ **P/QRS/T wave amplitudes** now calculated from Lead II waveforms
- ✅ **RV5 amplitude** measured from Lead V5 R-wave peaks
- ✅ **SV1 amplitude** measured from Lead V1 S-wave depths
- ✅ **RV5+SV1 sum** automatically calculated for LVH detection

### **What Works Well:**
- All 12-lead graphs show real ECG waveforms
- Primary metrics (HR, PR, QRS, QT, QTc, ST) are calculated live
- Patient information is dynamic
- Conclusions reflect actual ECG findings
- Wave amplitudes measured from actual signal data
- Lead-specific measurements for clinical diagnosis

---

## 🚀 **Future Enhancement Roadmap**

### **Phase 1: Basic Tracking** (Easy)
- [ ] Add session HR max/min tracking
- [ ] Add total heartbeat counter
- [ ] Fix QT interval display in reports

### **Phase 2: Amplitude Measurements** (Medium)
- [ ] Calculate P-wave amplitude
- [ ] Calculate QRS amplitude
- [ ] Calculate T-wave amplitude
- [ ] Measure RV5 and SV1 specifically

### **Phase 3: Advanced Calculations** (Complex)
- [ ] Implement proper QRS axis calculation
- [ ] Add VCG spatial angle
- [ ] Calculate TAT (Total Activation Time)
- [ ] Alternative QTc formulas (Fridericia, Framingham)

---

**Last Updated**: October 13, 2025  
**Software Version**: Main Branch (Commit: efdb28d)

