import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QStackedWidget, QFrame, QCheckBox,
    QLineEdit, QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize

# --- Constants ---
USER_PROFILES_DIR = "user_profiles"
PRIMARY_COLOR = "#FFA726"  # A calm, friendly orange
ACCENT_COLOR = "#FB8C00"
TEXT_COLOR = "#424242"
EMERGENCY_COLOR = "#D32F2F" # A strong but not overly aggressive red
BACKGROUND_COLOR = "#FFF3E0"
ERROR_COLOR = "#D32F2F"

class HushApp(QMainWindow):
    """
    The main window for the HUSH application. It manages the different screens
    using a QStackedWidget.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HUSH")
        self.setGeometry(100, 100, 800, 750)
        self.setWindowIcon(QIcon()) # You can add an icon file here later
        self.current_user = None

        # Create user profiles directory if it doesn't exist
        if not os.path.exists(USER_PROFILES_DIR):
            os.makedirs(USER_PROFILES_DIR)

        # Main widget to hold everything
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Use a QStackedWidget to manage screens
        self.stacked_widget = QStackedWidget()

        # Create the screens
        self.login_screen = LoginScreen(self)
        self.home_screen = HomeScreen(self)
        self.check_in_screen = CheckInScreen(self)

        # Add screens to the stack
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.check_in_screen)

        # Set the main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)

        # Apply the application-wide styles
        self.apply_stylesheet()
        
        # Start on the login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def apply_stylesheet(self):
        """Applies a CSS stylesheet to the entire application for a consistent look."""
        style = f"""
            QWidget {{
                background-color: {BACKGROUND_COLOR};
                font-family: Arial, sans-serif;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 16px;
            }}
            QLabel#Title {{
                font-size: 48px;
                font-weight: bold;
                color: {PRIMARY_COLOR};
                padding-bottom: 10px;
            }}
            QLabel#HushAcronym {{
                font-size: 20px;
                font-weight: bold;
                color: {ACCENT_COLOR};
            }}
            QLabel#InfoText {{
                font-size: 14px;
                line-height: 1.5;
                word-wrap: break-word;
            }}
            QLabel#ErrorLabel {{
                color: {ERROR_COLOR};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 18px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
            #EmergencyButton {{
                background-color: {EMERGENCY_COLOR};
                font-size: 24px;
                padding: 25px;
            }}
            #EmergencyButton:hover {{
                background-color: #B71C1C;
            }}
            QTextEdit, QLineEdit, QComboBox {{
                background-color: white;
                border: 2px solid {PRIMARY_COLOR};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                color: {TEXT_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
            QCheckBox {{
                font-size: 16px;
            }}
            QFrame#Separator {{
                background-color: {PRIMARY_COLOR};
            }}
            #FaceButton {{
                font-size: 40px;
                padding: 10px;
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 10px;
            }}
            #FaceButton:hover, #FaceButton:checked {{
                border-color: {ACCENT_COLOR};
                background-color: #FFE0B2;
            }}
            QPushButton#LinkButton {{
                background-color: transparent;
                color: {PRIMARY_COLOR};
                font-size: 14px;
                text-decoration: underline;
                padding: 5px;
            }}
        """
        self.setStyleSheet(style)

    def login_successful(self, username):
        """Handles successful login by switching screens and loading data."""
        self.current_user = username
        self.home_screen.welcome_user(username)
        self.check_in_screen.load_data()
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def switch_to_checkin(self):
        """Switches the view to the Check-In Screen."""
        self.stacked_widget.setCurrentWidget(self.check_in_screen)

    def switch_to_home(self):
        """Switches the view to the Home Screen."""
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def logout(self):
        """Logs out the current user and returns to the login screen."""
        self.current_user = None
        self.login_screen.clear_fields()
        self.stacked_widget.setCurrentWidget(self.login_screen)


class LoginScreen(QWidget):
    """A screen for user authentication (login or sign-up)."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(150, 50, 150, 50)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignCenter)

        # --- Title ---
        title = QLabel("HUSH")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        # --- Input Fields ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # --- Sign Up Fields (Initially Hidden) ---
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        
        self.autism_type_combo = QComboBox()
        self.autism_type_combo.addItem("Select Support Needs / Type...")
        self.autism_type_combo.addItems([
            "Level 1: Requiring Support",
            "Level 2: Requiring Substantial Support",
            "Level 3: Requiring Very Substantial Support",
            "Asperger's Syndrome",
            "Pervasive Developmental Disorder (PDD-NOS)",
            "I prefer not to say",
            "Other"
        ])

        # --- Buttons ---
        self.action_button = QPushButton("Login")
        self.action_button.clicked.connect(self.handle_login)
        
        self.switch_button = QPushButton("Don't have an account? Sign Up")
        self.switch_button.setObjectName("LinkButton")
        self.switch_button.clicked.connect(self.switch_to_signup_mode)

        # --- Error Label ---
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        
        # --- Add Widgets to Layout ---
        main_layout.addWidget(title)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.confirm_password_input)
        main_layout.addWidget(self.autism_type_combo)
        main_layout.addWidget(self.action_button)
        main_layout.addWidget(self.switch_button)
        main_layout.addWidget(self.error_label)
        main_layout.addStretch(1)

        # Start in login mode
        self.switch_to_login_mode()

    def switch_to_signup_mode(self):
        self.confirm_password_input.show()
        self.autism_type_combo.show()
        self.action_button.setText("Sign Up")
        self.action_button.clicked.disconnect()
        self.action_button.clicked.connect(self.handle_signup)
        self.switch_button.setText("Already have an account? Login")
        self.switch_button.clicked.disconnect()
        self.switch_button.clicked.connect(self.switch_to_login_mode)
        self.error_label.setText("")

    def switch_to_login_mode(self):
        self.confirm_password_input.hide()
        self.autism_type_combo.hide()
        self.action_button.setText("Login")
        self.action_button.clicked.disconnect()
        self.action_button.clicked.connect(self.handle_login)
        self.switch_button.setText("Don't have an account? Sign Up")
        self.switch_button.clicked.disconnect()
        self.switch_button.clicked.connect(self.switch_to_signup_mode)
        self.error_label.setText("")

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Username and password are required.")
            return

        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)
                if data.get("password") == password:
                    self.parent_window.login_successful(username)
                else:
                    self.error_label.setText("Incorrect password.")
            except (json.JSONDecodeError, IOError):
                self.error_label.setText("Error reading user profile.")
        else:
            self.error_label.setText("User not found.")

    def handle_signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        autism_type = self.autism_type_combo.currentText()
        
        if not username or not password:
            self.error_label.setText("Username and password are required.")
            return
        if password != confirm_password:
            self.error_label.setText("Passwords do not match.")
            return
        if self.autism_type_combo.currentIndex() == 0:
            self.error_label.setText("Please select an option.")
            return

        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}.json")
        if os.path.exists(profile_path):
            self.error_label.setText("Username already exists.")
            return
        
        profile_data = {
            "username": username,
            "password": password,
            "autism_type": autism_type
        }

        try:
            with open(profile_path, "w") as f:
                json.dump(profile_data, f, indent=4)
            # Automatically log in after successful sign up
            self.parent_window.login_successful(username)
        except IOError:
            self.error_label.setText("Could not create user profile.")

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.error_label.setText("")

class CheckInScreen(QWidget):
    """
    A screen for users to input information about how they are feeling.
    This data is saved locally to the user's profile.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        title_label = QLabel("How Are You Feeling?")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # --- Question 1 ---
        q1_label = QLabel("<b>1. What's wrong?</b><br>Can you tell me what you don’t like right now?")
        layout.addWidget(q1_label)
        
        self.feelings_group = QHBoxLayout()
        self.happy_face = self.create_face_button("😊")
        self.sad_face = self.create_face_button("😢")
        self.upset_face = self.create_face_button("😠")
        self.feelings_group.addWidget(self.happy_face)
        self.feelings_group.addWidget(self.sad_face)
        self.feelings_group.addWidget(self.upset_face)
        layout.addLayout(self.feelings_group)
        
        self.what_is_wrong_text = QTextEdit()
        self.what_is_wrong_text.setPlaceholderText("You can write more here...")
        self.what_is_wrong_text.setFixedHeight(60)
        layout.addWidget(self.what_is_wrong_text)


        # --- Other Questions ---
        q2_label = QLabel("<b>2. Where does it hurt or bother you?</b>")
        layout.addWidget(q2_label)
        self.body_parts_group = QHBoxLayout()
        self.head_check = QCheckBox("Head")
        self.tummy_check = QCheckBox("Tummy")
        self.ears_check = QCheckBox("Ears")
        self.body_parts_group.addWidget(self.head_check)
        self.body_parts_group.addWidget(self.tummy_check)
        self.body_parts_group.addWidget(self.ears_check)
        layout.addLayout(self.body_parts_group)

        q3_label = QLabel("<b>3. Is something too loud, bright, or noisy?</b>")
        layout.addWidget(q3_label)
        self.stimuli_group = QHBoxLayout()
        self.loud_check = QCheckBox("Too Loud")
        self.bright_check = QCheckBox("Too Bright")
        self.stimuli_group.addWidget(self.loud_check)
        self.stimuli_group.addWidget(self.bright_check)
        layout.addLayout(self.stimuli_group)

        q4_label = QLabel("<b>4. Did something happen that made you upset?</b>")
        layout.addWidget(q4_label)
        self.upset_reason_text = QTextEdit()
        self.upset_reason_text.setFixedHeight(60)
        layout.addWidget(self.upset_reason_text)
        
        # --- Guiding Questions ---
        q6_label = QLabel("<b>5. Do you want to take a break or go to a quiet place?</b>")
        layout.addWidget(q6_label)
        self.break_group = QHBoxLayout()
        self.break_yes = QCheckBox("Yes, please")
        self.break_no = QCheckBox("No, thank you")
        self.break_group.addWidget(self.break_yes)
        self.break_group.addWidget(self.break_no)
        layout.addLayout(self.break_group)

        q7_label = QLabel("<b>6. How can I help?</b>")
        layout.addWidget(q7_label)
        self.help_group = QHBoxLayout()
        self.hug_check = QCheckBox("A Hug")
        self.water_check = QCheckBox("Some Water")
        self.sit_down_check = QCheckBox("To Sit Down")
        self.call_parents_check = QCheckBox("Call My Parents")
        self.close_app_check = QCheckBox("Close This")
        self.help_group.addWidget(self.hug_check)
        self.help_group.addWidget(self.water_check)
        self.help_group.addWidget(self.sit_down_check)
        self.help_group.addWidget(self.call_parents_check)
        self.help_group.addWidget(self.close_app_check)
        layout.addLayout(self.help_group)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save & Go to Home")
        self.save_button.clicked.connect(self.save_and_switch)
        button_layout.addWidget(self.save_button)
        
        layout.addStretch(1)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_face_button(self, text):
        button = QPushButton(text)
        button.setObjectName("FaceButton")
        button.setCheckable(True)
        button.setFixedSize(QSize(80, 80))
        return button

    def save_and_switch(self):
        self.save_data()
        # In a real app, you might want to handle the "Call" or "Close" actions here
        if self.close_app_check.isChecked():
            self.parent_window.close()
        elif self.call_parents_check.isChecked():
            # This is a placeholder for a real call function
            QMessageBox.information(self, "Action", "Calling parents... (placeholder)")
            self.parent_window.switch_to_home()
        else:
            self.parent_window.switch_to_home()


    def get_checkin_data_path(self):
        if self.parent_window.current_user:
            return os.path.join(USER_PROFILES_DIR, f"{self.parent_window.current_user}_checkin.json")
        return None

    def save_data(self):
        path = self.get_checkin_data_path()
        if not path: return
        
        selected_feeling = ""
        if self.happy_face.isChecked(): selected_feeling = "happy"
        elif self.sad_face.isChecked(): selected_feeling = "sad"
        elif self.upset_face.isChecked(): selected_feeling = "upset"

        data = {
            "feeling": selected_feeling,
            "what_is_wrong_text": self.what_is_wrong_text.toPlainText(),
            "hurt_head": self.head_check.isChecked(),
            "hurt_tummy": self.tummy_check.isChecked(),
            "hurt_ears": self.ears_check.isChecked(),
            "is_loud": self.loud_check.isChecked(),
            "is_bright": self.bright_check.isChecked(),
            "upset_reason": self.upset_reason_text.toPlainText(),
            "wants_break": self.break_yes.isChecked(),
            "wants_hug": self.hug_check.isChecked(),
            "wants_water": self.water_check.isChecked(),
            "wants_sit": self.sit_down_check.isChecked(),
            "wants_call_parents": self.call_parents_check.isChecked(),
            "wants_close_app": self.close_app_check.isChecked()
        }
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving check-in data: {e}")
            
    def load_data(self):
        path = self.get_checkin_data_path()
        if not path or not os.path.exists(path):
            self.clear_fields()
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)
                
            if data.get("feeling") == "happy": self.happy_face.setChecked(True)
            elif data.get("feeling") == "sad": self.sad_face.setChecked(True)
            elif data.get("feeling") == "upset": self.upset_face.setChecked(True)
            
            self.what_is_wrong_text.setPlainText(data.get("what_is_wrong_text", ""))
            self.head_check.setChecked(data.get("hurt_head", False))
            self.tummy_check.setChecked(data.get("hurt_tummy", False))
            self.ears_check.setChecked(data.get("hurt_ears", False))
            self.loud_check.setChecked(data.get("is_loud", False))
            self.bright_check.setChecked(data.get("is_bright", False))
            self.break_yes.setChecked(data.get("wants_break", False))
            self.hug_check.setChecked(data.get("wants_hug", False))
            self.water_check.setChecked(data.get("wants_water", False))
            self.sit_down_check.setChecked(data.get("wants_sit", False))
            self.call_parents_check.setChecked(data.get("wants_call_parents", False))
            self.close_app_check.setChecked(data.get("wants_close_app", False))
            
            self.upset_reason_text.setPlainText(data.get("upset_reason", ""))
        except (IOError, json.JSONDecodeError):
            self.clear_fields()
    
    def clear_fields(self):
        """Resets all fields on the check-in screen to their default state."""
        self.happy_face.setChecked(False)
        self.sad_face.setChecked(False)
        self.upset_face.setChecked(False)
        self.what_is_wrong_text.clear()
        self.head_check.setChecked(False)
        self.tummy_check.setChecked(False)
        self.ears_check.setChecked(False)
        self.loud_check.setChecked(False)
        self.bright_check.setChecked(False)
        self.break_yes.setChecked(False)
        self.break_no.setChecked(False)
        self.hug_check.setChecked(False)
        self.water_check.setChecked(False)
        self.sit_down_check.setChecked(False)
        self.call_parents_check.setChecked(False)
        self.close_app_check.setChecked(False)
        self.upset_reason_text.clear()


class HomeScreen(QWidget):
    """
    The main landing screen of the app. Displays the HUSH acronym, app info,
    and the emergency button.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        top_bar_layout = QHBoxLayout()
        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignLeft)

        logout_button = QPushButton("Logout")
        logout_button.setFixedWidth(120)
        logout_button.clicked.connect(self.parent_window.logout)
        
        top_bar_layout.addWidget(self.welcome_label)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(logout_button)
        layout.addLayout(top_bar_layout)

        emergency_button = QPushButton("I NEED HELP")
        emergency_button.setObjectName("EmergencyButton")
        emergency_button.setMinimumHeight(100)
        emergency_button.clicked.connect(self.parent_window.switch_to_checkin)
        layout.addWidget(emergency_button)
        
        hush_title = QLabel("HUSH")
        hush_title.setObjectName("HushAcronym")
        hush_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(hush_title)
        
        hush_text = QLabel(
            "<b>Hear</b> – Actively listen to needs or behavior cues<br>"
            "<b>Understand</b> – Recognize what might be causing distress<br>"
            "<b>Soothe</b> – Use sensory or emotional strategies to calm<br>"
            "<b>Help</b> – Offer the next steps or coping techniques"
        )
        hush_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(hush_text)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("Separator")
        separator.setFixedHeight(2)
        layout.addWidget(separator)

        info_text_content = """
        <b>Our Goal:</b> To develop an AI-powered app designed to support children with autism during moments of stress or panic. Each child’s profile—including known stress triggers, preferences, and calming methods—can be set up by a caregiver, providing a personalized foundation for the app’s responses.
        """
        info_label = QLabel(info_text_content)
        info_label.setObjectName("InfoText")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignJustify)
        layout.addWidget(info_label)

        layout.addStretch(1)

        update_info_button = QPushButton("Update Check-In Answers")
        update_info_button.clicked.connect(self.parent_window.switch_to_checkin)
        layout.addWidget(update_info_button)
        self.setLayout(layout)

    def welcome_user(self, username):
        self.welcome_label.setText(f"<b>Welcome, {username}!</b>")

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = HushApp()
        window.show()
        sys.exit(app.exec_())    
#this is a comment
#test