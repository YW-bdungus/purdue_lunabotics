import sys
import os
import datetime
import re
from PySide6 import QtCore, QtWidgets

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        self.layout = QtWidgets.QGridLayout(self)

        # Sections
        self.init_launch_section()
        self.init_mode_section()
        self.init_checkbox_section()
        self.init_fullstop_button()
        self.init_status_window()
        self.init_readings_window()
        self.init_behavior_window()
        self.init_text_log()
        self.init_export_button()

        # Log storage
        self.log_entries = []

        # Process manager
        self.launch_manager = LaunchManager()
        self.launch_manager.process_started.connect(self.log_output)
        self.launch_manager.process_output.connect(self.log_output)
        self.launch_manager.process_error.connect(self.log_output)
        self.launch_manager.process_finished.connect(self.log_output)
        self.launch_manager.process_exists.connect(self.log_output)

        # Connect signals
        self.button_launch_robot.clicked.connect(self.execute_launch_robot)
        self.button_launch_computer.clicked.connect(self.execute_launch_computer)
        self.button_init_robot.clicked.connect(self.execute_init_robot)
        self.fullstop.clicked.connect(self.execute_fullstop)
        self.export_button.clicked.connect(self.export_logs)
        self.mode_autonomous.toggled.connect(self.execute_mode)
        self.main_camera_checkbox.toggled.connect(self.execute_main_camera)
        self.recording_checkbox.toggled.connect(self.execute_recording)
        self.foxglove_checkbox.toggled.connect(self.execute_foxglove)
        self.slam_checkbox.toggled.connect(self.execute_slam)
        self.teensy_checkbox.toggled.connect(self.execute_teensy)

        # Layout adjustments
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 5)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)
        self.layout.setColumnStretch(2, 3)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(20)

        # Window settings
        self.setWindowTitle("Lunabot GUI (resizable)")
        self.resize(800, 600)

    # Initialization methods
    def init_launch_section(self):
        group = QtWidgets.QGroupBox("Launch", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.button_launch_robot = QtWidgets.QPushButton("Launch Robot")
        self.button_launch_computer = QtWidgets.QPushButton("Launch Computer")
        self.button_init_robot = QtWidgets.QPushButton("Init Robot")
        self.button_init_robot.setStyleSheet('background-color: green; font-weight: bold;')
        for btn in (self.button_launch_robot, self.button_launch_computer, self.button_init_robot):
            layout.addWidget(btn)
        self.layout.addWidget(group, 0, 0)

    def init_mode_section(self):
        group = QtWidgets.QGroupBox("Mode", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.mode_autonomous = QtWidgets.QCheckBox("Autonomous Mode")
        layout.addWidget(self.mode_autonomous)
        self.layout.addWidget(group, 1, 0)

    def init_checkbox_section(self):
        group = QtWidgets.QGroupBox("Controls", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.main_camera_checkbox = QtWidgets.QCheckBox("Cameras")
        self.recording_checkbox   = QtWidgets.QCheckBox("Record")
        self.foxglove_checkbox    = QtWidgets.QCheckBox("Foxglove")
        self.slam_checkbox        = QtWidgets.QCheckBox("Slam")
        self.teensy_checkbox      = QtWidgets.QCheckBox("Teensy")
        for cb in (self.main_camera_checkbox, self.recording_checkbox,
                   self.foxglove_checkbox, self.slam_checkbox,
                   self.teensy_checkbox):
            cb.setChecked(False)
            layout.addWidget(cb)
        self.layout.addWidget(group, 2, 0)

    def init_fullstop_button(self):
        self.fullstop = QtWidgets.QPushButton("FULL STOP")
        self.fullstop.setStyleSheet('background-color: red; font-weight: bold;')
        self.layout.addWidget(self.fullstop, 1, 1, alignment=QtCore.Qt.AlignCenter)

    def init_status_window(self):
        group = QtWidgets.QGroupBox("Status", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("Status updates…")
        layout.addWidget(self.status_text)
        self.layout.addWidget(group, 2, 1)

    def init_readings_window(self):
        group = QtWidgets.QGroupBox("Readings", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.readings_text = QtWidgets.QTextEdit()
        self.readings_text.setReadOnly(True)
        self.readings_text.setPlaceholderText("Readings will appear here…")
        layout.addWidget(self.readings_text)
        self.layout.addWidget(group, 0, 1)

    def init_behavior_window(self):
        group = QtWidgets.QGroupBox("Behavior", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.behavior_text = QtWidgets.QTextEdit()
        self.behavior_text.setReadOnly(True)
        self.behavior_text.setPlaceholderText("Behavior outputs…")
        layout.addWidget(self.behavior_text)
        self.layout.addWidget(group, 2, 2)

    def init_text_log(self):
        group = QtWidgets.QGroupBox("Log", self)
        layout = QtWidgets.QVBoxLayout(group)
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        self.layout.addWidget(group, 0, 2)

    def init_export_button(self):
        self.export_button = QtWidgets.QPushButton("Export Logs")
        self.export_button.setStyleSheet('background-color: blue; color: white; font-weight: bold;')
        self.layout.addWidget(self.export_button, 1, 2, alignment=QtCore.Qt.AlignCenter)

    # Logging helpers
    def get_timestamp(self):
        return datetime.datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "]"

    def get_timestamp_for_sorting(self, entry):
        m = re.match(r'\[(\d{2}):(\d{2}):(\d{2})\.(\d{3})\]', entry)
        return int(m.group(1))*3600000 + int(m.group(2))*60000 + int(m.group(3))*1000 + int(m.group(4)) if m else 0

    def log_output(self, text, pid=None):
        ts = self.get_timestamp()
        entry = f"{ts} [Process {pid}] {text}" if pid is not None else f"{ts} {text}"
        self.log_text.append(entry)
        self.log_entries.append(entry)

    def log_command(self, cmd, pid):
        ts = self.get_timestamp()
        entry = f"{ts} [Process {pid}] Executing command: {cmd}"
        self.log_text.append(entry)
        self.log_entries.append(entry)

    def export_logs(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs", exist_ok=True)
        path = os.path.join("logs", f"lunabot_logs_{ts}.txt")
        with open(path, "w") as f:
            f.write(f"LunaBot Log Export - {datetime.datetime.now()}\n")
            f.write("-"*60 + "\n")
            for e in sorted(self.log_entries, key=self.get_timestamp_for_sorting):
                f.write(e + "\n")
        QtWidgets.QMessageBox.information(self, "Exported", f"Logs saved to {path}")
        self.log_output(f"Logs exported to {path}")

    # Slots
    def execute_init_robot(self):
        # Initialize all except SLAM checkbox remains untouched
        for cb in (self.main_camera_checkbox, self.recording_checkbox,
                   self.foxglove_checkbox, self.teensy_checkbox,
                   self.mode_autonomous):
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)
        self.log_output("Initializing essential systems…")
        self.execute_main_camera(True)
        self.execute_recording(True)
        self.execute_foxglove(True)
        self.execute_teensy(True)
        self.execute_mode(True)
        self.button_init_robot.setEnabled(False)
        self.button_init_robot.setText("Robot Initialized")
        self.button_init_robot.setStyleSheet('background-color: gray; font-weight: bold;')
        self.log_output("Robot initialization complete!")

    def execute_launch_robot(self):
        cmd = "roslaunch lunabot_bringup robot.launch"
        pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "robot.launch"])
        if pid:
            self.log_command(cmd, pid)

    def execute_launch_computer(self):
        cmd = "roslaunch lunabot_bringup computer.launch"
        pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "computer.launch"])
        if pid:
            self.log_command(cmd, pid)

    def execute_fullstop(self):
        cmd = "python fullstop.py"
        pid = self.launch_manager.start_roslaunch("python", ["fullstop.py"])
        if pid:
            self.log_command(cmd, pid)
        self.launch_manager.terminate_all_processes()
        self.log_output("FULL STOP executed — all processes terminated")
        for cb in (self.main_camera_checkbox, self.recording_checkbox,
                   self.foxglove_checkbox, self.slam_checkbox,
                   self.teensy_checkbox, self.mode_autonomous):
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self.button_init_robot.setEnabled(True)
        self.button_init_robot.setText("Init Robot")
        self.button_init_robot.setStyleSheet('background-color: green; font-weight: bold;')

    def execute_mode(self, checked):
        cmd = "roslaunch lunabot_bringup auto_mode.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "auto_mode.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid:
                self.launch_manager.terminate_process(pid)
                self.log_output(f"Killed auto_mode process {pid}")

    def execute_main_camera(self, checked):
        cmd = "roslaunch lunabot_perception cameras.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_perception", "cameras.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid:
                self.launch_manager.terminate_process(pid)
                self.log_output(f"Killed cameras.launch process {pid}")
            else:
                self.log_output("No cameras.launch process to kill")

    def execute_recording(self, checked):
        cmd = "roslaunch lunabot_bringup record.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "record.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid:
                self.launch_manager.terminate_process(pid)
                self.log_output(f"Killed record.launch process {pid}")
            else:
                self.log_output("No record.launch process to kill")

    def execute_foxglove(self, checked):
        cmd = "roslaunch foxglove_bridge foxglove_bridge.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["foxglove_bridge", "foxglove_bridge.launch"])


    def execute_main_camera(self, checked):
        cmd = "roslaunch lunabot_perception cameras.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_perception", "cameras.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid and self.launch_manager.terminate_process(pid):
                self.log_output(f"Killed cameras.launch process {pid}")
            else:
                self.log_output("No cameras.launch process to kill")

    def execute_recording(self, checked):
        cmd = "roslaunch lunabot_bringup record.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "record.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid and self.launch_manager.terminate_process(pid):
                self.log_output(f"Killed record.launch process {pid}")
            else:
                self.log_output("No record.launch process to kill")

    def execute_foxglove(self, checked):
        cmd = "roslaunch foxglove_bridge foxglove_bridge.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["foxglove_bridge", "foxglove_bridge.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid and self.launch_manager.terminate_process(pid):
                self.log_output(f"Killed foxglove_bridge.launch process {pid}")
            else:
                self.log_output("No foxglove_bridge.launch process to kill")

    def execute_slam(self, checked):
        cmd = "roslaunch lunabot_slam slam.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_slam", "slam.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid and self.launch_manager.terminate_process(pid):
                self.log_output(f"Killed slam.launch process {pid}")
            else:
                self.log_output("No slam.launch process to kill")

    def execute_teensy(self, checked):
        cmd = "roslaunch lunabot_bringup teensy.launch"
        if checked:
            pid = self.launch_manager.start_roslaunch("roslaunch", ["lunabot_bringup", "teensy.launch"])
            if pid:
                self.log_command(cmd, pid)
        else:
            pid = self.launch_manager.find_process_id(cmd)
            if pid and self.launch_manager.terminate_process(pid):
                self.log_output(f"Killed teensy.launch process {pid}")
            else:
                self.log_output("No teensy.launch process to kill")

    def resizeEvent(self, event):
        scale = self.width() / 800
        style = f"""
            QPushButton {{ font-size: {int(14*scale)}px; padding: {int(10*scale)}px; }}
            QTextEdit  {{ font-size: {int(12*scale)}px; }}
            QGroupBox  {{ font-size: {int(14*scale)}px; }}
            QCheckBox  {{ font-size: {int(12*scale)}px; }}
        """
        self.setStyleSheet(style)

        btn_w = max(150, int(150*scale))
        btn_h = max(50,  int(50*scale))
        for btn in (
            self.button_launch_robot, self.button_launch_computer,
            self.button_init_robot, self.fullstop, self.export_button
        ):
            btn.setFixedSize(btn_w, btn_h)

        super().resizeEvent(event)


class LaunchManager(QtCore.QObject):
    process_started  = QtCore.Signal(str, str)
    process_output   = QtCore.Signal(str, str)
    process_error    = QtCore.Signal(str, str)
    process_finished = QtCore.Signal(str, str)
    process_exists   = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.active_processes = {}
        self.next_id = 1

    def is_command_running(self, cmd):
        return any(info['command'] == cmd for info in self.active_processes.values())

    def find_process_id(self, cmd):
        for pid, info in self.active_processes.items():
            if info['command'] == cmd:
                return pid
        return None

    def start_roslaunch(self, program, args=None):
        cmd_str = program if args is None else " ".join([program] + args)
        if self.is_command_running(cmd_str):
            self.process_exists.emit(f"Process '{cmd_str}' is already running. Not starting a duplicate.")
            return None

        proc = QtCore.QProcess()
        pid = str(self.next_id)
        self.next_id += 1
        self.active_processes[pid] = {'proc': proc, 'command': cmd_str}

        proc.started.connect(lambda: self.process_started.emit(f"Process {pid} started: {cmd_str}", pid))
        proc.readyReadStandardOutput.connect(lambda: self._read_stdout(pid))
        proc.readyReadStandardError.connect(lambda: self._read_stderr(pid))
        proc.finished.connect(lambda ec, es: self._handle_finished(pid, ec))

        if args is None:
            proc.start(program)
        else:
            proc.start(program, args)

        return pid

    def terminate_process(self, pid):
        info = self.active_processes.pop(pid, None)
        if not info:
            return False
        proc = info['proc']
        proc.terminate()
        if not proc.waitForFinished(3000):
            proc.kill()
        return True

    def terminate_all_processes(self):
        for pid in list(self.active_processes):
            self.terminate_process(pid)

    def _read_stdout(self, pid):
        out = self.active_processes[pid]['proc'].readAllStandardOutput().data().decode()
        self.process_output.emit(out, pid)

    def _read_stderr(self, pid):
        err = self.active_processes[pid]['proc'].readAllStandardError().data().decode()
        self.process_error.emit(err, pid)

    def _handle_finished(self, pid, exit_code):
        self.process_finished.emit(f"Process {pid} finished with exit code {exit_code}", pid)
        # Cleanup finished
        self.active_processes.pop(pid, None)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
