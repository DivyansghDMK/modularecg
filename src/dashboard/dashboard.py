from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout, QCalendarWidget, QTextEdit,
    QDialog, QLineEdit, QComboBox, QFormLayout, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QMovie
from PyQt5.QtCore import Qt, QTimer
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import math
from ecg.twelve_lead_test import TwelveLeadTest
import os
import json

class MplCanvas(FigureCanvas):
    def __init__(self, width=4, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class SignInDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign In")
        self.setFixedSize(340, 240)
        self.setStyleSheet("""
            QDialog { background: #fff; border-radius: 18px; }
            QLabel { font-size: 15px; color: #222; }
            QLineEdit, QComboBox { border: 2px solid #ff6600; border-radius: 8px; padding: 6px 10px; font-size: 15px; background: #f7f7f7; }
            QPushButton { background: #ff6600; color: white; border-radius: 10px; padding: 8px 0; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background: #ff8800; }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 24, 28, 24)
        title = QLabel("Sign In to PulseMonitor")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Doctor", "Patient"])
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter your name")
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Password")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Role:", self.role_combo)
        form.addRow("Name:", self.name_edit)
        form.addRow("Password:", self.pass_edit)
        layout.addLayout(form)
        self.signin_btn = QPushButton("Sign In")
        self.signin_btn.clicked.connect(self.accept)
        layout.addWidget(self.signin_btn)
    def get_user_info(self):
        return self.role_combo.currentText(), self.name_edit.text()

class Dashboard(QWidget):
    def __init__(self, username=None, role=None):
        super().__init__()
        self.username = username
        self.role = role
        self.medical_mode = False
        self.setWindowTitle("ECG Monitor Dashboard")
        self.setGeometry(100, 100, 1300, 900)
        # --- Plasma GIF background ---
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 1300, 900)
        self.bg_label.lower()
        movie = QMovie("plasma.gif")
        self.bg_label.setMovie(movie)
        movie.start()
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        # --- Header ---
        header = QHBoxLayout()
        logo = QLabel("ECG Monitor")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        logo.setStyleSheet("color: #ff6600;")
        header.addWidget(logo)
        # --- Internet Status Dot ---
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(18, 18)
        self.status_dot.setStyleSheet("border-radius: 9px; background: gray; border: 2px solid #fff;")
        header.addWidget(self.status_dot)
        self.update_internet_status()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_internet_status)
        self.status_timer.start(3000)  # check every 3 seconds
        # --- Medical Mode Toggle ---
        self.medical_btn = QPushButton("Medical Mode")
        self.medical_btn.setCheckable(True)
        self.medical_btn.setStyleSheet("background: #00b894; color: white; border-radius: 10px; padding: 4px 18px;")
        self.medical_btn.clicked.connect(self.toggle_medical_mode)
        header.addWidget(self.medical_btn)
        header.addStretch()
        self.user_label = QLabel(f"{self.username or 'User'}\n{self.role or ''}")
        self.user_label.setFont(QFont("Arial", 10))
        self.user_label.setAlignment(Qt.AlignRight)
        header.addWidget(self.user_label)
        self.sign_btn = QPushButton("Sign Out")
        self.sign_btn.setStyleSheet("background: #e74c3c; color: white; border-radius: 10px; padding: 4px 18px;")
        self.sign_btn.clicked.connect(self.handle_sign_out)
        header.addWidget(self.sign_btn)
        main_layout.addLayout(header)
        # --- Greeting and Date Row ---
        greet_row = QHBoxLayout()
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        greet = QLabel(f"<span style='font-size:18pt;font-weight:bold;'>{greeting}, {self.username or 'User'}</span><br><span style='color:#888;'>Welcome to your ECG dashboard</span>")
        greet.setFont(QFont("Arial", 14))
        greet_row.addWidget(greet)
        greet_row.addStretch()
        date_btn = QPushButton("ECG Lead Test 12")
        date_btn.setStyleSheet("background: #ff6600; color: white; border-radius: 16px; padding: 8px 24px;")
        date_btn.clicked.connect(self.go_to_lead_test)
        greet_row.addWidget(date_btn)
        main_layout.addLayout(greet_row)
        # --- Main Grid ---
        grid = QGridLayout()
        grid.setSpacing(20)
        # --- Heart Rate Card ---
        heart_card = QFrame()
        heart_card.setStyleSheet("background: white; border-radius: 16px;")
        heart_layout = QVBoxLayout(heart_card)
        heart_label = QLabel("Live Heart Rate Overview")
        heart_label.setFont(QFont("Arial", 14, QFont.Bold))
        heart_img = QLabel()
        self.heart_pixmap = QPixmap(r"C:/Users/DELL/Desktop/EcgFR/assets/her.png")
        self.heart_base_size = 220
        heart_img.setFixedSize(self.heart_base_size + 20, self.heart_base_size + 20)
        heart_img.setAlignment(Qt.AlignCenter)
        heart_img.setPixmap(self.heart_pixmap.scaled(self.heart_base_size, self.heart_base_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        heart_layout.addWidget(heart_label)
        heart_layout.addWidget(heart_img)
        heart_layout.addWidget(QLabel("Stress Level: Low"))
        heart_layout.addWidget(QLabel("Average Variability: 90ms"))
        grid.addWidget(heart_card, 0, 0, 2, 1)
        # --- Heartbeat Animation ---
        self.heart_img = heart_img
        self.heartbeat_phase = 0
        self.heartbeat_timer = QTimer(self)
        self.heartbeat_timer.timeout.connect(self.animate_heartbeat)
        self.heartbeat_timer.start(30)  # ~33 FPS
        # --- Patient Body Analysis Cards ---
        analysis_card = QFrame()
        analysis_card.setStyleSheet("background: white; border-radius: 16px;")
        analysis_layout = QHBoxLayout(analysis_card)
        for title, value, unit in [
            ("Glucose Level", "127", "mg/dl"),
            ("Cholesterol Level", "164", "mg"),
            ("Paracetamol", "35", "%")
        ]:
            box = QVBoxLayout()
            lbl = QLabel(title)
            lbl.setFont(QFont("Arial", 10, QFont.Bold))
            val = QLabel(f"{value} {unit}")
            val.setFont(QFont("Arial", 16, QFont.Bold))
            box.addWidget(lbl)
            box.addWidget(val)
            analysis_layout.addLayout(box)
        grid.addWidget(analysis_card, 0, 1, 1, 2)
        # --- ECG Recording (Animated Chart) ---
        ecg_card = QFrame()
        ecg_card.setStyleSheet("background: white; border-radius: 16px;")
        ecg_layout = QVBoxLayout(ecg_card)
        ecg_label = QLabel("ECG Recording")
        ecg_label.setFont(QFont("Arial", 12, QFont.Bold))
        ecg_layout.addWidget(ecg_label)
        self.ecg_canvas = MplCanvas(width=4, height=2)
        self.ecg_canvas.axes.set_facecolor("#eee")
        self.ecg_canvas.axes.set_xticks([])
        self.ecg_canvas.axes.set_yticks([])
        self.ecg_canvas.axes.set_title("Lead II", fontsize=10)
        ecg_layout.addWidget(self.ecg_canvas)
        grid.addWidget(ecg_card, 1, 1)
        # --- Total Visitors (Pie Chart) ---
        visitors_card = QFrame()
        visitors_card.setStyleSheet("background: white; border-radius: 16px;")
        visitors_layout = QVBoxLayout(visitors_card)
        visitors_label = QLabel("Total Visitors")
        visitors_label.setFont(QFont("Arial", 12, QFont.Bold))
        visitors_layout.addWidget(visitors_label)
        pie_canvas = MplCanvas(width=2.5, height=2.5)
        pie_data = [30, 25, 30, 15]
        pie_labels = ["December", "November", "October", "September"]
        pie_colors = ["#ff6600", "#00b894", "#636e72", "#fdcb6e"]
        wedges, texts, autotexts = pie_canvas.axes.pie(
            pie_data, labels=pie_labels, autopct='%1.0f%%', colors=pie_colors, startangle=90
        )
        pie_canvas.axes.set_aspect('equal')
        visitors_layout.addWidget(pie_canvas)
        grid.addWidget(visitors_card, 1, 2)
        # --- Schedule Card ---
        schedule_card = QFrame()
        schedule_card.setStyleSheet("background: white; border-radius: 16px;")
        schedule_layout = QVBoxLayout(schedule_card)
        schedule_label = QLabel("Schedule")
        schedule_label.setFont(QFont("Arial", 12, QFont.Bold))
        schedule_layout.addWidget(schedule_label)
        cal = QCalendarWidget()
        cal.setFixedHeight(120)
        # Highlight last ECG usage date in red
        from PyQt5.QtGui import QTextCharFormat, QColor
        last_ecg_file = 'last_ecg_date.json'
        import datetime
        today = datetime.date.today()
        # Try to load last ECG date from file
        last_ecg_date = None
        if os.path.exists(last_ecg_file):
            with open(last_ecg_file, 'r') as f:
                try:
                    data = json.load(f)
                    last_ecg_date = data.get('last_ecg_date')
                except Exception:
                    last_ecg_date = None
        if last_ecg_date:
            try:
                y, m, d = map(int, last_ecg_date.split('-'))
                last_date = Qt.QDate(y, m, d)
                fmt = QTextCharFormat()
                fmt.setBackground(QColor('red'))
                fmt.setForeground(QColor('white'))
                cal.setDateTextFormat(last_date, fmt)
            except Exception:
                pass
        schedule_layout.addWidget(cal)
        grid.addWidget(schedule_card, 2, 0)
        # --- Issue Found Card ---
        issue_card = QFrame()
        issue_card.setStyleSheet("background: white; border-radius: 16px;")
        issue_layout = QVBoxLayout(issue_card)
        issue_label = QLabel("Issue Found")
        issue_label.setFont(QFont("Arial", 12, QFont.Bold))
        issue_layout.addWidget(issue_label)
        issues_text = (
            "1. Heart Rate\n"
            "   • Tachycardia: Abnormally fast heart rate.\n"
            "   • Bradycardia: Abnormally slow heart rate.\n\n"
            "2. Heart Rhythm\n"
            "   • Normal Sinus Rhythm: Regular rhythm from the sinoatrial node.\n"
            "   • Arrhythmias: Irregular rhythms (e.g., atrial fibrillation, ventricular tachycardia, heart block).\n\n"
            "3. Electrical Conduction\n"
            "   • Heart block (1st, 2nd, 3rd degree), bundle branch blocks (right/left).\n\n"
            "4. Cardiac Size and Hypertrophy\n"
            "   • Enlarged chambers or hypertrophy (e.g., left ventricular hypertrophy).\n\n"
            "5. Ischemia and Infarction\n"
            "   • Ischemia: ST depression.\n"
            "   • Infarction: ST elevation, pathological Q waves.\n\n"
            "6. Electrolyte Abnormalities\n"
            "   • Hyperkalemia: Peaked T waves.\n"
            "   • Hypokalemia: Flattened/inverted T waves, U waves.\n"
            "   • Calcium: QT interval changes.\n\n"
            "7. Pericardial Disease\n"
            "   • Pericarditis: Diffuse ST elevation, PR depression.\n\n"
            "8. Pacemaker Activity\n"
            "   • Pacemaker function and capture.\n\n"
            "9. Drug Effects\n"
            "   • Digitalis, antiarrhythmics: Characteristic ECG changes.\n\n"
            "10. Cardiac Arrest Patterns\n"
            "   • Asystole, ventricular fibrillation, PEA."
        )
        issues_box = QTextEdit()
        issues_box.setReadOnly(True)
        issues_box.setText(issues_text)
        issues_box.setStyleSheet("background: #f7f7f7; border: none; font-size: 12px;")
        issues_box.setMinimumHeight(180)
        issue_layout.addWidget(issues_box)
        grid.addWidget(issue_card, 2, 1, 1, 2)
        # --- ECG Monitor Metrics Cards ---
        metrics_card = QFrame()
        metrics_card.setStyleSheet("background: white; border-radius: 16px;")
        metrics_layout = QHBoxLayout(metrics_card)
        for title, value, unit in [
            ("Heart Rate", "76", "bpm"),
            ("PR Interval", "160", "ms"),
            ("QRS Duration", "90", "ms"),
            ("QTc Interval", "410", "ms"),
            ("QRS Axis", "+60", "°"),
            ("ST Segment", "Normal", ""),
        ]:
            box = QVBoxLayout()
            lbl = QLabel(title)
            lbl.setFont(QFont("Arial", 10, QFont.Bold))
            val = QLabel(f"{value} {unit}")
            val.setFont(QFont("Arial", 16, QFont.Bold))
            box.addWidget(lbl)
            box.addWidget(val)
            metrics_layout.addLayout(box)
        grid.addWidget(metrics_card, 0, 1, 1, 2)
        main_layout.addLayout(grid)
        # --- ECG Animation Setup ---
        self.ecg_x = np.linspace(0, 2, 500)
        self.ecg_y = 1000 + 200 * np.sin(2 * np.pi * 2 * self.ecg_x) + 50 * np.random.randn(500)
        self.ecg_line, = self.ecg_canvas.axes.plot(self.ecg_x, self.ecg_y, color="#ff6600")
        self.anim = FuncAnimation(self.ecg_canvas.figure, self.update_ecg, interval=50, blit=True)
    def update_ecg(self, frame):
        self.ecg_y = np.roll(self.ecg_y, -1)
        self.ecg_y[-1] = 1000 + 200 * np.sin(2 * np.pi * 2 * self.ecg_x[-1] + frame/10) + 50 * np.random.randn()
        self.ecg_line.set_ydata(self.ecg_y)
        return [self.ecg_line]
    def animate_heartbeat(self):
        # Heartbeat effect: scale up and down in a sine wave pattern
        beat = 1 + 0.13 * math.sin(self.heartbeat_phase) + 0.07 * math.sin(2 * self.heartbeat_phase)
        size = int(self.heart_base_size * beat)
        self.heart_img.setPixmap(self.heart_pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.heartbeat_phase += 0.18  # Controls speed of beat
        if self.heartbeat_phase > 2 * math.pi:
            self.heartbeat_phase -= 2 * math.pi
    def handle_sign(self):
        if self.sign_btn.text() == "Sign In":
            dialog = SignInDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                role, name = dialog.get_user_info()
                if not name.strip():
                    QMessageBox.warning(self, "Input Error", "Please enter your name.")
                    return
                self.user_label.setText(f"{name}\n{role}")
                self.sign_btn.setText("Sign Out")
        else:
            self.user_label.setText("Not signed in")
            self.sign_btn.setText("Sign In")
    def handle_sign_out(self):
        self.user_label.setText("Not signed in")
        self.sign_btn.setText("Sign In")
    def go_to_lead_test(self):
        # Simulate redirect to ECG 12-lead test page
        QMessageBox.information(self, "ECG Lead Test 12", "Redirected to ECG Lead Test 12 page! (Demo)")
    def update_internet_status(self):
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self.status_dot.setStyleSheet("border-radius: 9px; background: #00e676; border: 2px solid #fff;")
            self.status_dot.setToolTip("Connected to Internet")
        except Exception:
            self.status_dot.setStyleSheet("border-radius: 9px; background: #e74c3c; border: 2px solid #fff;")
            self.status_dot.setToolTip("No Internet Connection")
    def toggle_medical_mode(self):
        self.medical_mode = not self.medical_mode
        if self.medical_mode:
            # Medical color coding: blue/green/white
            self.setStyleSheet("QWidget { background: #e3f6fd; } QFrame { background: #f8fdff; border-radius: 16px; } QLabel { color: #006266; }")
            self.medical_btn.setText("Normal Mode")
            self.medical_btn.setStyleSheet("background: #0984e3; color: white; border-radius: 10px; padding: 4px 18px;")
        else:
            self.setStyleSheet("")
            self.medical_btn.setText("Medical Mode")
            self.medical_btn.setStyleSheet("background: #00b894; color: white; border-radius: 10px; padding: 4px 18px;")