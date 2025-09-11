import sys
import time
import numpy as np
import serial
import serial.tools.list_ports
import csv
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QGroupBox, QFileDialog,
    QStackedLayout, QGridLayout, QSizePolicy, QMessageBox, QFormLayout, QLineEdit, QFrame, QApplication, QDialog
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QDateTime
# --- CHANGED: Removed Matplotlib imports ---

# --- ADDED: PyQtGraph is now used for all plotting ---
import pyqtgraph as pg
from ecg.recording import ECGMenu
from scipy.signal import find_peaks
from utils.settings_manager import SettingsManager
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from functools import partial # For plot clicking

# (The classes SamplingRateCalculator, SerialECGReader, and DetailWindow from your first script remain the same)
# ... paste them here ...
# --- Configuration ---
HISTORY_LENGTH = 1000
NORMAL_HR_MIN, NORMAL_HR_MAX = 60, 100
LEAD_LABELS = [
    "I", "II", "III", "aVR", "aVL", "aVF",
    "V1", "V2", "V3", "V4", "V5", "V6"
]

class SamplingRateCalculator:
    def __init__(self, update_interval_sec=5):
        self.sample_count = 0
        self.last_update_time = time.monotonic()
        self.update_interval = update_interval_sec
        self.sampling_rate = 0

    def add_sample(self):
        self.sample_count += 1
        current_time = time.monotonic()
        elapsed = current_time - self.last_update_time
        if elapsed >= self.update_interval:
            self.sampling_rate = self.sample_count / elapsed
            self.sample_count = 0
            self.last_update_time = current_time
        return self.sampling_rate

class SerialECGReader:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.running = False
        self.data_count = 0
        print(f"🔌 SerialECGReader initialized: Port={port}, Baud={baudrate}")

    def start(self):
        print("🚀 Starting ECG data acquisition...")
        self.ser.reset_input_buffer()
        time.sleep(0.1)
        self.running = True
        print("✅ ECG device started - waiting for data...")

    def stop(self):
        print("⏹️ Stopping ECG data acquisition...")
        self.running = False
        print(f"📊 Total data packets received: {self.data_count}")

    def read_value(self):
        if not self.running:
            return None
        try:
            line_raw = self.ser.readline()
            line_data = line_raw.decode('utf-8', errors='replace').strip()

            if line_data:
                self.data_count += 1
                try:
                    values = [int(x) for x in line_data.split() if x.strip()]
                    if len(values) >= 8:
                        lead1_val, v4_val, v5_val, lead2_val, v3_val, v6_val, v1_val, v2_val = values[:8]
                        lead3_val = lead2_val - lead1_val
                        avr_val = -(lead1_val + lead2_val) / 2
                        avl_val = lead1_val - (lead2_val / 2)
                        avf_val = lead2_val - (lead1_val / 2)
                        all_12_leads = [lead1_val, lead2_val, lead3_val, avr_val, avl_val, avf_val,
                                        v1_val, v2_val, v3_val, v4_val, v5_val, v6_val]
                        return all_12_leads
                except (ValueError, IndexError):
                    pass
            return None
        except Exception as e:
            print(f"❌ Serial communication error: {e}")
        return None

    def close(self):
        print("🔌 Closing serial connection...")
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("✅ Serial connection closed")

class DetailWindow(QWidget):
    def __init__(self, title, signal_data, sampling_rate, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detail View - {title}")
        self.setGeometry(150, 150, 800, 500)
        self.parent_monitor = parent
        self.lead_index = LEAD_LABELS.index(title) if title in LEAD_LABELS else 0
        self.sampling_rate = sampling_rate
        layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Sample Number')
        self.plot_widget.setTitle(f"{title} - Live View", color="k", size="16pt")
        layout.addWidget(self.plot_widget)
        self.data_line = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2))
        self.r_peaks_scatter = self.plot_widget.plot([], [], pen=None, symbol='o', symbolBrush='r', symbolSize=8)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_plot)
        self.timer.start(50)
        if len(signal_data) > 0:
            self.data_line.setData(signal_data)

    def update_live_plot(self):
        if self.parent_monitor and hasattr(self.parent_monitor, 'data'):
            current_data = self.parent_monitor.data[self.lead_index]
            if len(current_data) > 0:
                self.data_line.setData(current_data)
                if len(current_data) > 100:
                    self.plot_widget.setXRange(len(current_data) - 200, len(current_data))

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

# --- THIS IS THE CORRECTED CLASS ---
class ECGTestPage(QWidget):
    LEADS_MAP = {
        "Lead II ECG Test": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "Lead III ECG Test": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "7 Lead ECG Test": ["V1", "V2", "V3", "V4", "V5", "V6", "II"],
        "12 Lead ECG Test": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "ECG Live Monitoring": ["II"]
    }

    def __init__(self, test_name, stacked_widget):
        super().__init__()
        self.test_name = test_name
        self.leads = self.LEADS_MAP[test_name]
        self.stacked_widget = stacked_widget
        self.settings_manager = SettingsManager()
        self.serial_reader = None
        self.sampler = SamplingRateCalculator()

        # --- REPLACED: Data structure now matches the working script (list of numpy arrays) ---
        self.data = [np.zeros(HISTORY_LENGTH) for _ in range(12)]
        
        # --- All the UI setup code is the same ---
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(800, 600)
        self.setWindowTitle("12-Lead ECG Monitor")
        main_hbox = QHBoxLayout(self)
        main_hbox.setSpacing(10)
        main_hbox.setContentsMargins(8, 8, 8, 8)

        # --- Left Menu Panel Setup (unchanged) ---
        menu_container = QWidget()
        menu_container.setMinimumWidth(200)
        menu_container.setMaximumWidth(280)
        menu_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        menu_container.setStyleSheet("QWidget { background: #f8f9fa; border-right: 1px solid #dee2e6; }")
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(12, 12, 12, 12)
        menu_layout.setSpacing(8)
        header_label = QLabel("ECG Control Panel")
        header_label.setStyleSheet("QLabel { color: #ff6600; font-size: 18px; font-weight: bold; padding-bottom: 10px; border-bottom: 2px solid #ff6600; margin-bottom: 10px; }")
        header_label.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(header_label)
        
        ecg_menu_buttons = [
            ("Save ECG", lambda: print("Save clicked"), "#28a745"),
            ("Open ECG", lambda: print("Open clicked"), "#17a2b8"),
            # ... add other menu buttons as needed
        ]
        for text, handler, color in ecg_menu_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(handler)
            menu_layout.addWidget(btn)
        menu_layout.addStretch()

        # --- Right Main Content Panel ---
        main_vbox = QVBoxLayout()
        main_hbox.addWidget(menu_container, 1)
        main_hbox.addLayout(main_vbox, 5)

        # --- Metrics Frame (unchanged) ---
        self.metrics_frame = self.create_metrics_frame()
        main_vbox.addWidget(self.metrics_frame)
        
        # --- REPLACED: Matplotlib plot area is replaced with a simple QWidget container ---
        self.plot_area = QWidget()
        self.plot_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_vbox.addWidget(self.plot_area)

        # --- NEW: Create the PyQtGraph plot grid (from your working script) ---
        grid = QGridLayout(self.plot_area)
        grid.setSpacing(8)
        self.plot_widgets = []
        self.data_lines = []
        
        positions = [(i, j) for i in range(4) for j in range(3)]
        for i in range(len(self.leads)):
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('w')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)
            plot_widget.getAxis('left').setTextPen('k')
            plot_widget.getAxis('bottom').setTextPen('k')
            plot_widget.setTitle(self.leads[i], color='k', size='10pt')
            plot_widget.setYRange(-4000, 4000) # Set a generous initial Y-range
            
            # --- MAKE PLOT CLICKABLE ---
            plot_widget.scene().sigMouseClicked.connect(partial(self.plot_clicked, i))
            
            row, col = positions[i]
            grid.addWidget(plot_widget, row, col)
            data_line = plot_widget.plot(pen=pg.mkPen(color=self.LEAD_COLORS.get(self.leads[i], 'b'), width=1.5))

            self.plot_widgets.append(plot_widget)
            self.data_lines.append(data_line)
        
        self.r_peaks_scatter = self.plot_widgets[1].plot([], [], pen=None, symbol='o', symbolBrush='r', symbolSize=8)
        
        # --- Bottom Buttons (unchanged) ---
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.ports_btn = QPushButton("Ports")
        # Update button text to show current port
        current_port = self.settings_manager.get_serial_port()
        if current_port and current_port != "Select Port":
            self.ports_btn.setText(f"Port: {current_port}")
        else:
            self.ports_btn.setText("Ports")
        self.back_btn = QPushButton("Back")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.ports_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.back_btn)
        main_vbox.addLayout(btn_layout)

        # --- Connect Signals (unchanged logic) ---
        self.start_btn.clicked.connect(self.start_acquisition)
        self.stop_btn.clicked.connect(self.stop_acquisition)
        self.ports_btn.clicked.connect(self.show_ports_dialog)
        self.back_btn.clicked.connect(self.go_back)

        # --- Main Timer for Plot Updates ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)

    # --- REPLACED: This is the high-performance update function from your working script ---
    def update_plots(self):
        if not self.serial_reader or not self.serial_reader.running:
            return

        # Read a batch of data to keep up
        lines_processed = 0
        while lines_processed < 20: # Process up to 20 readings per GUI update
            all_12_leads = self.serial_reader.read_value()
            if all_12_leads:
                # Update data buffers
                for i in range(12):
                    self.data[i] = np.roll(self.data[i], -1)
                    self.data[i][-1] = all_12_leads[i]
                
                # Update sampling rate
                sampling_rate = self.sampler.add_sample()
                if sampling_rate > 0 and 'sampling_rate' in self.metric_labels:
                    self.metric_labels['sampling_rate'].setText(f"{sampling_rate:.1f} Hz")
                
                lines_processed += 1
            else:
                break # No more data in buffer

        # If we got any new data, update all plots at once
        if lines_processed > 0:
            for i in range(len(self.leads)):
                if i < len(self.data_lines):
                    self.data_lines[i].setData(self.data[i])

            # R-Peak detection and Heart Rate calculation on Lead II (index 1)
            lead_ii_data = self.data[1]
            if self.sampler.sampling_rate > 0:
                try:
                    min_distance = max(1, int(self.sampler.sampling_rate * 0.4))
                    # Adjust height threshold based on your signal's baseline and amplitude
                    mean_val = np.mean(lead_ii_data)
                    std_val = np.std(lead_ii_data)
                    peaks, _ = find_peaks(lead_ii_data, height=mean_val + 1.5 * std_val, distance=min_distance)
                    
                    self.r_peaks_scatter.setData(peaks, lead_ii_data[peaks])
                    
                    if len(peaks) >= 2:
                        bpm = (self.sampler.sampling_rate / np.mean(np.diff(peaks))) * 60
                        if 30 < bpm < 220 and 'heart_rate' in self.metric_labels:
                             self.metric_labels['heart_rate'].setText(f"{int(bpm)}")
                except Exception as e:
                    print(f"Peak detection error: {e}")

    # --- UNCHANGED METHODS BELOW ---
    def start_acquisition(self):
        port = self.settings_manager.get_serial_port()
        baud = self.settings_manager.get_baud_rate()
        if not port or not baud or port == "Select Port":
            QMessageBox.warning(self, "Configuration Error", "Please configure the serial port and baud rate first.")
            return

        try:
            self.serial_reader = SerialECGReader(port, int(baud))
            self.serial_reader.start()
            self.timer.start(50) # Update plots every 50ms (20 FPS)
            print("Acquisition started.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to start acquisition: {e}")
            self.serial_reader = None

    def stop_acquisition(self):
        self.timer.stop()
        if self.serial_reader:
            self.serial_reader.stop()
            self.serial_reader.close()
            self.serial_reader = None
        print("Acquisition stopped.")

    def plot_clicked(self, plot_index, event):
        if self.sampler.sampling_rate > 0:
            lead_name = self.leads[plot_index]
            lead_data = self.data[plot_index]
            # Create and show the detail window
            self.detail_view = DetailWindow(lead_name, lead_data, self.sampler.sampling_rate, self)
            self.detail_view.show()
            
    # Add other helper methods like create_metrics_frame, show_ports_dialog, go_back, etc.
    # from your original script. They don't need to be changed.
    LEAD_COLORS = { "I": "#00ff99", "II": "#ff0055", "III": "#0099ff", "aVR": "#ff9900", "aVL": "#cc00ff", "aVF": "#00ccff", "V1": "#ffcc00", "V2": "#00ffcc", "V3": "#ff6600", "V4": "#6600ff", "V5": "#00b894", "V6": "#ff0066" }
    
    def create_metrics_frame(self):
        metrics_frame = QFrame()
        metrics_frame.setObjectName("metrics_frame")
        metrics_frame.setStyleSheet("QFrame#metrics_frame { background: #000000; border: 2px solid #333333; border-radius: 6px; padding: 4px; }")
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setSpacing(10)
        self.metric_labels = {}
        
        metric_info = [
            ("Heart Rate", "00", "heart_rate", "#ff0000"),
            ("PR (ms)", "--", "pr_interval", "#ff0000"),
            ("QRS (ms)", "--", "qrs_duration", "#ffff00"),
            ("SR (Hz)", "--", "sampling_rate", "#ffffff")
        ]
        
        for title, value, key, color in metric_info:
            box = QVBoxLayout()
            box.setSpacing(2)
            lbl = QLabel(title)
            lbl.setFont(QFont("Arial", 10, QFont.Bold))
            lbl.setStyleSheet("color: #00ff00;")
            lbl.setAlignment(Qt.AlignCenter)
            val = QLabel(value)
            val.setFont(QFont("Arial", 14, QFont.Bold))
            val.setStyleSheet(f"color: {color};")
            val.setAlignment(Qt.AlignCenter)
            box.addWidget(lbl)
            box.addWidget(val)
            metrics_layout.addLayout(box)
            self.metric_labels[key] = val
            metrics_layout.addStretch()
        return metrics_frame

    def show_ports_dialog(self):
        """Show port selection dialog"""
        dialog = PortSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            port_name, baud_rate = dialog.get_selection()
            if port_name and baud_rate:
                # Save settings
                self.settings_manager.set_serial_port(port_name)
                self.settings_manager.set_baud_rate(baud_rate)
                
                QMessageBox.information(self, "Port Configuration", 
                                      f"Port configured successfully!\nPort: {port_name}\nBaud Rate: {baud_rate}")
                
                # Update the ports button text to show selected port
                self.ports_btn.setText(f"Port: {port_name}")

    def go_back(self):
        """Go back to the dashboard"""
        self.stacked_widget.setCurrentIndex(0)


class PortSelectionDialog(QDialog):
    """Custom dialog for port and baud rate selection"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Port Configuration")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select COM Port and Baud Rate")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # COM Port selection
        self.port_combo = QComboBox()
        ports = serial.tools.list_ports.comports()
        self.port_combo.addItem("Select Port")
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
        form_layout.addRow("COM Port:", self.port_combo)
        
        # Baud Rate selection
        self.baud_combo = QComboBox()
        baud_rates = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]
        self.baud_combo.addItems(baud_rates)
        self.baud_combo.setCurrentText("115200")  # Default baud rate
        form_layout.addRow("Baud Rate:", self.baud_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Set default button
        self.ok_btn.setDefault(True)
    
    def get_selection(self):
        """Get the selected port and baud rate"""
        selected_port = self.port_combo.currentText()
        selected_baud = self.baud_combo.currentText()
        
        if selected_port != "Select Port":
            # Extract just the port name (e.g., "COM3" from "COM3 - USB Serial Port")
            port_name = selected_port.split(" - ")[0]
            return port_name, selected_baud
        return None, None

