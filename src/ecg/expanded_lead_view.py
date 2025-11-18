"""
Expanded Lead View - Detailed ECG lead analysis with PQRST labeling and metrics
This module provides an expanded view of individual ECG leads with comprehensive analysis.
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
    QSizePolicy, QScrollArea, QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QApplication, QDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
import pyqtgraph as pg
from scipy.signal import find_peaks, butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

class PQRSTAnalyzer:
    """Analyze ECG signal to detect P, Q, R, S, T waves and calculate metrics"""
    
    def __init__(self, sampling_rate=500):
        self.fs = sampling_rate
        self.r_peaks = []
        self.p_peaks = []
        self.q_peaks = []
        self.s_peaks = []
        self.t_peaks = []
        
    def analyze_signal(self, signal):
        """Analyze ECG signal and detect all wave components"""
        try:
            # Filter the signal
            filtered_signal = self._filter_signal(signal)
            
            # Detect R peaks first
            self.r_peaks = self._detect_r_peaks(filtered_signal)
            
            if len(self.r_peaks) > 0:
                # Detect other waves based on R peaks
                self.p_peaks = self._detect_p_waves(filtered_signal, self.r_peaks)
                self.q_peaks = self._detect_q_waves(filtered_signal, self.r_peaks)
                self.s_peaks = self._detect_s_waves(filtered_signal, self.r_peaks)
                self.t_peaks = self._detect_t_waves(filtered_signal, self.r_peaks)
            
            return {
                'r_peaks': self.r_peaks,
                'p_peaks': self.p_peaks,
                'q_peaks': self.q_peaks,
                's_peaks': self.s_peaks,
                't_peaks': self.t_peaks
            }
        except Exception as e:
            print(f"Error in PQRST analysis: {e}")
            return {'r_peaks': [], 'p_peaks': [], 'q_peaks': [], 's_peaks': [], 't_peaks': []}
    
    def _filter_signal(self, signal):
        """Apply bandpass filter to ECG signal"""
        try:
            nyq = 0.5 * self.fs
            low = 0.5 / nyq
            high = 40 / nyq
            b, a = butter(4, [low, high], btype='band')
            return filtfilt(b, a, signal)
        except:
            return signal
    
    def _detect_r_peaks(self, signal):
        """Detect R peaks using Pan-Tompkins algorithm"""
        try:
            # Differentiate
            diff = np.ediff1d(signal)
            # Square
            squared = diff ** 2
            # Moving window integration
            window_size = int(0.15 * self.fs)
            mwa = np.convolve(squared, np.ones(window_size)/window_size, mode='same')
            
            # Find peaks
            threshold = np.mean(mwa) + 0.5 * np.std(mwa)
            min_distance = int(0.2 * self.fs)
            peaks, _ = find_peaks(mwa, height=threshold, distance=min_distance)
            return peaks
        except:
            return []
    
    def _detect_p_waves(self, signal, r_peaks):
        """Detect P waves before R peaks"""
        p_peaks = []
        for r in r_peaks:
            # Look for P wave 120-200ms before R peak for better accuracy
            start = max(0, r - int(0.20 * self.fs))
            end = max(0, r - int(0.12 * self.fs))
            if end > start:
                segment = signal[start:end]
                if len(segment) > 0:
                    p_idx = start + np.argmax(segment)
                    p_peaks.append(p_idx)
        return p_peaks
    
    def _detect_q_waves(self, signal, r_peaks):
        """Detect Q waves (negative deflection before R)"""
        q_peaks = []
        for r in r_peaks:
            # Look for Q wave up to 80ms before R peak
            start = max(0, r - int(0.08 * self.fs))
            end = r
            if end > start:
                segment = signal[start:end]
                if len(segment) > 0:
                    # Q wave is the minimum point between the P wave end and R peak
                    q_idx = start + np.argmin(segment)
                    q_peaks.append(q_idx)
        return q_peaks
    
    def _detect_s_waves(self, signal, r_peaks):
        """Detect S waves (negative deflection after R)"""
        s_peaks = []
        for r in r_peaks:
            # Look for S wave up to 80ms after R peak
            start = r
            end = min(len(signal), r + int(0.08 * self.fs))
            if end > start:
                segment = signal[start:end]
                if len(segment) > 0:
                    s_idx = start + np.argmin(segment)
                    s_peaks.append(s_idx)
        return s_peaks
    
    def _detect_t_waves(self, signal, r_peaks):
        """Detect T waves after S waves"""
        t_peaks = []
        for r in r_peaks:
            # Look for T wave 100-300ms after R peak
            start = min(len(signal), r + int(0.1 * self.fs))
            end = min(len(signal), r + int(0.3 * self.fs))
            if end > start:
                segment = signal[start:end]
                if len(segment) > 0:
                    t_idx = start + np.argmax(segment)
                    t_peaks.append(t_idx)
        return t_peaks

class MetricsCard(QFrame):
    """Individual metric card with color coding and animations"""
    
    def __init__(self, title, value, unit, color="#0984e3", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        # Base sizes used for responsive scaling - reduced for smaller screens
        self._base_title_pt = 11
        self._base_value_pt = 20
        self._base_status_pt = 10
        
        # Increase card vertical room to prevent value text cropping on macOS/Windows
        self.setMinimumHeight(160)
        self.setMaximumHeight(200)
        self.base_style = f"""
            QFrame {{
                background: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
                border-top: 4px solid {self.color};
                margin: 4px;
            }}
        """
        self.hover_style = f"""
            QFrame {{
                background: #f8f9fa;
                border-radius: 8px;
                border: 2px solid {self.color};
                border-top: 4px solid {self.color};
                margin: 4px;
            }}
        """
        self.setStyleSheet(self.base_style)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", self._base_title_pt, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.color}; border: none; margin: 0; padding: 0; font-weight: bold; background: transparent;")
        title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(f"{self.value} {self.unit}")
        self.value_label.setFont(QFont("Segoe UI", self._base_value_pt, QFont.Bold))
        self.value_label.setStyleSheet("color: #2c3e50; border: none; margin: 4px 0; font-weight: bold; background: transparent;")
        self.value_label.setAlignment(Qt.AlignLeft)
        # Ensure enough label height for larger fonts to avoid clipping
        self.value_label.setMinimumHeight(40)
        self.value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel(self.get_status())
        self.status_label.setFont(QFont("Segoe UI", self._base_status_pt, QFont.Bold))
        self.status_label.setStyleSheet(f"color: white; background-color: {self.get_status_color()}; border-radius: 6px; padding: 6px 10px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(self.status_label)
        
    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.base_style)
        super().leaveEvent(event)

    def get_status(self):
        """Get status based on metric value"""
        if self.title == "Heart Rate":
            if 60 <= self.value <= 100: return "NORMAL"
            elif self.value < 60: return "BRADYCARDIA"
            else: return "TACHYCARDIA"
        elif self.title == "PR Interval":
            if 120 <= self.value <= 200: return "NORMAL"
            elif self.value < 120: return "SHORT"
            else: return "PROLONGED"
        elif self.title == "QRS Duration":
            if 80 <= self.value <= 120: return "NORMAL"
            elif self.value < 80: return "NARROW"
            else: return "WIDE"
        elif self.title == "QTc Interval":
            if 350 <= self.value <= 450: return "NORMAL"
            elif self.value < 350: return "SHORT"
            else: return "PROLONGED"
        else:
            return "MEASURED"
    
    def get_status_color(self):
        """Get color based on status"""
        status = self.get_status()
        if status == "NORMAL": return "#2ecc71"  # Green
        if status in ["BRADYCARDIA", "TACHYCARDIA", "PROLONGED", "WIDE"]: return "#e74c3c"  # Red
        if status in ["SHORT", "NARROW"]: return "#f39c12" # Orange
        return "#3498db" # Blue
    
    def update_value(self, new_value):
        """Update the metric value"""
        self.value = new_value
        self.value_label.setText(f"{self.value} {self.unit}")
        self.status_label.setText(self.get_status())
        self.status_label.setStyleSheet(f"color: white; background-color: {self.get_status_color()}; border-radius: 4px; padding: 2px 6px;")

    def set_scale(self, scale: float) -> None:
        """Scale fonts responsively based on a scale factor.

        The scale is typically derived from current window size vs. baseline.
        """
        scale = max(0.7, min(1.6, scale))
        self.value_label.setFont(QFont("Segoe UI", int(self._base_value_pt * scale), QFont.Bold))
        self.status_label.setFont(QFont("Segoe UI", int(self._base_status_pt * scale), QFont.Bold))
        # Title is the first child label in layout
        if isinstance(self.layout().itemAt(0).widget(), QLabel):
            self.layout().itemAt(0).widget().setFont(QFont("Segoe UI", int(self._base_title_pt * scale), QFont.Bold))

class ArrhythmiaDetector:
    """Detect various types of arrhythmias from ECG data"""
    
    def __init__(self, sampling_rate=500):
        self.fs = sampling_rate
    
    def detect_arrhythmias(self, signal, r_peaks):
        """Detect various arrhythmias"""
        arrhythmias = []
        
        if len(r_peaks) < 3:
            return ["Insufficient data for arrhythmia detection."]
        
        # Calculate RR intervals
        rr_intervals = np.diff(r_peaks) / self.fs * 1000  # in ms
        
        # Check for specific arrhythmias first
        if self._is_atrial_fibrillation(signal, r_peaks):
            arrhythmias.append("Possible Atrial Fibrillation")
        if self._is_ventricular_tachycardia(rr_intervals):
            arrhythmias.append("Possible Ventricular Tachycardia")
        if self._is_premature_ventricular_contractions(signal, r_peaks):
            arrhythmias.append("Premature Ventricular Contractions Detected")
        
        # If no major arrhythmia, check rate-based conditions
        if not arrhythmias:
            if self._is_bradycardia(rr_intervals):
                arrhythmias.append("Sinus Bradycardia")
            elif self._is_tachycardia(rr_intervals):
                arrhythmias.append("Sinus Tachycardia")

        # If still nothing, check for NSR
        if not arrhythmias and self._is_normal_sinus_rhythm(rr_intervals):
            return ["Normal Sinus Rhythm"]
            
        return arrhythmias if arrhythmias else ["Unspecified Irregular Rhythm"]
    
    def _is_normal_sinus_rhythm(self, rr_intervals):
        """Check if rhythm is normal sinus rhythm"""
        if len(rr_intervals) < 3: return False
        mean_hr = 60000 / np.mean(rr_intervals)
        std_rr = np.std(rr_intervals)
        return 60 <= mean_hr <= 100 and std_rr < 120 # Variation less than 120ms
    
    def _is_atrial_fibrillation(self, signal, r_peaks):
        """Detect atrial fibrillation"""
        if len(r_peaks) < 10: return False
        rr_intervals = np.diff(r_peaks)
        # AF is characterized by highly irregular RR intervals and no clear P waves
        cv = np.std(rr_intervals) / np.mean(rr_intervals) if np.mean(rr_intervals) > 0 else 0
        return cv > 0.15
    
    def _is_ventricular_tachycardia(self, rr_intervals):
        """Detect ventricular tachycardia"""
        if len(rr_intervals) < 3: return False
        mean_hr = 60000 / np.mean(rr_intervals)
        # VT is a run of 3 or more consecutive PVCs, typically wide QRS and fast rate
        return mean_hr > 120 and np.std(rr_intervals) < 40 # Fast and regular
    
    def _is_bradycardia(self, rr_intervals):
        """Detect bradycardia"""
        if len(rr_intervals) < 3: return False
        mean_hr = 60000 / np.mean(rr_intervals)
        return mean_hr < 60
    
    def _is_tachycardia(self, rr_intervals):
        """Detect tachycardia"""
        if len(rr_intervals) < 3: return False
        mean_hr = 60000 / np.mean(rr_intervals)
        return mean_hr > 100
    
    def _is_premature_ventricular_contractions(self, signal, r_peaks):
        """Detect PVCs"""
        if len(r_peaks) < 5: return False
        rr_intervals = np.diff(r_peaks) / self.fs
        mean_rr = np.mean(rr_intervals)
        for i in range(len(rr_intervals)):
            if rr_intervals[i] < 0.8 * mean_rr: # A beat is premature
                # Check for compensatory pause
                if i + 1 < len(rr_intervals) and rr_intervals[i+1] > 1.2 * mean_rr:
                    return True
        return False

class ExpandedLeadView(QDialog):
    """Expanded view for individual ECG leads with detailed analysis"""
    
    def __init__(self, lead_name, ecg_data, sampling_rate=500, parent=None):
        super().__init__(parent)
        self.lead_name = lead_name
        self.ecg_data = np.array(ecg_data) if ecg_data is not None and len(ecg_data) > 0 else np.array([])
        self.sampling_rate = sampling_rate
        # Keep a reference to parent ECG page for shared metrics
        self._parent = parent
        self.analyzer = PQRSTAnalyzer(sampling_rate)
        self.arrhythmia_detector = ArrhythmiaDetector(sampling_rate)
        # Display gain to make waves visually smaller (half-height)
        self.display_gain = 0.5

        self.amplification = 1.0  # Amplification factor
        self.min_amplification = 0.1  # Minimum 10% of original
        self.max_amplification = 10.0  # Maximum 10x amplification

        # Store original y-axis limits (will be set after first plot)
        self.fixed_ylim = None

        # Store the baseline (mean) of the signal for proper zooming
        self.signal_baseline = 0.0
        
        # Demo mode settings - sync with parent's demo manager
        self.demo_mode_active = False
        self.demo_manager = None
        if parent and hasattr(parent, 'demo_manager') and hasattr(parent, 'demo_toggle'):
            self.demo_mode_active = parent.demo_toggle.isChecked()
            self.demo_manager = parent.demo_manager
            print(f"🎬 Expanded view: Demo mode is {'ON' if self.demo_mode_active else 'OFF'}")
        
        # Live data update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.is_live = False
        
        self.setWindowTitle(f"Detailed Analysis - {lead_name}")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 900)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        self.setup_ui()
        self.analyze_ecg()
        
        # Start live updates if parent is available (hardware data)
        if parent is not None:
            self.start_live_mode()

            # Initialize button states based on parent acquisition status
            if hasattr(self, 'expanded_start_btn'):
                self.update_button_states()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.create_header(main_layout)
        
        # Main content area with proper proportions
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Left side - ECG plot (70% of width)
        self.create_ecg_plot(content_layout)
        
        # Right side - Metrics (30% of width)
        self.create_metrics_panel(content_layout)
        
        main_layout.addLayout(content_layout, 1)
        
        # Bottom - Arrhythmia analysis
        self.create_arrhythmia_panel(main_layout)
    
    def create_header(self, parent_layout):
        """Create the header section"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 0, 5, 0)
        
        title_label = QLabel(f"Lead {self.lead_name} - Detailed Waveform Analysis")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; border: none; background: transparent;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #34495e; color: white; border-radius: 5px;
                padding: 8px 18px; font-weight: bold; font-size: 10pt;
            }
            QPushButton:hover { background: #5d6d7e; }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        parent_layout.addWidget(header_frame)

    # Mouse wheel event for amplification

    def wheelEvent(self, event):
        """Handle mouse wheel scrolling for amplification"""
        try:
            # Get scroll direction
            delta = event.angleDelta().y()
            
            # Calculate amplification change
            if delta > 0:
                # Scroll up = amplify (zoom in)
                self.amplification *= 1.1
            else:
                # Scroll down = deamplify (zoom out)
                self.amplification /= 1.1
            
            # Clamp amplification to limits
            self.amplification = max(self.min_amplification, 
                                    min(self.max_amplification, self.amplification))
            
            # Update the plot
            self.update_plot()
            
            # Update amplification display if it exists
            if hasattr(self, 'amp_label'):
                self.amp_label.setText(f"{self.amplification:.2f}x")
            
            event.accept()
        except Exception as e:
            print(f"Error in wheel event: {e}")
    
    def create_ecg_plot(self, parent_layout):
        """Create the ECG plot area"""
        plot_frame = QFrame()
        plot_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        plot_layout = QVBoxLayout(plot_frame)
        plot_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create matplotlib figure with better sizing
        # Use a moderate DPI, but allow canvas to expand with layout
        self.fig = Figure(figsize=(10, 6), facecolor='white', dpi=110)
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout(pad=2.0)
        
        self.setup_ecg_plot()
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(700, 420)
        plot_layout.addWidget(self.canvas)

        # --- AMPLIFICATION CONTROLS ---
        control_frame = QFrame()
        control_frame.setStyleSheet("background: transparent; border: none;")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(10)
        
        # Amplification label
        amp_title = QLabel("Amplification:")
        amp_title.setStyleSheet("""
            color: #2c3e50; 
            font-weight: bold; 
            font-size: 11pt;
            background: transparent;
            border: none;
        """)
        control_layout.addWidget(amp_title)
        
        # - Button (Decrease amplification)
        minus_btn = QPushButton("−")
        minus_btn.setMinimumSize(40, 35)
        minus_btn.setMaximumSize(40, 35)
        minus_btn.setStyleSheet("""
            QPushButton {
                background: #3498db; 
                color: white; 
                border-radius: 6px;
                font-weight: bold; 
                font-size: 18pt;
                border: 2px solid #2980b9;
            }
            QPushButton:hover { 
                background: #2980b9; 
            }
            QPushButton:pressed {
                background: #21618c;
            }
        """)
        minus_btn.clicked.connect(self.decrease_amplification)
        control_layout.addWidget(minus_btn)
        
        # Amplification display
        self.amp_label = QLabel(f"{self.amplification:.2f}x")
        self.amp_label.setMinimumWidth(60)
        self.amp_label.setAlignment(Qt.AlignCenter)
        self.amp_label.setStyleSheet("""
            color: #2c3e50; 
            font-weight: bold; 
            font-size: 12pt;
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            padding: 5px;
        """)
        control_layout.addWidget(self.amp_label)
        
        # + Button (Increase amplification)
        plus_btn = QPushButton("+")
        plus_btn.setMinimumSize(40, 35)
        plus_btn.setMaximumSize(40, 35)
        plus_btn.setStyleSheet("""
            QPushButton {
                background: #3498db; 
                color: white; 
                border-radius: 6px;
                font-weight: bold; 
                font-size: 18pt;
                border: 2px solid #2980b9;
            }
            QPushButton:hover { 
                background: #2980b9; 
            }
            QPushButton:pressed {
                background: #21618c;
            }
        """)
        plus_btn.clicked.connect(self.increase_amplification)
        control_layout.addWidget(plus_btn)
        
        # Reset Button
        reset_btn = QPushButton("Reset")
        reset_btn.setMinimumSize(60, 35)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6; 
                color: white; 
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold; 
                font-size: 10pt;
                border: 2px solid #7f8c8d;
            }
            QPushButton:hover { 
                background: #7f8c8d; 
            }
        """)
        reset_btn.clicked.connect(self.reset_amplification)
        control_layout.addWidget(reset_btn)
        
        # Info label
        info_label = QLabel("💡 Use mouse scroll to zoom")
        info_label.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 9pt;
            font-style: italic;
            background: transparent;
            border: none;
        """)
        control_layout.addWidget(info_label)
        
        control_layout.addStretch()

        startstop_layout = QHBoxLayout()
        startstop_layout.addStretch()
        
        # Start Button for Expanded Lead View
        self.expanded_start_btn = QPushButton("Start")
        self.expanded_start_btn.setMinimumSize(100, 40)
        self.expanded_start_btn.setStyleSheet("""
            QPushButton {
                background: #28a745; 
                color: white; 
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold; 
                font-size: 11pt;
                border: 2px solid #218838;
            }
            QPushButton:hover { 
                background: #218838; 
            }
            QPushButton:pressed {
                background: #1e7e34;
            }
            QPushButton:disabled {
                background: #6c757d;
                border: 2px solid #6c757d;
            }
        """)
        self.expanded_start_btn.clicked.connect(self.start_parent_acquisition)
        startstop_layout.addWidget(self.expanded_start_btn)
        
        # Stop Button for Expanded Lead View
        self.expanded_stop_btn = QPushButton("Stop")
        self.expanded_stop_btn.setMinimumSize(100, 40)
        self.expanded_stop_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545; 
                color: white; 
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold; 
                font-size: 11pt;
                border: 2px solid #c82333;
            }
            QPushButton:hover { 
                background: #c82333; 
            }
            QPushButton:pressed {
                background: #bd2130;
            }
            QPushButton:disabled {
                background: #6c757d;
                border: 2px solid #6c757d;
            }
        """)
        self.expanded_stop_btn.clicked.connect(self.stop_parent_acquisition)
        startstop_layout.addWidget(self.expanded_stop_btn)
        
        plot_layout.addLayout(startstop_layout)
        
        plot_layout.addWidget(control_frame)
        
        parent_layout.addWidget(plot_frame, 7) # Plot takes ~70% of horizontal space

    # Amplification functions

    def increase_amplification(self):
        """Increase amplification by 20%"""
        self.amplification *= 1.2
        self.amplification = min(self.max_amplification, self.amplification)
        if hasattr(self, 'amp_label'):
            self.amp_label.setText(f"{self.amplification:.2f}x")
        self.update_plot()
        print(f"✅ Amplification increased to {self.amplification:.2f}x")

    def decrease_amplification(self):
        """Decrease amplification by 20%"""
        self.amplification /= 1.2
        self.amplification = max(self.min_amplification, self.amplification)
        if hasattr(self, 'amp_label'):
            self.amp_label.setText(f"{self.amplification:.2f}x")
        self.update_plot()
        print(f"✅ Amplification decreased to {self.amplification:.2f}x")

    def reset_amplification(self):
        """Reset amplification to default (1.0x)"""
        self.amplification = 1.0
        if hasattr(self, 'amp_label'):
            self.amp_label.setText(f"{self.amplification:.2f}x")
        self.update_plot()
        print("✅ Amplification reset to 1.00x")
    
    def setup_ecg_plot(self):
        """Setup the ECG plot with proper styling"""
        if len(self.ecg_data) == 0:
            self.ax.text(0.5, 0.5, 'No ECG Data Available', 
                        transform=self.ax.transAxes, ha='center', va='center',
                        fontsize=16, color='gray')
            return
        
        # Calculate time axis based on demo mode or normal mode
        if self.demo_mode_active and self.demo_manager:
            # Demo mode: use time window from demo manager
            try:
                time_window = self.demo_manager.time_window
                num_samples = len(self.ecg_data)
                time = np.linspace(0, time_window, num_samples)
            except Exception as e:
                print(f"⚠️ Error getting demo time window in setup: {e}")
                time = np.arange(len(self.ecg_data)) / self.sampling_rate
        else:
            # Normal mode: calculate time window based on wave speed (same as 12-lead view)
            try:
                parent = self.parent()
                if parent and hasattr(parent, 'settings_manager'):
                    wave_speed = float(parent.settings_manager.get_wave_speed())
                    # Calculate time window based on wave speed (same logic as 12-lead view)
                    baseline_seconds = 10.0
                    seconds_scale = (25.0 / max(1e-6, wave_speed))
                    time_window = baseline_seconds * seconds_scale
                    
                    # Create time axis that matches the time window
                    num_samples = len(self.ecg_data)
                    time = np.linspace(0, time_window, num_samples)
                else:
                    # Fallback: use sampling rate if settings not available
                    time = np.arange(len(self.ecg_data)) / self.sampling_rate
            except Exception as e:
                print(f"⚠️ Error calculating time window in setup: {e}")
                # Fallback: use sampling rate
                time = np.arange(len(self.ecg_data)) / self.sampling_rate
        
        # Plot at 1.0x to establish baseline
        scaled = self.ecg_data * self.display_gain * 1.0  # Use 1.0x for baseline
        
        # Calculate and store the baseline (mean) for proper zooming
        self.signal_baseline = np.mean(scaled)
        
        self.ax.plot(time, scaled, color='#0984e3', linewidth=1.0, label='ECG Signal')
        
        self.ax.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold', color='#34495e')
        self.ax.set_ylabel('Amplitude (mV)', fontsize=14, fontweight='bold', color='#34495e')
        
        # Add demo mode or wave speed info to title
        if self.demo_mode_active and self.demo_manager:
            mode_text = f" [{self.demo_manager.current_wave_speed}mm/s]"
        else:
            # Show wave speed for normal mode too
            try:
                parent = self.parent()
                if parent and hasattr(parent, 'settings_manager'):
                    wave_speed = float(parent.settings_manager.get_wave_speed())
                    mode_text = f" [{wave_speed:.1f}mm/s]"
                else:
                    mode_text = ""
            except Exception:
                mode_text = ""
        self.ax.set_title(f'Lead {self.lead_name} - PQRST Analysis{mode_text}', 
                         fontsize=18, fontweight='bold', color='#2c3e50')
        
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#bdc3c7')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        self.ax.set_xlim(0, max(time) if len(time) > 0 else 1)
        
        # Store fixed y-limits based on original data (1.0x amplification)
        if len(self.ecg_data) > 0:
            y_margin = (np.max(scaled) - np.min(scaled)) * 0.1
            y_min = np.min(scaled) - y_margin
            y_max = np.max(scaled) + y_margin
            self.fixed_ylim = (y_min, y_max)
            self.ax.set_ylim(y_min, y_max)

        if hasattr(self, 'canvas'):
            self.canvas.draw()
    
    def create_metrics_panel(self, parent_layout):
        """Create the metrics panel"""
        # A container frame for the entire right-side panel
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        # Let this panel be responsive; width controlled by stretch factors
        metrics_frame.setMinimumWidth(300)
        metrics_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # The scroll area allows content to overflow vertically
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                background: transparent; 
                border: none; 
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 25px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # A widget that will sit inside the scroll area and hold the layout
        metrics_container_widget = QWidget()
        metrics_container_widget.setStyleSheet("background: transparent;")

        # A vertical layout for a single column of cards
        self.metrics_vbox = QVBoxLayout(metrics_container_widget)
        self.metrics_vbox.setContentsMargins(10, 10, 5, 10)
        self.metrics_vbox.setSpacing(12)

        self.metrics_cards = {}
        self.create_metrics_cards()

        scroll_area.setWidget(metrics_container_widget)

        # The main layout for the right panel
        main_metrics_layout = QVBoxLayout(metrics_frame)
        main_metrics_layout.setContentsMargins(0, 0, 0, 0)
        main_metrics_layout.addWidget(scroll_area)

        parent_layout.addWidget(metrics_frame, 3) # Metrics panel takes 30% of horizontal space
    
    def create_metrics_cards(self):
        """Create individual metric cards"""
        # Include Heart Rate and R-R Interval display as requested
        metrics = [
            ("Heart Rate", 0, "bpm", "#e74c3c"),
            ("RR Interval", 0, "ms", "#2980b9"),
            ("PR Interval", 0, "ms", "#8e44ad"),
            ("QRS Duration", 0, "ms", "#27ae60"),
            ("P Duration", 0, "ms", "#16a085"),
        ]
        
        for i, (title, value, unit, color) in enumerate(metrics):
            card = MetricsCard(title, value, unit, color)
            self.metrics_cards[title.lower().replace(" ", "_")] = card
            self.metrics_vbox.addWidget(card)
        
        # Add a stretch at the end
        self.metrics_vbox.addStretch(1)
        
        # Initialize with some default values for testing
        self.update_metric('heart_rate', 0)
        self.update_metric('rr_interval', 0)
        self.update_metric('pr_interval', 0)
        self.update_metric('qrs_duration', 0)
        self.update_metric('p_duration', 0)
    
    def start_live_mode(self):
        """Start live data updates"""
        self.is_live = True
        self.timer.start(100)  # Update every 100ms
    
    def on_wave_speed_changed(self):
        """Handle wave speed changes in both demo mode and normal mode"""
        try:
            parent = self.parent()
            if not parent:
                return
            
            if self.demo_mode_active and self.demo_manager:
                # Demo mode: update demo manager's wave speed settings
                try:
                    self.demo_manager._update_wave_speed_settings()
                    # Force an update to reflect the new wave speed
                    self.update_plot()
                    print(f"🎬 Expanded view: Wave speed updated to {self.demo_manager.current_wave_speed}mm/s")
                except Exception as e:
                    print(f"⚠️ Error updating wave speed in expanded view (demo mode): {e}")
            else:
                # Normal mode: force an update to reflect the new wave speed
                try:
                    if hasattr(parent, 'settings_manager'):
                        wave_speed = float(parent.settings_manager.get_wave_speed())
                        # Force update to apply new wave speed
                        self.update_plot()
                        print(f"📊 Expanded view: Wave speed updated to {wave_speed:.1f}mm/s")
                except Exception as e:
                    print(f"⚠️ Error updating wave speed in expanded view (normal mode): {e}")
        except Exception as e:
            print(f"⚠️ Error updating wave speed in expanded view: {e}")

    def resizeEvent(self, event):
        """Respond to window resizing by scaling fonts and components."""
        try:
            # Baseline matches initial size above
            base_w, base_h = 1400.0, 900.0
            cur_w, cur_h = max(1, self.width()), max(1, self.height())
            scale = min(cur_w / base_w, cur_h / base_h)

            # Scale metric cards
            for card in getattr(self, 'metrics_cards', {}).values():
                if hasattr(card, 'set_scale'):
                    card.set_scale(scale)
        except Exception:
            pass
        super().resizeEvent(event)
    
    def stop_live_mode(self):
        """Stop live data updates"""
        self.is_live = False
        self.timer.stop()
    
    def update_live_data(self):
        """Update ECG data from parent (hardware or demo)"""
        if not self.is_live or not hasattr(self, 'parent') or self.parent() is None:
            return
        
        try:
            # Get current data from parent ECG test page
            parent = self.parent()
            
            # Check if demo mode is active - update flag
            if hasattr(parent, 'demo_toggle'):
                self.demo_mode_active = parent.demo_toggle.isChecked()
                if hasattr(parent, 'demo_manager'):
                    self.demo_manager = parent.demo_manager
            
            # Align sampling rate with parent so HR/RR match dashboard
            try:
                if hasattr(parent, 'sampler') and getattr(parent.sampler, 'sampling_rate', 0):
                    self.sampling_rate = float(parent.sampler.sampling_rate)
                    self.analyzer.fs = self.sampling_rate
                    self.arrhythmia_detector.fs = self.sampling_rate
                elif hasattr(parent, 'sampling_rate') and parent.sampling_rate:
                    self.sampling_rate = float(parent.sampling_rate)
                    self.analyzer.fs = self.sampling_rate
                    self.arrhythmia_detector.fs = self.sampling_rate
            except Exception:
                pass
            
            if hasattr(parent, 'data') and len(parent.data) > 0:
                # Find the lead index for this lead
                lead_index = self.get_lead_index()
                if lead_index is not None and lead_index < len(parent.data):
                    new_data = parent.data[lead_index]
                    if len(new_data) > 0:
                        # In demo mode, apply wave speed and gain adjustments
                        if self.demo_mode_active and self.demo_manager:
                            # Get wave speed settings from demo manager
                            try:
                                current_wave_speed = self.demo_manager.current_wave_speed
                                time_window = self.demo_manager.time_window
                                samples_per_second = self.demo_manager.samples_per_second
                                
                                # Calculate number of samples to show based on wave speed
                                num_samples_to_show = max(1, int(time_window * samples_per_second))
                                
                                # Get the most recent samples matching the time window
                                # This ensures R peaks align with main view
                                data_array = np.array(new_data)
                                total_len = len(data_array)
                                
                                if total_len > 0:
                                    # Use the same data pointer logic as demo mode for consistency
                                    data_ptr = getattr(self.demo_manager, 'data_ptr', 0)
                                    start = int(data_ptr % total_len)
                                    idx = (start + np.arange(num_samples_to_show)) % total_len
                                    data_slice = data_array[idx]
                                    
                                    # Apply wave gain from demo settings (same as main view)
                                    try:
                                        if hasattr(parent, 'settings_manager'):
                                            current_gain = float(parent.settings_manager.get_wave_gain()) / 10.0
                                            
                                            # Reduce amplification for 20mm/mV to prevent clipping in expanded view (demo mode only)
                                            if current_gain >= 2.0:  # 20mm/mV or higher
                                                reduction_factor = 0.55  # Reduce to 55% to prevent clipping
                                                current_gain = current_gain * reduction_factor
                                                print(f"🎬 Expanded view: Reduced gain to {current_gain:.2f}x (from 2.0x) to prevent clipping at 20mm/mV")
                                        else:
                                            current_gain = 0.5
                                        
                                        # Apply the gain to the data slice
                                        self.ecg_data = data_slice * current_gain
                                        print(f"🎬 Expanded view: Applied wave gain={current_gain:.2f}x to demo data")
                                    except Exception as gain_err:
                                        print(f"⚠️ Error applying wave gain in expanded view: {gain_err}")
                                        self.ecg_data = data_slice
                                    
                                    # Update sampling rate to match demo
                                    self.sampling_rate = samples_per_second
                                    self.analyzer.fs = self.sampling_rate
                                    self.arrhythmia_detector.fs = self.sampling_rate
                                    
                                    print(f"🎬 Expanded view demo: wave_speed={current_wave_speed}, time_window={time_window:.1f}s, samples={num_samples_to_show}, gain={current_gain:.2f}x")
                                else:
                                    self.ecg_data = np.array(new_data)
                            except Exception as e:
                                print(f"⚠️ Error applying demo settings in expanded view: {e}")
                                self.ecg_data = np.array(new_data)
                        else:
                            # Normal mode (serial data) - apply wave speed-based time window
                            try:
                                # Get wave speed from settings manager (same as 12-lead view)
                                if hasattr(parent, 'settings_manager'):
                                    wave_speed = float(parent.settings_manager.get_wave_speed())
                                else:
                                    wave_speed = 25.0  # Default
                                
                                # Calculate time window based on wave speed (same logic as 12-lead view)
                                # 12.5 mm/s → 20 s window (more peaks visible - compressed)
                                # 25 mm/s → 10 s window (default)
                                # 50 mm/s → 5 s window (fewer peaks visible - stretched)
                                baseline_seconds = 10.0
                                seconds_scale = (25.0 / max(1e-6, wave_speed))
                                seconds_to_show = baseline_seconds * seconds_scale
                                
                                # Calculate number of samples to show based on wave speed
                                sampling_rate = 80.0  # Hardware sampling rate (same as 12-lead view)
                                samples_to_show = int(sampling_rate * seconds_to_show)
                                
                                # Take only the most recent samples_to_show from the buffer
                                data_array = np.array(new_data)
                                if len(data_array) > samples_to_show:
                                    data_slice = data_array[-samples_to_show:]
                                else:
                                    data_slice = data_array
                                
                                # Do NOT apply wave gain for real serial data - amplification is available instead
                                self.ecg_data = data_slice
                                print(f"📊 Expanded view serial: wave_speed={wave_speed:.1f}mm/s, time_window={seconds_to_show:.1f}s, samples={len(data_slice)}")
                            except Exception as e:
                                print(f"⚠️ Error applying wave speed in expanded view (normal mode): {e}")
                                # Fallback: use all data if calculation fails
                                self.ecg_data = np.array(new_data)
                        
                        self.update_plot()
                        self.analyze_ecg()

                        # Update button states to reflect parent's status
                        if hasattr(self, 'expanded_start_btn'):
                            self.update_button_states()

        except Exception as e:
            print(f"Error updating live data: {e}")
    
    def get_lead_index(self):
        """Get the lead index for this lead name"""
        lead_mapping = {
            'I': 0, 'II': 1, 'III': 2, 'aVR': 3, 'aVL': 4, 'aVF': 5,
            'V1': 6, 'V2': 7, 'V3': 8, 'V4': 9, 'V5': 10, 'V6': 11
        }
        return lead_mapping.get(self.lead_name)
    
    def update_plot(self):
        """Update the ECG plot with new data"""
        if len(self.ecg_data) == 0:
            return
        
        try:
            # Clear the plot
            self.ax.clear()
            
            # Apply amplification around the baseline, not around 0
            # This keeps the signal centered during zoom
            
            # Calculate time axis based on demo mode or normal mode
            if self.demo_mode_active and self.demo_manager:
                # Demo mode: use time window from demo manager for correct wave speed display
                try:
                    time_window = self.demo_manager.time_window
                    num_samples = len(self.ecg_data)
                    # Create time axis that matches the time window
                    time = np.linspace(0, time_window, num_samples)
                except Exception as e:
                    print(f"⚠️ Error getting demo time window: {e}")
                    time = np.arange(len(self.ecg_data)) / self.sampling_rate
            else:
                # Normal mode: calculate time window based on wave speed (same as 12-lead view)
                try:
                    parent = self.parent()
                    if parent and hasattr(parent, 'settings_manager'):
                        wave_speed = float(parent.settings_manager.get_wave_speed())
                        # Calculate time window based on wave speed (same logic as 12-lead view)
                        baseline_seconds = 10.0
                        seconds_scale = (25.0 / max(1e-6, wave_speed))
                        time_window = baseline_seconds * seconds_scale
                        
                        # Create time axis that matches the time window
                        num_samples = len(self.ecg_data)
                        time = np.linspace(0, time_window, num_samples)
                    else:
                        # Fallback: use sampling rate if settings not available
                        time = np.arange(len(self.ecg_data)) / self.sampling_rate
                except Exception as e:
                    print(f"⚠️ Error calculating time window for normal mode: {e}")
                    # Fallback: use sampling rate
                    time = np.arange(len(self.ecg_data)) / self.sampling_rate
            
            base_scaled = self.ecg_data * self.display_gain
            
            # Update baseline if data changed
            self.signal_baseline = np.mean(base_scaled)
            
            # Zoom around the baseline: baseline + (signal - baseline) * amplification
            scaled = self.signal_baseline + (base_scaled - self.signal_baseline) * self.amplification
            
            self.ax.plot(time, scaled, color='#0984e3', linewidth=1.0, label='ECG Signal')
            
            # Update labels and styling
            self.ax.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold', color='#34495e')
            self.ax.set_ylabel('Amplitude (mV)', fontsize=14, fontweight='bold', color='#34495e')
            
            # Show amplification and wave speed info in title
            amp_text = f" (Zoom: {self.amplification:.2f}x)" if self.amplification != 1.0 else ""
            if self.demo_mode_active and self.demo_manager:
                mode_text = f" [{self.demo_manager.current_wave_speed}mm/s]"
            else:
                # Show wave speed for normal mode too
                try:
                    parent = self.parent()
                    if parent and hasattr(parent, 'settings_manager'):
                        wave_speed = float(parent.settings_manager.get_wave_speed())
                        mode_text = f" [{wave_speed:.1f}mm/s]"
                    else:
                        mode_text = ""
                except Exception:
                    mode_text = ""
            self.ax.set_title(f'Lead {self.lead_name} - Live PQRST Analysis{amp_text}{mode_text}', 
                            fontsize=18, fontweight='bold', color='#2c3e50')
            
            # Grid and styling
            self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#bdc3c7')
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            # Set x limits
            self.ax.set_xlim(0, max(time) if len(time) > 0 else 1)
            
            # FIXED Y-AXIS: Always use the same y-limits regardless of amplification
            # This makes the wave appear to zoom in/out while staying centered
            if self.fixed_ylim is not None:
                self.ax.set_ylim(self.fixed_ylim[0], self.fixed_ylim[1])
            elif len(self.ecg_data) > 0 and self.fixed_ylim is None:
                # Fallback: calculate and store fixed limits if not set
                baseline_scaled = self.ecg_data * self.display_gain * 1.0
                self.signal_baseline = np.mean(baseline_scaled)
                y_margin = (np.max(baseline_scaled) - np.min(baseline_scaled)) * 0.1
                y_min = np.min(baseline_scaled) - y_margin
                y_max = np.max(baseline_scaled) + y_margin
                self.fixed_ylim = (y_min, y_max)
                self.ax.set_ylim(y_min, y_max)
            
            # Redraw
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating plot: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_live_mode()
        event.accept()

    # Start/Stop Acquisition from Expanded Lead View

    def start_parent_acquisition(self):
        """Start serial data acquisition from parent ECG test page"""
        try:
            parent = self.parent()
            
            # Check if demo mode is active - prevent starting if it is
            if parent and hasattr(parent, 'demo_toggle') and parent.demo_toggle.isChecked():
                QMessageBox.warning(self, "Demo Mode Active", 
                    "Cannot start serial acquisition while Demo mode is ON.\n\n"
                    "Please turn off Demo mode first to use real serial data.")
                print("Cannot start acquisition - Demo mode is active")
                return
            
            if parent and hasattr(parent, 'start_acquisition'):
                print("Starting acquisition from expanded lead view...")
                parent.start_acquisition()
                
                # Update button states
                self.expanded_start_btn.setEnabled(False)
                self.expanded_stop_btn.setEnabled(True)
                
                # Ensure live mode is active for this view
                if not self.is_live:
                    self.start_live_mode()
                    
                print("✅ Acquisition started successfully from expanded view")
            else:
                QMessageBox.warning(self, "Error", 
                    "Cannot start acquisition. Parent ECG page not found.")
                print("Parent ECG test page not available")
        except Exception as e:
            print(f"Error starting acquisition from expanded view: {e}")
            QMessageBox.warning(self, "Error", 
                f"Failed to start acquisition: {str(e)}")
    
    def stop_parent_acquisition(self):
        """Stop serial data acquisition from parent ECG test page"""
        try:
            parent = self.parent()
            if parent and hasattr(parent, 'stop_acquisition'):
                print("⏹️ Stopping acquisition from expanded lead view...")
                parent.stop_acquisition()
                
                # Update button states
                self.expanded_start_btn.setEnabled(True)
                self.expanded_stop_btn.setEnabled(False)
                
                print("✅ Acquisition stopped successfully from expanded view")
            else:
                QMessageBox.warning(self, "Error", 
                    "Cannot stop acquisition. Parent ECG page not found.")
                print("❌ Parent ECG test page not available")
        except Exception as e:
            print(f"❌ Error stopping acquisition from expanded view: {e}")
            QMessageBox.warning(self, "Error", 
                f"Failed to stop acquisition: {str(e)}")
    
    def update_button_states(self):
        """Update start/stop button states based on parent acquisition status"""
        try:
            parent = self.parent()
            
            # Check if demo mode is active
            is_demo_mode = False
            if parent and hasattr(parent, 'demo_toggle'):
                is_demo_mode = parent.demo_toggle.isChecked()
            
            # Hide buttons if demo mode is ON, show if OFF
            if hasattr(self, 'expanded_start_btn') and hasattr(self, 'expanded_stop_btn'):
                if is_demo_mode:
                    # Demo mode is ON - hide the buttons
                    self.expanded_start_btn.setVisible(False)
                    self.expanded_stop_btn.setVisible(False)
                    print("Demo mode ON - Start/Stop buttons hidden in expanded view")
                else:
                    # Demo mode is OFF - show the buttons and update their states
                    self.expanded_start_btn.setVisible(True)
                    self.expanded_stop_btn.setVisible(True)
                    
                    # Update enabled/disabled state based on acquisition status
                    if parent and hasattr(parent, 'timer'):
                        is_running = parent.timer.isActive()
                        self.expanded_start_btn.setEnabled(not is_running)
                        self.expanded_stop_btn.setEnabled(is_running)
                    else:
                        # Default state if parent not available
                        self.expanded_start_btn.setEnabled(True)
                        self.expanded_stop_btn.setEnabled(False)
                    
                    print("Demo mode OFF - Start/Stop buttons visible in expanded view")
        except Exception as e:
            print(f"Error updating button states: {e}")
    
    def create_arrhythmia_panel(self, parent_layout):
        """Create the arrhythmia analysis panel"""
        arrhythmia_frame = QFrame()
        arrhythmia_frame.setFixedHeight(70)
        arrhythmia_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        arrhythmia_layout = QHBoxLayout(arrhythmia_frame)
        arrhythmia_layout.setContentsMargins(15, 10, 15, 10)
        arrhythmia_layout.setSpacing(15)
        
        title = QLabel("Rhythm Interpretation:")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; border: none; background: transparent;")
        arrhythmia_layout.addWidget(title)
        
        self.arrhythmia_list = QLabel("Analyzing...")
        self.arrhythmia_list.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.arrhythmia_list.setStyleSheet("color: #34495e; border: none; background: transparent;")
        self.arrhythmia_list.setWordWrap(True)
        self.arrhythmia_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        arrhythmia_layout.addWidget(self.arrhythmia_list, 1)
        
        parent_layout.addWidget(arrhythmia_frame)
    
    def analyze_ecg(self):
        """Analyze the ECG signal and update metrics"""
        if self.ecg_data.size == 0:
            self.arrhythmia_list.setText("No data to analyze.")
            return
        
        try:
            analysis = self.analyzer.analyze_signal(self.ecg_data)
            self.calculate_metrics(analysis)
            
            arrhythmias = self.arrhythmia_detector.detect_arrhythmias(self.ecg_data, analysis['r_peaks'])
            self.update_arrhythmia_display(arrhythmias)
            
            self.update_plot_with_markers(analysis)
        except Exception as e:
            print(f"Error in ECG analysis: {e}")
            self.arrhythmia_list.setText("An error occurred during analysis.")
    
    def calculate_metrics(self, analysis):
        """Calculate ECG metrics from analysis results"""
        try:
            # Check if demo mode is active from parent
            parent = self._parent if hasattr(self, '_parent') else None
            is_demo_mode = False
            if parent is not None and hasattr(parent, 'demo_toggle'):
                is_demo_mode = parent.demo_toggle.isChecked()
            
            # If demo mode is active, use fixed demo values
            if is_demo_mode:
                self.update_metric('heart_rate', 60)
                self.update_metric('rr_interval', 1000)
                self.update_metric('pr_interval', 160)
                self.update_metric('qrs_duration', 85)
                self.update_metric('p_duration', 80)
                return
            
            # Otherwise, calculate from real data
            r_peaks, p_peaks, q_peaks, s_peaks, t_peaks = (
                analysis['r_peaks'], analysis['p_peaks'], analysis['q_peaks'],
                analysis['s_peaks'], analysis['t_peaks']
            )
            
            # Heart Rate & RR Interval - use same calculation as 12-lead page if available
            heart_rate = 0
            if parent is not None and hasattr(parent, 'calculate_heart_rate'):
                try:
                    heart_rate = int(parent.calculate_heart_rate(self.ecg_data))
                    self.update_metric('heart_rate', max(0, heart_rate))
                    self.update_metric('rr_interval', int(60000 / heart_rate) if heart_rate > 0 else 0)
                except Exception:
                    heart_rate = 0
            else:
                if len(r_peaks) > 1:
                    rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
                    mean_rr = np.mean(rr_intervals)
                    heart_rate = 60000 / mean_rr if mean_rr > 0 else 0
                    self.update_metric('heart_rate', int(heart_rate))
                    self.update_metric('rr_interval', int(mean_rr))
            
            # PR Interval
            if len(p_peaks) > 0 and len(q_peaks) > 0:
                # A more robust PR interval is P-onset to Q-onset
                # Simplified: p_peak to q_peak
                pr_intervals = [(q - p) / self.sampling_rate * 1000 for p, q in zip(p_peaks, q_peaks) if q > p]
                if pr_intervals:
                    self.update_metric('pr_interval', int(np.mean(pr_intervals)))
            
            # QRS Duration
            if len(q_peaks) > 0 and len(s_peaks) > 0:
                qrs_durations = [(s - q) / self.sampling_rate * 1000 for q, s in zip(q_peaks, s_peaks) if s > q]
                if qrs_durations:
                    self.update_metric('qrs_duration', int(np.mean(qrs_durations)))
            
            # QTc Interval (Bazett's formula)
            if 'rr_interval' in self.metrics_cards and self.metrics_cards['rr_interval'].value > 0:
                rr_sec = self.metrics_cards['rr_interval'].value / 1000.0
                # Simplified QT, actual QT needs T-wave end detection
                qt_interval_ms = 380 # Assuming a typical QT
                qtc = qt_interval_ms / np.sqrt(rr_sec) if rr_sec > 0 else 0
                self.update_metric('qtc_interval', int(qtc))

            # P Duration (simplified)
            self.update_metric('p_duration', 80) # Typical duration
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
    
    def update_metric(self, metric_name, value):
        """Update a specific metric card"""
        if metric_name in self.metrics_cards:
            self.metrics_cards[metric_name].update_value(value)
    
    def update_arrhythmia_display(self, arrhythmias):
        """Update the arrhythmia display"""
        arrhythmia_text = ", ".join(arrhythmias) if arrhythmias else "No specific arrhythmia detected."
        self.arrhythmia_list.setText(arrhythmia_text)
        
        # Color code based on severity
        is_normal = "Normal Sinus Rhythm" in arrhythmia_text
        self.arrhythmia_list.setStyleSheet(f"""
            color: {'#2ecc71' if is_normal else '#e74c3c'};
            font-weight: bold;
            border: none;
        """)
    
    def update_plot_with_markers(self, analysis):
        """Update the plot without PQRST labels/markers (as requested)"""
        if self.ecg_data.size == 0:
            return

        try:
            # Remove any previously drawn markers/labels and do not add new ones
            while len(self.ax.collections) > 0:
                self.ax.collections.pop()
            while len(self.ax.texts) > 0:
                self.ax.texts.pop()

            # Ensure no legend is shown
            leg = self.ax.get_legend()
            if leg is not None:
                leg.remove()

            self.canvas.draw()

        except Exception as e:
            print(f"Error updating plot markers: {e}")

def show_expanded_lead_view(lead_name, ecg_data, sampling_rate=500, parent=None):
    """Show the expanded lead view dialog"""
    dialog = ExpandedLeadView(lead_name, ecg_data, sampling_rate, parent)
    dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create more realistic sample ECG data
    fs = 500
    duration = 5 # seconds
    t = np.linspace(0, duration, duration * fs, endpoint=False)
    
    # P wave
    p_wave = 0.1 * np.exp(-((t % 1 - 0.25)**2) / 0.005)
    # QRS complex
    qrs_complex = 1.0 * np.exp(-((t % 1 - 0.4)**2) / 0.002) - 0.3 * np.exp(-((t % 1 - 0.37)**2) / 0.001) - 0.2 * np.exp(-((t % 1 - 0.43)**2) / 0.001)
    # T wave
    t_wave = 0.3 * np.exp(-((t % 1 - 0.6)**2) / 0.01)
    # Noise
    noise = 0.03 * np.random.randn(len(t))
    
    sample_ecg = p_wave + qrs_complex + t_wave + noise
    
    dialog = ExpandedLeadView("Lead II", sample_ecg, fs)
    dialog.show()
    
    sys.exit(app.exec_())
