from PySide6 import QtCore, QtWidgets

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        # Button to start the process
        self.button = QtWidgets.QPushButton("Run Command")
        self.layout.addWidget(self.button)

        # Text area to display output
        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setReadOnly(True)
        self.layout.addWidget(self.text_output)

        # QProcess instance
        self.process = QtCore.QProcess(self)

        # Connect button to start process
        self.button.clicked.connect(self.run_command)

        # Connect process signals to slots
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)

    def run_command(self):
        # Command to run (e.g., `ls` or `roslaunch`)
        self.process.start("cmd", ["/c", "dir"])

    def read_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.text_output.append(output)

    def read_stderr(self):
        error = self.process.readAllStandardError().data().decode()
        self.text_output.append(f"<span style='color:red;'>{error}</span>")

    def process_finished(self):
        self.text_output.append("<span style='color:green;'>Process finished.</span>")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
