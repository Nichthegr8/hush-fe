
import hashlib
import sys
import json
import os
import tempfile

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt, Image

import packages.connectors as connectors
import packages.config as config
import packages.audiorecorder as audiorecorder

# --- Constants ---
USER_PROFILES_DIR = "user_profiles"
CACHE_FILE = "app_cache.json"
PRIMARY_COLOR = "#0D3B66"      # Deep, confident navy blue
ACCENT_COLOR = "#4D6A92"      # Softer steel-blue for highlights
TEXT_COLOR = "#424242"        # Neutral dark gray—unchanged
EMERGENCY_COLOR = "#D32F2F"    # Strong red—unchanged
BACKGROUND_COLOR = "#B4D6E3"  # Light, airy blue background
ROUNDEDWIDGET_COLOR = "#C4E6F3"  # Light, airy blue background
ERROR_COLOR = "#D32F2F"        # Same red for errors
FONT_SIZE = "20px"

# --- Helper Functions --
def load_image(image_path, scaleFactor=.3):
    if not os.path.exists(image_path):
        print(f"Warning: Image file not found at '{image_path}'.")
        return QPixmap()
    img = Image.open(image_path)
    img = img.resize((int(img.width * scaleFactor), int(img.height * scaleFactor)))
    qim = ImageQt(img)
    pix = QPixmap.fromImage(qim)
    return pix

# --- Rounded widget ---

class signalHolder(QWidget):
    signal = pyqtSignal(str)

class RoundedWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumHeight(50)
        self.setContentsMargins(12, 12, 12, 12)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        color = QColor(ROUNDEDWIDGET_COLOR)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 42, 42)
        super().paintEvent(event)

# --- Main Application Window ---
class HushApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HUSH")
        self.setGeometry(100, 100, 567, 1162)
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
        self.ai_page = AIPage(self)
        self.ai_page.start_conversation()

        # --- Add screens to the stack ---
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
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
                font-size: {FONT_SIZE};
                font-weight: bold;
                color: {PRIMARY_COLOR};
                border: 2px solid {ACCENT_COLOR};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QCheckBox {{
                font-size: {FONT_SIZE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: {FONT_SIZE};
            }}
            QLabel#Title {{
                font-size: {FONT_SIZE};
                font-weight: bold;
                color: {PRIMARY_COLOR};
                padding-bottom: 10px;
            }}
            QLabel#ErrorLabel {{
                color: {ERROR_COLOR};
                font-size: {FONT_SIZE};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: {FONT_SIZE};
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
                font-size: {FONT_SIZE};
                color: {TEXT_COLOR};
            }}
            QTextEdit#ChatDisplay {{
                background-color: #FFFFFF;
                border: 2px solid {ACCENT_COLOR};
            }}
            QPushButton#LinkButton {{
                background-color: transparent;
                color: {PRIMARY_COLOR};
                font-size: {FONT_SIZE};
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
        self.switch_to_ai_page()

    def switch_to_ai_page(self):
        self.stacked_widget.setCurrentWidget(self.ai_page)


# --- LOGIN SCREEN ---
class LoginScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.load_cached_info()

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

        prof_cs = connectors.profilesClientSide(config.PROFL_SERVICE_HOST)
        prof_cs.onClientError = lambda error: self.error_label.setText(error)
        prof_cs.onGotProfile = lambda profile: self.onGotProfile(profile, prof_cs)
        prof_cs.log_in(username, password)

    def onGotProfile(self, profile: dict, prof_cs: connectors.profilesClientSide):
        prof_cs.sclient.close()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        self.cache_info(username, password)
        self.parent_window.login_successful(profile)
    
    def cache_info(self, username, password):
        with open(CACHE_FILE, 'w') as f:
            json.dump({'username': username, 'password': password}, f)

    def load_cached_info(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    self.username_input.setText(cache["username"])
                    self.password_input.setText(cache["password"])
                    self.attempt_login()
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
        self.dob_input = QLineEdit()
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

        # --- Gather all data into a dictionary ---
        profile_data = {
            "credentials": {
                "username": username,
                "password": hashlib.sha256(password.encode()).hexdigest()
            },
            "general": {
                "first_name": self.first_name_input.text(),
                "last_name": self.last_name_input.text(),
                "gender": self.gender_input.currentText(),
                "dob": self.dob_input.text()
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
            profl_cs = connectors.profilesClientSide(config.PROFL_SERVICE_HOST)
            profl_cs.sign_up(profile_data)
            profl_cs.onClientError = lambda error: self.error_label.setText(error)
            profl_cs.onSignupSuccess = lambda: self.parent_window.switch_to_login()
        except IOError as e:
            self.error_label.setText(f"Error saving profile: {e}")

class HoverQPushButton(QPushButton):
    onhoverenter = pyqtSignal()
    onhoverexit = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def enterEvent(self, event):
        self.onhoverenter.emit()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.onhoverexit.emit()
        super().leaveEvent(event)

class AIPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def emoji_to_qicon(self, emoji: str, size: int = 64) -> QIcon:
        # Create a QPixmap to draw the emoji
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        # Use QPainter to draw the emoji text
        painter = QPainter(pixmap)
        font = QFont("Segoe UI Emoji", int(size * 0.5))  # Use emoji-compatible font
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    def create_emoji_button(self, emoji, label_text):
        button = QPushButton()
        icon_size = 64  # or however big you want the icon

        button.setIcon(self.emoji_to_qicon(emoji, size=icon_size))
        button.setIconSize(QSize(icon_size, icon_size))
        button.setFixedSize(QSize(icon_size + 16, icon_size + 16))  # allow some padding

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #DDEEFF;
                border-radius: {icon_size // 2}px;
            }}
        """)
        button.setToolTip(label_text)
        button.clicked.connect(lambda _, e=emoji: self.emoji_clicked(e))
        return button


    def emoji_clicked(self, emoji):
        pass


    def init_ui(self):
        layout = QVBoxLayout()

        q1_label = QLabel(f"<h2>How are you feeling right now?</h2>")
        layout.addWidget(q1_label)

        self.feelings_group = QHBoxLayout()
        feelings = [
            ("😢", "Sad"),
            ("😟", "Anxious"),
            ("😡", "Angry"),
            ("😨", "Scared"),
            ("🤕", "Hurt"),
        ]

        for emoji, text in feelings:
            vbox = QVBoxLayout()
            btn = self.create_emoji_button(emoji, text)
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            btn.clicked.connect(lambda *args, t=text: self.onEmojiClicked(t))
            vbox.addWidget(btn, alignment=Qt.AlignCenter)
            vbox.addWidget(label)
            self.feelings_group.addLayout(vbox)

        self.setLayout(layout)
        
        emergency_button = QPushButton("HELP")
        emergency_button.setStyleSheet("QPushButton { font-weight: bold; }")
        emergency_button.setFixedWidth(457)
        emergency_button.setFixedHeight(80)
        
        menu_label = QLabel()
        menu_label.setPixmap(load_image("logo.png"))
        
        menu_label.setFixedHeight(100)
        menu_label.setFixedWidth(100)

        menu_label.setStyleSheet(f"""
            QPushButton {{
                border-radius: 25px;
            }}
        """)
        
        profilepicture = HoverQPushButton(QIcon(load_image("profile.png")), None, None)
        
        profilepicture.setFixedHeight(80)
        profilepicture.setFixedWidth(80)
        profilepicture.setIconSize(QSize(80, 80)) 

        profilepicture.setStyleSheet(f"""
            QPushButton {{
                border-radius: 40px;
                background-color: none;
                background: none;
            }}
            QPushButton::hover {{
                border-radius: 40px;
                background-color: none;
                background: none;
            }}
        """)
        profilepicture.onhoverenter.connect(lambda pfp = profilepicture: self.pfpenter(pfp))
        profilepicture.onhoverexit.connect(lambda pfp = profilepicture: self.pfpexit(pfp))

        topbarlayout = QHBoxLayout()
        topbarlayout.addWidget(menu_label)
        #topbarlayout.addSpacing(75)
        topbarlayout.addWidget(emergency_button)
        #topbarlayout.addSpacing(75)
        topbarlayout.addWidget(profilepicture)

        self.chat_display = QVBoxLayout()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.addStretch(1)

        self.btnwrapper = RoundedWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type here to talk to me...")
        self.user_input.returnPressed.connect(self.send_message)

        self.send = QPushButton(QIcon("up_arrow.png"), "", None)
        self.send.clicked.connect(self.send_message)

        self.camera = QPushButton(QIcon("camera.png"), "", None)

        self.mic = QPushButton(QIcon("microphone.png"), "", None)

        self.user_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.send.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        fixed_height = 50
        self.user_input.setFixedHeight(fixed_height+10)
        self.send.setFixedHeight(fixed_height)
        self.send.setFixedWidth(fixed_height)
        self.camera.setFixedHeight(fixed_height)
        self.camera.setFixedWidth(fixed_height)
        self.mic.setFixedHeight(fixed_height)
        self.mic.setFixedWidth(fixed_height)
        
        button_layout.addWidget(self.mic)
        button_layout.addWidget(self.camera)     
        button_layout.addWidget(self.user_input)
        button_layout.addWidget(self.send)

        self.btnwrapper.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ROUNDEDWIDGET_COLOR};
                border: 2px solid {ROUNDEDWIDGET_COLOR};
                padding: 10px;
                font-size: {FONT_SIZE};
                color: {TEXT_COLOR};
            }}
            QPushButton {{
                border-radius: 25px;
            }}""")
        
        self.btnwrapper.setLayout(button_layout)
        self.mic.clicked.connect(self.onmicclicked)

        # Container widget for layout
        chat_container = QWidget()
        chat_container.setLayout(self.chat_display)

        # Scroll area to wrap the container
        chat_scroll_area = QScrollArea()
        chat_scroll_area.setWidgetResizable(True)
        chat_scroll_area.setWidget(chat_container)
        chat_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addLayout(topbarlayout)
        layout.addSpacing(40)
        layout.addWidget(q1_label)
        layout.addLayout(self.feelings_group)
        layout.addSpacing(40)
        layout.addWidget(chat_scroll_area)
        layout.addWidget(self.btnwrapper)
        self.setLayout(layout)
        self.llmcs = connectors.llmClientSide(self.parent_window.current_user_data, config.LLM_SERVICE_HOST)
        self.llmcs.onendstream = self.onendstreamprompt
        self.oes = lambda:None
        self.audiorecorder = None
        self.ad_cs = connectors.audioDescClientSide(config.AUDESC_SERVICE_HOST)
        self.ad_cs.gotAudioDescription = self.onaudiodescribed

    def pfpenter(self, button: QPushButton):
        button.setIcon(QIcon(load_image("profile-hover.png")))

    def pfpexit(self, button: QPushButton):
        button.setIcon(QIcon(load_image("profile.png")))

    def onmicclicked(self):
        if self.audiorecorder:
            self.endmic()
        else:
            self.startmic()

    def startmic(self):
        self.audiorecorder = audiorecorder.Recorder()
        self.audiorecorder.start_recording()

    def endmic(self):
        frames = self.audiorecorder.stop_recording()
        tmpfile = tempfile.mktemp(".wav", "tmp", tempfile.gettempdir())
        self.audiorecorder.frames_to_file(frames, tmpfile)
        self.audiorecorder.frames_to_file(frames, "test2.wav")
        self.ad_cs.describe(tmpfile)
        self.audiorecorder = None

    def onaudiodescribed(self, description):
        self.showSendPrompt(description)
        ai_response = QLabel("")
        self.chat_display.addWidget(ai_response)
        self.llmcs.addToStream = lambda text: self.onStreamPartRecieved(text, ai_response)
        self.llmcs.generate_response(f"{{'input-type': 'text', 'description': '{description}'}}")

    def start_conversation(self):
        self.addwidgettostretchlay(QLabel("I'm here to help. Tell me what's happening."), self.chat_display)
        self.user_input.setFocus()

    def addwidgettostretchlay(self, widget, layout: QBoxLayout):
        stretch_index = layout.count()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.spacerItem() is not None:
                stretch_index = i
                break
        layout.insertWidget(stretch_index, widget)

    def addlayouttostretchlay(self, widget, layout: QBoxLayout):
        stretch_index = layout.count()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.spacerItem() is not None:
                stretch_index = i
                break
        layout.insertLayout(stretch_index, widget)
    
    def send_message(self):
        user_text = self.user_input.text().strip()
        if not user_text: return

        usermessagewidget = QWidget()
        layout = QHBoxLayout(usermessagewidget)
        layout.addStretch(1)
        usermessagewidget.setStyleSheet(f"""background-color: #d2f0ff;
                            color: #000;
                            padding: 10px;
                            border-radius: 12px;
                            font-size: {FONT_SIZE};
                            margin: 6px 0;""")
        layout.addWidget(QLabel(user_text))
        usermessagewidget.setLayout(layout)

        usermessagelayout = QHBoxLayout()
        usermessagelayout.addStretch(1)
        usermessagelayout.addWidget(usermessagewidget)

        self.addlayouttostretchlay(usermessagelayout, self.chat_display)
        self.user_input.clear()
        self.send.setDisabled(True)
        self.llmcs.onendstream = self.onendstreamprompt
        ai_response = QLabel("")
        ai_response.setWordWrap(True)
        sigh = signalHolder()
        sigh.signal.connect(lambda text: self.onStreamPartRecieved(text, ai_response))
        self.llmcs.addToStream = lambda text: sigh.signal.emit(text)
        self.llmcs.generate_response(f"{{'input-type': 'text', 'content': '{user_text}'}}")
        self.addwidgettostretchlay(ai_response, self.chat_display)

    def onendstreamprompt(self):
        self.send.setDisabled(False)
        self.llmcs.addToStream = self.oes

    def showSendPrompt(self, prompt):
        usermessagewidget = QWidget()
        layout = QHBoxLayout(usermessagewidget)
        layout.addStretch(1)
        usermessagewidget.setStyleSheet(f"""background-color: #d2f0ff;
                            color: #000;
                            padding: 10px;
                            border-radius: 12px;
                            font-size: {FONT_SIZE};
                            margin: 6px 0;""")
        layout.addWidget(QLabel(prompt))
        usermessagewidget.setLayout(layout)

        usermessagelayout = QHBoxLayout()
        usermessagelayout.addStretch(1)
        usermessagelayout.addWidget(usermessagewidget)

        self.addlayouttostretchlay(usermessagelayout, self.chat_display)

    def onEmojiClicked(self, emoji: str):
        self.showSendPrompt(f"I am {emoji}")

        self.send.setDisabled(True)

        ai_response = QLabel("")
        ai_response.setWordWrap(True)
        sigh = signalHolder()
        sigh.signal.connect(lambda text: self.onStreamPartRecieved(text, ai_response))
        self.llmcs.addToStream = lambda text: sigh.signal.emit(text)
        self.llmcs.generate_response(f"{{'input-type': 'text', 'content': 'I am {emoji}'}}")

        self.addwidgettostretchlay(ai_response, self.chat_display)

    def onStreamPartRecieved(self, text: str, qlabel: QLabel):
        qlabel.setText(qlabel.text()+text)

# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HushApp()
    window.show()
    sys.exit(app.exec_())