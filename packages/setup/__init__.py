from .window import SetupWindow, QApplication

def setup(argv = []):
    app = QApplication(argv)
    wnd = SetupWindow()
    wnd.show()
    return app.exec()