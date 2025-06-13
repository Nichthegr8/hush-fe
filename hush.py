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
PRIMARY_COLOR = "#0D3B66"    # Deep, confident navy blue
ACCENT_COLOR = "#4D6A92"     # Softer steel‑blue for highlights
TEXT_COLOR = "#424242"       # Neutral dark gray—unchanged
EMERGENCY_COLOR = "#D32F2F"  # Strong red—unchanged
BACKGROUND_COLOR = "#B4D6E3" # Light, airy blue background
ERROR_COLOR = "#D32F2F"      # Same red for errors

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
        self.home_screen = HomeScreen(self)
        self.check_in_screen = CheckInScreen(self)

        # Add screens to the stack
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.check_in_screen)

        # Set the main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)

        # Apply the application-wide styles
        self.apply_stylesheet()
        
        # Start on the home screen
        self.stacked_widget.setCurrentWidget(self.home_screen)

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

    def switch_to_checkin(self):
        """Switches the view to the Check-In Screen."""
        self.stacked_widget.setCurrentWidget(self.check_in_screen)

    def switch_to_home(self):
        """Switches the view to the Home Screen."""
        self.stacked_widget.setCurrentWidget(self.home_screen)
        
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

        q2_label = QLabel("<b>2. How can I help?</b>")
        layout.addWidget(q2_label)
        
        self.how_to_help_text = QTextEdit()
        self.how_to_help_text.setPlaceholderText("Tell me here...")
        self.how_to_help_text.setFixedHeight(60)
        layout.addWidget(self.how_to_help_text)

        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        button_layout.addWidget(self.submit_button)
        
        layout.addStretch(1)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def submit(self):
        pass # Replace with sockcomm to send info

    def create_face_button(self, text):
        button = QPushButton(text)
        button.setObjectName("FaceButton")
        button.setCheckable(True)
        button.setFixedSize(QSize(80, 80))
        return button
    
    def clear_fields(self):
        """Resets all fields on the check-in screen to their default state."""
        self.what_is_wrong_text.clear()
        self.happy_face.setChecked(False)
        self.sad_face.setChecked(False)
        self.upset_face.setChecked(False)

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
        
        top_bar_layout.addWidget(self.welcome_label)
        top_bar_layout.addStretch(1)
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

        self.setLayout(layout)

    def welcome_user(self, username):
        self.welcome_label.setText(f"<b>Welcome, {username}!</b>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HushApp()
    window.show()
    sys.exit(app.exec_())    
