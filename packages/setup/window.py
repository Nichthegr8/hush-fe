from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .data import JsonLData, EmergencyContact

class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, *args, **kwargs):
        for callback in self.callbacks:
            if callable(callback):
                callback(*args, **kwargs)


class CTextInput(QWidget):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lay = QHBoxLayout()

        self.onSubmit = Signal()

        self.textLabel = QLabel(text)
        self.sep = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.inputField = QLineEdit()

        self.inputField.returnPressed.connect(self.onSubmit.emit)

        self.lay.addWidget(self.textLabel)
        self.lay.addSpacerItem(self.sep)
        self.lay.addWidget(self.inputField)

        self.setLayout(self.lay)


class KeyFilter(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onKeyPressed = Signal()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.onKeyPressed.emit(event)
        return False


class CTextListInputItem(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lay = QHBoxLayout()

        self.onSubmit = Signal()
        self.onRemove = Signal()

        self.inputField = QLineEdit()
        self.sep1 = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.addBtn = QPushButton("Add", self)
        self.sep2 = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.removeBtn = QPushButton("X", self)

        self.inputField.returnPressed.connect(self.onSubmit.emit)
        self.addBtn.clicked.connect(self.onSubmit.emit)
        self.removeBtn.clicked.connect(self.onRemove.emit)

        self.key_filter = KeyFilter()
        self.key_filter.onKeyPressed.connect(self.backspacePressed)
        self.inputField.installEventFilter(self.key_filter)

        self.lay.addWidget(self.inputField)
        self.lay.addSpacerItem(self.sep1)
        self.lay.addWidget(self.addBtn)
        self.lay.addSpacerItem(self.sep2)
        self.lay.addWidget(self.removeBtn)

        self.setLayout(self.lay)

    def backspacePressed(self, event):
        kCode = 16777219  # Qt::Key_Backspace
        if event.key() == kCode and not self.inputField.text():
            self.onRemove.emit()


class CTextListInput(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lay = QVBoxLayout()
        self.inputs = []
        self.addItem()
        self.setLayout(self.lay)

    def addItem(self, *args, **kwargs):
        # Determine where to insert *before* adding the new item
        createAtIndex = len(self.inputs)  # default to end
        for index, item in enumerate(self.inputs):
            if item.inputField.hasFocus():
                createAtIndex = index + 1
                break

        item = CTextListInputItem()
        item.onSubmit.connect(self.addItem)
        item.onRemove.connect(lambda *args: self.removeItem(item))

        self.inputs.insert(createAtIndex, item)
        self.lay.insertWidget(createAtIndex, item)

        # Now safely set focus
        item.inputField.setFocus()

    def removeItem(self, item, *args):
        if type(item) == bool:
            item = args[0]
        if len(self.inputs) > 1:
            idx = self.inputs.index(item)
            self.lay.removeWidget(item)
            self.inputs.pop(idx)
            item.setParent(None)
            item.deleteLater()
            # Focus previous if possible
            if self.inputs:
                focus_idx = max(0, idx - 1)
                self.inputs[focus_idx].inputField.setFocus()

class HPair(QWidget):
    def __init__(self, items=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lay = QHBoxLayout()

        for item in items:
            try:
                self.lay.addWidget(item)
            except:
                try:
                    self.lay.addItem(item)
                except:
                    try:
                        self.lay.addSpacerItem(item)
                    except:
                        pass

        self.setLayout(self.lay)


class SetupWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lay = QVBoxLayout()

        self.setWindowTitle("HUSH Setup")

        self.toggle = QCheckBox("Dark Mode")
        self.toggle.setChecked(True)
        self.toggle.stateChanged.connect(self.toggle_theme)

        self.dark = True
        self.setdark()

        self.nameInput = CTextInput("Name:")
        self.birthDateInput = CTextInput("Date of birth:")
        self.diagnosisInput = CTextInput("Diagnosis:")
        self.symptomsInput = CTextListInput()
        self.symptomsInputPair = HPair([QLabel("Symptoms:"), self.symptomsInput])
        self.emergencyContactsInput = CTextListInput()
        self.emergencyContactsInputPair = HPair([QLabel("Emergency Contacts (name, phone number):"), self.emergencyContactsInput])
        self.ctechniqueInput = CTextListInput()
        self.ctechniqueInputPair = HPair([QLabel("Examples of working calming techniques:"), self.ctechniqueInput])

        self.submitBtn = QPushButton("Submit")
        self.submitBtn.clicked.connect(self.submit)

        self.lay.addWidget(self.toggle)
        self.lay.addWidget(self.nameInput)
        self.lay.addWidget(self.birthDateInput)
        self.lay.addWidget(self.diagnosisInput)
        self.lay.addWidget(self.symptomsInputPair)
        self.lay.addWidget(self.emergencyContactsInputPair)
        self.lay.addWidget(self.ctechniqueInputPair)
        self.lay.addWidget(self.submitBtn)

        self.setLayout(self.lay)

    def submit(self):
        name = self.nameInput.inputField.text()
        bday = self.birthDateInput.inputField.text()
        diag = self.diagnosisInput.inputField.text()

        symptoms = [i.inputField.text().strip() for i in self.symptomsInput.inputs]
        econtacts = [i.inputField.text().split(",") for i in self.emergencyContactsInput.inputs]
        ctechniques = [i.inputField.text().strip() for i in self.ctechniqueInput.inputs]

        jdata = JsonLData()
        jdata.set_name(name)
        jdata.set_birthdate(bday)
        jdata.set_diagnosis(diag)
        jdata.set_symptoms(symptoms)
        jdata.set_e_contacts([
            EmergencyContact(ec[0].strip(), ec[1].strip())
        for ec in econtacts])
        jdata.set_techniques(ctechniques)
        msg = QMessageBox()
        msg.setWindowTitle(self.windowTitle())
        try:
            jdata.save("data/profile.json")
            msg.setText("Successfully saved.\nSetup will now close.")
            msg.setIcon(QMessageBox.Information)
            hook = self.close
        except Exception as e:
            msg.setText(f"Error saving data:\n{e}")
            msg.setIcon(QMessageBox.Warning)
            hook = lambda:None
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        hook()

    def toggle_theme(self):
        self.dark = not self.dark
        if self.dark:
            self.setdark()
        else:
            self.setlight()

    def setdark(self):
        with open("packages/setup/dark.css")as f:
            self.setStyleSheet(f.read())

    def setlight(self):
        with open("packages/setup/light.css")as f:
            self.setStyleSheet(f.read())