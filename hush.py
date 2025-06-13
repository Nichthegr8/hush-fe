import sys
import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# --- Constants ---
USER_PROFILES_DIR = "user_profiles"
PRIMARY_COLOR = "#FFA726"  # A calm, friendly orange
ACCENT_COLOR = "#FB8C00"
TEXT_COLOR = "#EEEEEE"
EMERGENCY_COLOR = "#D32F2F" # A strong but not overly aggressive red
BACKGROUND_COLOR = "#303030"
ERROR_COLOR = "#D32F2F"
ROUNDEDWIDGET_COLOR = "#424242"

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
            QPushButton#SendButton {{
                border-radius: 25px;
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
                background-color: {ROUNDEDWIDGET_COLOR};
                border: 2px solid {ROUNDEDWIDGET_COLOR};
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

        self.btnwrapper = RoundedWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("What do you need help with?")

        self.send = QPushButton("↑")
        self.send.clicked.connect(self.prompt)
        self.send.setObjectName("SendButton")

        self.prompt_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.send.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        fixed_height = 50
        self.prompt_input.setFixedHeight(fixed_height+10)
        self.send.setFixedHeight(fixed_height)
        self.send.setFixedWidth(fixed_height)
        
        button_layout.addWidget(self.prompt_input)
        button_layout.addWidget(self.send)
        
        self.btnwrapper.setLayout(button_layout)

        layout.addStretch(1)
        layout.addWidget(self.btnwrapper)
        self.setLayout(layout)

    def prompt(self):
        self.send
            
    def clear_fields(self):
        """Resets all fields on the check-in screen to their default state."""
        ...


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