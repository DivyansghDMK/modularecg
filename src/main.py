import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget, QWidget, QInputDialog, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from auth.sign_in import SignIn
from auth.sign_out import SignOut
from dashboard.dashboard import Dashboard
from splash_screen import SplashScreen


USER_DATA_FILE = "users.json"


def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)


# Login/Register Dialog
class LoginRegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Monitor - Sign In / Sign Up")
        self.setMinimumSize(800, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setStyleSheet("""
            QDialog { background: #fafbfc; border-radius: 18px; }
            QLabel#AppTitle { color: #2453ff; font-size: 26px; font-weight: bold; }
            QLabel#Headline { color: #2453ff; font-size: 22px; font-weight: bold; }
            QLabel#Welcome { color: #222; font-size: 13px; }
            QLineEdit { border: 1.5px solid #2453ff; border-radius: 4px; padding: 8px 12px; font-size: 15px; background: #fff; }
            QPushButton#LoginBtn { background: #2453ff; color: white; border-radius: 4px; padding: 8px 0; font-size: 16px; font-weight: bold; }
            QPushButton#LoginBtn:hover { background: #1a3bb3; }
            QPushButton#SignUpBtn { background: #fff; color: #2453ff; border: 1.5px solid #2453ff; border-radius: 4px; padding: 8px 0; font-size: 16px; font-weight: bold; }
            QPushButton#SignUpBtn:hover { background: #eaf0ff; }
            QCheckBox { font-size: 13px; }
            QLabel#Social { color: #2453ff; font-size: 13px; font-weight: bold; }
            QPushButton#SocialBtn { background: none; color: #2453ff; border: none; font-size: 13px; text-decoration: underline; }
            QPushButton#SocialBtn:hover { color: #1a3bb3; }
        """)
        from auth.sign_in import SignIn
        self.sign_in_logic = SignIn()
        self.init_ui()
        self.result = False
        self.username = None
        self.user_details = {}
        self.center_on_screen()

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        # Set up GIF background
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()
        gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/v.gif'))
        if os.path.exists(gif_path):
            from PyQt5.QtGui import QMovie
            movie = QMovie(gif_path)
            self.bg_label.setMovie(movie)
            movie.start()
        self.bg_label.setScaledContents(True)
        # Glass effect container in center
        glass = QWidget(self)
        glass.setObjectName("Glass")
        glass.setStyleSheet("""
            QWidget#Glass {
                background: rgba(255,255,255,0.18);
                border-radius: 24px;
                border: 2px solid rgba(255,255,255,0.35);
            }
        """)
        glass.setMinimumSize(520, 480)
        # Create stacked widget and login/register widgets BEFORE using stacked_col
        self.stacked = QStackedWidget(glass)
        self.login_widget = self.create_login_widget()
        self.register_widget = self.create_register_widget()
        self.stacked.addWidget(self.login_widget)
        self.stacked.addWidget(self.register_widget)
        # Now build glass layout
        glass_layout = QHBoxLayout(glass)
        glass_layout.setContentsMargins(32, 32, 32, 32)
        # ECG image inside glass, left side
        ecg_img = QLabel()
        from PyQt5.QtGui import QPixmap
        ecg_pix = QPixmap(os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/v1.png')))
        if not ecg_pix.isNull():
            ecg_img.setPixmap(ecg_pix.scaled(320, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            ecg_img.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
            ecg_img.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            ecg_img.setStyleSheet("margin-right: 32px; margin-left: 0px; border-radius: 24px; box-shadow: 0 0 32px #ff6600; background: transparent;")
        glass_layout.addWidget(ecg_img, 2)
        # Login/Register stacked widget (vertical)
        stacked_col = QVBoxLayout()
        # Instagram-style title
        title = QLabel("Pulse Monitor")
        title.setFont(QFont("Pacifico, Segoe Script, cursive", 34, QFont.Bold))
        title.setStyleSheet("color: #ff6600; letter-spacing: 1px; margin-bottom: 12px; padding-top: 8px; padding-bottom: 8px;")
        title.setAlignment(Qt.AlignHCenter)
        stacked_col.addWidget(title)
        stacked_col.addSpacing(8)
        stacked_col.addWidget(self.stacked, 2)
        # Add sign up prompt below
        signup_row = QHBoxLayout()
        signup_row.addStretch(1)
        signup_lbl = QLabel("Don't have an account?")
        signup_lbl.setStyleSheet("color: #fff; font-size: 15px;")
        signup_btn = QPushButton("Sign up")
        signup_btn.setStyleSheet("color: #ff6600; background: transparent; border: none; font-size: 15px; font-weight: bold; text-decoration: underline;")
        signup_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        signup_row.addWidget(signup_lbl)
        signup_row.addWidget(signup_btn)
        signup_row.addStretch(1)
        stacked_col.addSpacing(10)
        stacked_col.addLayout(signup_row)
        stacked_col.addStretch(1)
        glass_layout.addLayout(stacked_col, 3)
        glass_layout.setSpacing(0)
        # Center glass in dialog
        main_layout = QVBoxLayout(self)
        main_layout.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(glass, 1)
        row.addStretch(1)
        main_layout.addLayout(row)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        # Make glass and all widgets expand responsively
        glass.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Resize background with window
        self.resizeEvent = self._resize_bg

    def _resize_bg(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        event.accept()

    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email Address")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        login_btn = QPushButton("Login")
        login_btn.setObjectName("LoginBtn")
        login_btn.setStyleSheet("background: #ff6600; color: white; border-radius: 10px; padding: 8px 0; font-size: 16px; font-weight: bold;")
        login_btn.clicked.connect(self.handle_login)
        phone_btn = QPushButton("Login with Phone Number")
        phone_btn.setObjectName("SignUpBtn")
        phone_btn.setStyleSheet("background: #ff6600; color: white; border-radius: 10px; padding: 8px 0; font-size: 16px; font-weight: bold;")
        phone_btn.clicked.connect(self.handle_phone_login)
        for w in [self.login_email, self.login_password, login_btn, phone_btn]:
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_email.setStyleSheet("border: 2px solid #ff6600; border-radius: 8px; padding: 6px 10px; font-size: 15px; background: #f7f7f7; color: #222;")
        self.login_password.setStyleSheet("border: 2px solid #ff6600; border-radius: 8px; padding: 6px 10px; font-size: 15px; background: #f7f7f7; color: #222;")
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addWidget(login_btn)
        layout.addWidget(phone_btn)
        # Add nav links under phone_btn
        nav_row = QHBoxLayout()
        from nav_home import NavHome
        from nav_about import NavAbout
        from nav_blog import NavBlog
        from nav_pricing import NavPricing
        nav_links = [
            ("Home", NavHome),
            ("About us", NavAbout),
            ("Blog", NavBlog),
            ("Pricing", NavPricing)
        ]
        self.nav_stack = QStackedWidget()
        self.nav_pages = {}
        def show_nav_page(page_name):
            self.nav_stack.setCurrentWidget(self.nav_pages[page_name])
            self.nav_stack.setVisible(True)
        for text, NavClass in nav_links:
            nav_btn = QPushButton(text)
            nav_btn.setStyleSheet("color: #ff6600; background: transparent; border: none; font-size: 15px; font-weight: bold; text-decoration: underline;")
            page = NavClass()
            self.nav_stack.addWidget(page)
            self.nav_pages[text] = page
            if text == "Pricing":
                from nav_pricing import show_pricing_dialog
                nav_btn.clicked.connect(lambda checked, p=self: show_pricing_dialog(p))
            else:
                nav_btn.clicked.connect(lambda checked, t=text: show_nav_page(t))
            nav_row.addWidget(nav_btn)
        layout.addLayout(nav_row)
        layout.addWidget(self.nav_stack)
        self.nav_stack.setVisible(False)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def create_register_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Full Name")
        self.reg_age = QLineEdit()
        self.reg_age.setPlaceholderText("Age")
        self.reg_gender = QLineEdit()
        self.reg_gender.setPlaceholderText("Gender")
        self.reg_address = QLineEdit()
        self.reg_address.setPlaceholderText("Address")
        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("Phone Number")
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Confirm Password")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        register_btn = QPushButton("Sign Up")
        register_btn.setObjectName("SignUpBtn")
        register_btn.clicked.connect(self.handle_register)
        for w in [self.reg_name, self.reg_age, self.reg_gender, self.reg_address, self.reg_phone, self.reg_password, self.reg_confirm, register_btn]:
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Apply dashboard color coding
        for w in [self.reg_name, self.reg_age, self.reg_gender, self.reg_address, self.reg_phone, self.reg_password, self.reg_confirm]:
            w.setStyleSheet("border: 2px solid #ff6600; border-radius: 8px; padding: 6px 10px; font-size: 15px; background: #f7f7f7; color: #222;")
        register_btn.setStyleSheet("background: #ff6600; color: white; border-radius: 10px; padding: 8px 0; font-size: 16px; font-weight: bold;")
        register_btn.setMinimumHeight(36)
        layout.addWidget(self.reg_name)
        layout.addWidget(self.reg_age)
        layout.addWidget(self.reg_gender)
        layout.addWidget(self.reg_address)
        layout.addWidget(self.reg_phone)
        layout.addWidget(self.reg_password)
        layout.addWidget(self.reg_confirm)
        layout.addWidget(register_btn)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def handle_login(self):
        email = self.login_email.text()
        password = self.login_password.text()
        if self.sign_in_logic.sign_in_user(email, password):
            self.result = True
            self.username = email
            self.user_details = {}
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password.")

    def handle_phone_login(self):
        phone, ok = QInputDialog.getText(self, "Login with Phone Number", "Enter your phone number:")
        if ok and phone:
            # Here you would implement phone-based authentication logic
            QMessageBox.information(self, "Phone Login", f"Logged in with phone: {phone} (Demo)")
            self.result = True
            self.username = phone
            self.user_details = {'contact': phone}
            self.accept()

    def handle_register(self):
        name = self.reg_name.text()
        age = self.reg_age.text()
        gender = self.reg_gender.text()
        address = self.reg_address.text()
        phone = self.reg_phone.text()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        if not all([name, age, gender, address, phone, password, confirm]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        # Use phone as username for registration
        if not self.sign_in_logic.register_user(phone, password):
            QMessageBox.warning(self, "Error", "Phone number already registered.")
            return
        QMessageBox.information(self, "Success", "Registration successful! You can now sign in.")
        self.stacked.setCurrentIndex(0)

    def _show_nav_window(self, NavClass, text):
        nav_win = NavClass()
        nav_win.setWindowTitle(text)
        nav_win.setMinimumSize(400, 300)
        nav_win.show()
        if not hasattr(self, '_nav_windows'):
            self._nav_windows = []
        self._nav_windows.append(nav_win)


def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    login = LoginRegisterDialog()
    splash.finish(login)
    while True:
        if login.exec_() == QDialog.Accepted and login.result:
            dashboard = Dashboard(username=login.username, role=None)
            dashboard.show()
            app.exec_()
            # After dashboard closes (sign out), show login again (reuse dialog)
            login = LoginRegisterDialog()
        else:
            break


if __name__ == "__main__":
    main()