import sys
import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt, Image

# --- Constants ---
USER_PROFILES_DIR = "user_profiles"
CACHE_FILE = "app_cache.json"
PRIMARY_COLOR = "#0D3B66"      # Deep, confident navy blue
ACCENT_COLOR = "#4D6A92"      # Softer steel-blue for highlights
TEXT_COLOR = "#424242"        # Neutral dark gray—unchanged
EMERGENCY_COLOR = "#D32F2F"    # Strong red—unchanged
BACKGROUND_COLOR = "#B4D6E3"  # Light, airy blue background
ERROR_COLOR = "#D32F2F"        # Same red for errors

# --- Helper Functions --
def load_image(image_path):
    if not os.path.exists(image_path):
        print(f"Warning: Image file not found at '{image_path}'.")
        return QPixmap()
    scaleFactor = 0.5
    img = Image.open(image_path)
    img = img.resize((int(img.width * scaleFactor), int(img.height * scaleFactor)))
    qim = ImageQt(img)
    pix = QPixmap.fromImage(qim)
    return pix

# --- Main Application Window ---
class HushApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HUSH")
        self.setGeometry(100, 100, 800, 750)
        self.setWindowIcon(QIcon())
        self.current_user_data = None

        if not os.path.exists(USER_PROFILES_DIR):
            os.makedirs(USER_PROFILES_DIR)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stacked_widget = QStackedWidget()

        # --- Create all screens ---
        self.login_screen = LoginScreen(self)
        self.signup_screen = SignUpScreen(self)
        self.home_screen = HomeScreen(self)
        self.check_in_screen = CheckInScreen(self)
        self.ai_page = AIPage(self)

        # --- Add screens to the stack ---
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.check_in_screen)
        self.stacked_widget.addWidget(self.ai_page)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)
        self.apply_stylesheet()
        
        # --- Start on the Login Screen ---
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def apply_stylesheet(self):
        style = f"""
            /* Styles remain largely the same, with additions for new widgets */
            QWidget {{
                background-color: {BACKGROUND_COLOR};
                font-family: Arial, sans-serif;
            }}
            QScrollArea {{
                border: none;
            }}
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: {PRIMARY_COLOR};
                border: 2px solid {ACCENT_COLOR};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
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
            QTextEdit, QLineEdit, QComboBox, QDateEdit {{
                background-color: white;
                border: 2px solid {PRIMARY_COLOR};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                color: {TEXT_COLOR};
            }}
            QTextEdit#ChatDisplay {{
                background-color: #FFFFFF;
                border: 2px solid {ACCENT_COLOR};
            }}
            QPushButton#LinkButton {{
                background-color: transparent;
                color: {PRIMARY_COLOR};
                font-size: 14px;
                text-decoration: underline;
                padding: 5px;
                border: none;
                font-weight: normal;
            }}
        """
        self.setStyleSheet(style)

    # --- Navigation Methods ---
    def switch_to_signup(self):
        self.stacked_widget.setCurrentWidget(self.signup_screen)

    def switch_to_login(self):
        self.login_screen.password_input.clear() # Clear password on return
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def login_successful(self, user_data):
        self.current_user_data = user_data
        self.home_screen.load_profile(user_data)
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def switch_to_checkin(self):
        self.stacked_widget.setCurrentWidget(self.check_in_screen)

    def switch_to_home(self):
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def switch_to_ai_page(self, initial_context=None):
        self.ai_page.start_conversation(initial_context)
        self.stacked_widget.setCurrentWidget(self.ai_page)

# --- LOGIN SCREEN ---
class LoginScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.load_cached_username()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(100, 50, 100, 50)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("HUSH Login")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.attempt_login)

        signup_button = QPushButton("Create New Profile")
        signup_button.setObjectName("LinkButton")
        signup_button.clicked.connect(self.parent_window.switch_to_signup)
        
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.error_label)
        layout.addSpacing(20)
        layout.addWidget(login_button)
        layout.addWidget(signup_button, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        
        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}.json")

        if not os.path.exists(profile_path):
            self.error_label.setText("Username not found.")
            return

        try:
            with open(profile_path, 'r') as f:
                user_data = json.load(f)
            
            # NOTE: This is NOT a secure way to handle passwords. For prototyping only.
            if user_data['credentials']['password'] == password:
                self.cache_username(username)
                self.parent_window.login_successful(user_data)
            else:
                self.error_label.setText("Incorrect password.")
        except (json.JSONDecodeError, KeyError):
            self.error_label.setText("Profile file is corrupted.")
    
    def cache_username(self, username):
        with open(CACHE_FILE, 'w') as f:
            json.dump({'last_user': username}, f)

    def load_cached_username(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    self.username_input.setText(cache.get('last_user', ''))
            except (json.JSONDecodeError, KeyError):
                pass

# --- SIGN UP SCREEN (PROFILE SETUP) ---
class SignUpScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        # --- Main Layout with Scroll Area ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Section: Credentials ---
        cred_group = QGroupBox("Account Credentials")
        cred_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        cred_layout.addRow("Username:", self.username_input)
        cred_layout.addRow("Password:", self.password_input)
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # --- Section: General ---
        general_group = QGroupBox("General")
        general_layout = QFormLayout()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Prefer not to say", "Female", "Male", "Non-binary"])
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setCalendarPopup(True)
        general_layout.addRow("First Name:", self.first_name_input)
        general_layout.addRow("Last Name (Optional):", self.last_name_input)
        general_layout.addRow("Gender:", self.gender_input)
        general_layout.addRow("Date of Birth:", self.dob_input)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # --- Section: Diagnosis & Communication ---
        diag_group = QGroupBox("Diagnosis & Communication")
        diag_layout = QVBoxLayout()
        diag_layout.addWidget(QLabel("<b>What type of Autism do you have?</b> (or other diagnosis)"))
        self.autism_type_input = QTextEdit()
        self.autism_type_input.setFixedHeight(80)
        diag_layout.addWidget(self.autism_type_input)
        
        diag_layout.addWidget(QLabel("<b>Communication Style (select all that apply):</b>"))
        self.comm_verbal = QCheckBox("Verbal")
        self.comm_visual = QCheckBox("Visual (Pictures/Symbols)")
        self.comm_sound = QCheckBox("Sound Cues")
        self.comm_sign = QCheckBox("Sign Language")
        diag_layout.addWidget(self.comm_verbal)
        diag_layout.addWidget(self.comm_visual)
        diag_layout.addWidget(self.comm_sound)
        diag_layout.addWidget(self.comm_sign)
        diag_group.setLayout(diag_layout)
        layout.addWidget(diag_group)

        # --- Section: Calming ---
        calming_group = QGroupBox("Calming Preferences")
        calming_layout = QVBoxLayout()
        calming_layout.addWidget(QLabel("<b>Calming Images (Select favorites):</b><br><i>(AI can help suggest themes here)</i>"))
        # Placeholder for AI suggestions
        self.img_nature = QCheckBox("Nature (forests, oceans)")
        self.img_animals = QCheckBox("Animals (cats, dogs)")
        self.img_abstract = QCheckBox("Abstract Shapes & Colors")
        self.img_dark = QCheckBox("Dark, simple images")
        calming_layout.addWidget(self.img_nature)
        calming_layout.addWidget(self.img_animals)
        calming_layout.addWidget(self.img_abstract)
        calming_layout.addWidget(self.img_dark)
        
        calming_layout.addWidget(QLabel("<br><b>Calming Sounds (Select favorites):</b>"))
        # Placeholder for AI suggestions
        self.sound_nature = QCheckBox("Nature sounds (rain, birds)")
        self.sound_music = QCheckBox("Soft Music")
        self.sound_white_noise = QCheckBox("White Noise")
        calming_layout.addWidget(self.sound_nature)
        calming_layout.addWidget(self.sound_music)
        calming_layout.addWidget(self.sound_white_noise)
        
        calming_layout.addWidget(QLabel("<br><b>Known Calming Techniques:</b>"))
        self.calming_tech_input = QTextEdit()
        self.calming_tech_input.setPlaceholderText("e.g., breathing techniques, fidget toys, jokes...")
        self.calming_tech_input.setFixedHeight(80)
        calming_layout.addWidget(self.calming_tech_input)
        calming_group.setLayout(calming_layout)
        layout.addWidget(calming_group)

        # --- Section: Triggers ---
        triggers_group = QGroupBox("Triggers & Sensitivities")
        triggers_layout = QVBoxLayout()
        triggers_layout.addWidget(QLabel("<b>What are some of the main things that cause anxiety?</b><br><i>(AI can present a list of common triggers)</i>"))
        # Placeholder for AI suggestions
        self.trigger_crowds = QCheckBox("Large crowds or loud places")
        self.trigger_changes = QCheckBox("Unexpected changes in routine")
        self.trigger_social = QCheckBox("Social interactions")
        triggers_layout.addWidget(self.trigger_crowds)
        triggers_layout.addWidget(self.trigger_changes)
        triggers_layout.addWidget(self.trigger_social)
        
        triggers_layout.addWidget(QLabel("<br><b>What are some things you are sensitive to?</b>"))
        self.sensitive_input = QTextEdit()
        self.sensitive_input.setPlaceholderText("e.g., bright lights, strong smells, certain textures...")
        self.sensitive_input.setFixedHeight(80)
        triggers_layout.addWidget(self.sensitive_input)
        triggers_group.setLayout(triggers_layout)
        layout.addWidget(triggers_group)

        # --- Section: Emergency ---
        emergency_group = QGroupBox("Emergency Contact")
        emergency_layout = QFormLayout()
        self.e_contact_name = QLineEdit()
        self.e_contact_rel = QLineEdit()
        self.e_contact_phone = QLineEdit()
        self.e_gps_tracking = QComboBox()
        self.e_gps_tracking.addItems(["Only when using the App", "Always", "No"])
        emergency_layout.addRow("Primary Contact Name:", self.e_contact_name)
        emergency_layout.addRow("Relationship to child:", self.e_contact_rel)
        emergency_layout.addRow("Phone Number:", self.e_contact_phone)
        emergency_layout.addRow("Allow GPS Tracking:", self.e_gps_tracking)
        emergency_group.setLayout(emergency_layout)
        layout.addWidget(emergency_group)
        
        # --- Error Label and Buttons ---
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        layout.addWidget(self.error_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        back_button = QPushButton("Back to Login")
        back_button.clicked.connect(self.parent_window.switch_to_login)
        create_button = QPushButton("Create Profile")
        create_button.clicked.connect(self.create_profile)
        button_layout.addWidget(back_button)
        button_layout.addWidget(create_button)
        layout.addLayout(button_layout)
        
        scroll_area.setWidget(main_widget)
        main_v_layout = QVBoxLayout(self)
        main_v_layout.addWidget(scroll_area)
        self.setLayout(main_v_layout)

    def create_profile(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Username and Password cannot be empty.")
            return
        
        profile_path = os.path.join(USER_PROFILES_DIR, f"{username}.json")
        if os.path.exists(profile_path):
            self.error_label.setText("This username is already taken.")
            return

        # --- Gather all data into a dictionary ---
        profile_data = {
            "credentials": {
                "username": username,
                "password": password # INSECURE: FOR PROTOTYPE ONLY
            },
            "general": {
                "first_name": self.first_name_input.text(),
                "last_name": self.last_name_input.text(),
                "gender": self.gender_input.currentText(),
                "dob": self.dob_input.date().toString("yyyy-MM-dd")
            },
            "diagnosis": {
                "autism_type": self.autism_type_input.toPlainText(),
                "communication_styles": [
                    cb.text() for cb in [self.comm_verbal, self.comm_visual, self.comm_sound, self.comm_sign] if cb.isChecked()
                ]
            },
            "calming": {
                "image_themes": [cb.text() for cb in [self.img_nature, self.img_animals, self.img_abstract, self.img_dark] if cb.isChecked()],
                "sound_themes": [cb.text() for cb in [self.sound_nature, self.sound_music, self.sound_white_noise] if cb.isChecked()],
                "techniques": self.calming_tech_input.toPlainText()
            },
            "triggers": {
                "anxieties": [cb.text() for cb in [self.trigger_crowds, self.trigger_changes, self.trigger_social] if cb.isChecked()],
                "sensitivities": self.sensitive_input.toPlainText()
            },
            "emergency": {
                "primary_contact_name": self.e_contact_name.text(),
                "relationship": self.e_contact_rel.text(),
                "phone": self.e_contact_phone.text(),
                "gps": self.e_gps_tracking.currentText()
            }
        }
        
        # --- Save data to file and log in ---
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=4)
            # Automatically log in the user after successful creation
            self.parent_window.login_successful(profile_data)
        except IOError as e:
            self.error_label.setText(f"Error saving profile: {e}")

# --- HOME SCREEN ---
class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.welcome_label)

        hush_title = QLabel()
        hush_title.setPixmap(load_image("logo.png"))
        hush_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(hush_title)

        # --- MODIFIED: Removed Emergency Button ---
        checkin_button = QPushButton("Enter My Safe Place")
        checkin_button.setMinimumHeight(100)
        checkin_button.clicked.connect(self.parent_window.switch_to_checkin)
        layout.addWidget(checkin_button)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_profile(self, user_data):
        first_name = user_data.get("general", {}).get("first_name", "User")
        self.welcome_label.setText(f"<h2>Welcome, {first_name}!</h2>")

# --- CHECK-IN SCREEN ---
class CheckInScreen(QWidget):
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

        # --- MODIFIED: Removed Question 3 ---
        q1_label = QLabel("<b>1. How are you feeling right now?</b>")
        layout.addWidget(q1_label)
        
        self.feelings_group = QHBoxLayout()
        self.happy_face = QCheckBox("😊 Happy")
        self.sad_face = QCheckBox("😢 Sad")
        self.upset_face = QCheckBox("😠 Upset")
        self.feelings_group.addWidget(self.happy_face)
        self.feelings_group.addWidget(self.sad_face)
        self.feelings_group.addWidget(self.upset_face)
        layout.addLayout(self.feelings_group)

    

        self.what_is_wrong_text = QTextEdit()
        self.what_is_wrong_text.setPlaceholderText("You can write more here...")
        self.what_is_wrong_text.setFixedHeight(80)
        layout.addWidget(self.what_is_wrong_text)

        layout.addStretch(1)

        button_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent_window.switch_to_home)
        submit_button = QPushButton("Submit to AI")
        submit_button.clicked.connect(self.submit_to_ai)
        
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self):
        data = { "feeling": "", "what_is_wrong": self.what_is_wrong_text.toPlainText().strip() }
        if self.happy_face.isChecked(): data["feeling"] = "Happy 😊"
        elif self.sad_face.isChecked(): data["feeling"] = "Sad 😢"
        elif self.upset_face.isChecked(): data["feeling"] = "Upset 😠"
        return data

    def submit_to_ai(self):
        checkin_data = self.get_data()
        self.parent_window.switch_to_ai_page(initial_context=checkin_data)

# --- AI PAGE ---
class AIPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type here to talk to me...")
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        self.user_input.returnPressed.connect(self.send_message)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(send_button)

        back_button = QPushButton("Back to Home")
        back_button.clicked.connect(self.parent_window.switch_to_home)
        
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def start_conversation(self, initial_context=None):
        self.chat_display.clear()
        if initial_context:
            self.chat_display.append("<b style='color:#0D3B66;'>HUSH AI:</b> Thanks for checking in. I see that:")
            if initial_context.get("feeling"): self.chat_display.append(f"- You're feeling: {initial_context['feeling']}")
            if initial_context.get("what_is_wrong"): self.chat_display.append(f"- The problem is: {initial_context['what_is_wrong']}")
            self.chat_display.append("<br><b style='color:#0D3B66;'>HUSH AI:</b> I'm here for you. Please tell me more.")
        else:
            self.chat_display.append("<b style='color:#0D3B66;'>HUSH AI:</b> I'm here to help. Tell me what's happening.")
        self.user_input.setFocus()
    
    def send_message(self):
        user_text = self.user_input.text().strip()
        if not user_text: return
        self.chat_display.append(f"<b style='color:#4D6A92;'>You:</b> {user_text}")
        self.user_input.clear()
        ai_response = "I understand. Thank you for sharing. What else is on your mind?"
        self.chat_display.append(f"<b style='color:#0D3B66;'>HUSH AI:</b> {ai_response}")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HushApp()
    window.show()
    sys.exit(app.exec_())