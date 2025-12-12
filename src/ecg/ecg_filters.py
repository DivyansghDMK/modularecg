"""
ECG Filter Module - AC Filter, EMG Filter, and DFT Filter Implementation

This module provides medical-grade filtering for ECG signals:
- AC Filter: Notch filter to remove 50Hz or 60Hz power line interference
- EMG Filter: High-pass filter to remove muscle artifacts (25Hz, 35Hz, 45Hz, 75Hz, 100Hz, 150Hz)
- DFT Filter: High-pass filter to remove baseline wander (0.05Hz, 0.5Hz)

Usage:
    from ecg.ecg_filters import apply_ecg_filters
    
    filtered_signal = apply_ecg_filters(
        signal, 
        sampling_rate=500,
        ac_filter="50",  # "off", "50", or "60"
        emg_filter="150",  # "25", "35", "45", "75", "100", "150"
        dft_filter="0.5"  # "off", "0.05", or "0.5"
    )
"""

import numpy as np
from scipy.signal import butter, filtfilt, iirnotch
from typing import Union, Optional


def apply_ac_filter(signal: np.ndarray, sampling_rate: float, ac_filter: str) -> np.ndarray:
    """
    Apply AC (Notch) Filter to remove power line interference
    
    Args:
        signal: Input ECG signal
        sampling_rate: Sampling frequency in Hz
        ac_filter: "off", "50", or "60" (Hz)
    
    Returns:
        Filtered signal
    """
    if ac_filter == "off" or not ac_filter:
        return signal
    
    try:
        notch_freq = float(ac_filter)  # 50 or 60 Hz
        
        # Design notch filter (bandstop filter)
        nyquist = sampling_rate / 2.0
        quality_factor = 30.0  # Quality factor for notch filter
        
        # Normalize frequency
        w0 = notch_freq / nyquist
        
        # Ensure frequency is within valid range (0 < w0 < 1)
        if w0 <= 0 or w0 >= 1:
            print(f"⚠️ AC filter frequency {notch_freq}Hz is invalid for sampling rate {sampling_rate}Hz")
            return signal
        
        # Design IIR notch filter
        b, a = iirnotch(w0, quality_factor)
        
        # Apply filter (zero-phase filtering)
        filtered_signal = filtfilt(b, a, signal)
        
        return filtered_signal
    
    except Exception as e:
        print(f"❌ Error applying AC filter ({ac_filter}Hz): {e}")
        return signal


def apply_emg_filter(signal: np.ndarray, sampling_rate: float, emg_filter: str) -> np.ndarray:
    """
    Apply EMG Filter (High-pass filter) to remove muscle artifacts
    
    Args:
        signal: Input ECG signal
        sampling_rate: Sampling frequency in Hz
        emg_filter: Cutoff frequency - "25", "35", "45", "75", "100", or "150" (Hz)
    
    Returns:
        Filtered signal
    """
    if not emg_filter or emg_filter == "off":
        return signal
    
    try:
        cutoff_freq = float(emg_filter)  # High-pass cutoff frequency
        
        # Design high-pass Butterworth filter
        nyquist = sampling_rate / 2.0
        
        # Normalize cutoff frequency
        normalized_cutoff = cutoff_freq / nyquist
        
        # Ensure cutoff is within valid range
        if normalized_cutoff <= 0 or normalized_cutoff >= 1:
            print(f"⚠️ EMG filter cutoff {cutoff_freq}Hz is invalid for sampling rate {sampling_rate}Hz")
            return signal
        
        # Design 4th order high-pass Butterworth filter
        b, a = butter(4, normalized_cutoff, btype='high')
        
        # Apply filter (zero-phase filtering)
        filtered_signal = filtfilt(b, a, signal)
        
        return filtered_signal
    
    except Exception as e:
        print(f"❌ Error applying EMG filter ({emg_filter}Hz): {e}")
        return signal


def apply_dft_filter(signal: np.ndarray, sampling_rate: float, dft_filter: str) -> np.ndarray:
    """
    Apply DFT Filter (High-pass filter) to remove baseline wander
    
    Args:
        signal: Input ECG signal
        sampling_rate: Sampling frequency in Hz
        dft_filter: Cutoff frequency - "off", "0.05", or "0.5" (Hz)
    
    Returns:
        Filtered signal
    """
    if dft_filter == "off" or not dft_filter:
        return signal
    
    try:
        cutoff_freq = float(dft_filter)  # Low cutoff frequency (0.05 or 0.5 Hz)
        
        # Design high-pass Butterworth filter for baseline wander removal
        nyquist = sampling_rate / 2.0
        
        # Normalize cutoff frequency
        normalized_cutoff = cutoff_freq / nyquist
        
        # Ensure cutoff is within valid range
        if normalized_cutoff <= 0 or normalized_cutoff >= 1:
            print(f"⚠️ DFT filter cutoff {cutoff_freq}Hz is invalid for sampling rate {sampling_rate}Hz")
            return signal
        
        # Design 2nd order high-pass Butterworth filter (gentle for baseline)
        b, a = butter(2, normalized_cutoff, btype='high')
        
        # Apply filter (zero-phase filtering)
        filtered_signal = filtfilt(b, a, signal)
        
        return filtered_signal
    
    except Exception as e:
        print(f"❌ Error applying DFT filter ({dft_filter}Hz): {e}")
        return signal


def apply_ecg_filters(
    signal: Union[np.ndarray, list],
    sampling_rate: float = 500,
    ac_filter: Optional[str] = None,
    emg_filter: Optional[str] = None,
    dft_filter: Optional[str] = None
) -> np.ndarray:
    """
    Apply all ECG filters in the correct order:
    1. DFT Filter (baseline wander removal) - first
    2. EMG Filter (muscle artifact removal)
    3. AC Filter (power line interference removal) - last
    
    Args:
        signal: Input ECG signal (numpy array or list)
        sampling_rate: Sampling frequency in Hz (default: 500)
        ac_filter: AC filter setting - "off", "50", or "60"
        emg_filter: EMG filter setting - "25", "35", "45", "75", "100", "150"
        dft_filter: DFT filter setting - "off", "0.05", or "0.5"
    
    Returns:
        Filtered signal as numpy array
    """
    # Convert to numpy array if needed
    if not isinstance(signal, np.ndarray):
        signal = np.array(signal, dtype=float)
    
    # Check minimum signal length
    if len(signal) < 10:
        return signal
    
    # Apply filters in correct order
    filtered = signal.copy()
    
    # 1. DFT Filter first (removes slow baseline wander)
    if dft_filter:
        filtered = apply_dft_filter(filtered, sampling_rate, dft_filter)
    
    # 2. EMG Filter second (removes muscle artifacts)
    if emg_filter:
        filtered = apply_emg_filter(filtered, sampling_rate, emg_filter)
    
    # 3. AC Filter last (removes power line interference)
    if ac_filter:
        filtered = apply_ac_filter(filtered, sampling_rate, ac_filter)
    
    return filtered


def apply_ecg_filters_from_settings(
    signal: Union[np.ndarray, list],
    sampling_rate: float = 500,
    settings_manager=None
) -> np.ndarray:
    """
    Apply ECG filters using settings from SettingsManager
    
    Args:
        signal: Input ECG signal
        sampling_rate: Sampling frequency in Hz
        settings_manager: SettingsManager instance (optional, will create if not provided)
    
    Returns:
        Filtered signal
    """
    # Import here to avoid circular imports
    if settings_manager is None:
        from utils.settings_manager import SettingsManager
        settings_manager = SettingsManager()
    
    # Get filter settings
    ac_filter = settings_manager.get_setting("filter_ac", "off")
    emg_filter = settings_manager.get_setting("filter_emg", "150")
    dft_filter = settings_manager.get_setting("filter_dft", "0.5")
    
    # Apply filters
    return apply_ecg_filters(
        signal=signal,
        sampling_rate=sampling_rate,
        ac_filter=ac_filter,
        emg_filter=emg_filter,
        dft_filter=dft_filter
    )

