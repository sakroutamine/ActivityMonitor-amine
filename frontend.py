import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
                             QLabel, QMessageBox, QInputDialog, QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import QTimer, QTime, Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QIcon
from ActivityTracker import ActivityTracker  # Assuming ActivityTracker.py is the filename


class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super(CircularProgressBar, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(150, 150)  # Size of the circle
        self.value = 0

    def setValue(self, val):
        self.value = val
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen()
        pen.setWidth(10)

        # Adjust to ensure circle is not elliptical
        side = min(self.width(), self.height())
        rect = QRect((self.width() - side) // 2, (self.height() - side) // 2, side, side)

        # Unfilled Circle
        pen.setColor(QColor("#edf756"))  # Dusty White
        painter.setPen(pen)
        painter.drawArc(rect.adjusted(10, 10, -10, -10), 0, 360 * 16)

        # Filled Arc
        pen.setColor(QColor("#51e2f5"))  # Bright Blue
        painter.setPen(pen)
        spanAngle = int(-self.value * 16)
        painter.drawArc(rect.adjusted(10, 10, -10, -10), 0, spanAngle)

class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.activityTracker = ActivityTracker()  # Create an instance of ActivityTracker

    def initUI(self):
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 400, 200)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QHBoxLayout(self.centralWidget)

        # Menu Button
        self.menuButton = QPushButton("☰", self)
        self.menuButton.setStyleSheet("font-size: 24px; padding: 10px;")
        self.menuButton.setFixedWidth(50)
        self.menuButton.clicked.connect(self.toggleMenu)
        self.mainLayout.addWidget(self.menuButton)

        # Frame for Settings
        self.settingsFrame = QFrame(self)
        self.settingsLayout = QVBoxLayout(self.settingsFrame)
        self.settingsFrame.setFixedWidth(200)
        self.settingsFrame.setVisible(False)  # Hidden by default
        self.mainLayout.addWidget(self.settingsFrame)

        # Circular Progress Bar and Timer
        self.progressBar = CircularProgressBar(self)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label = QLabel("25:00", self)
        self.label.setFont(QFont("Arial", 40))
        self.label.setAlignment(Qt.AlignCenter)

        # Timer Layout
        self.timerLayout = QVBoxLayout()
        self.timerLayout.addWidget(self.progressBar)
        self.timerLayout.addWidget(self.label)

        # Control Buttons Layout
        self.controlButtonsLayout = QHBoxLayout()

        # Skip Button with an Icon
        self.skipButton = QPushButton("", self)
        self.skipButton.setIcon(QIcon("skip_icon.png"))  # Replace with your skip icon file path
        self.skipButton.setIconSize(QSize(40, 40))
        self.skipButton.setStyleSheet("background-color: transparent; border: none;")
        self.skipButton.setFixedSize(60, 60)
        self.skipButton.clicked.connect(self.skipCurrentPhase)
        self.controlButtonsLayout.addWidget(self.skipButton)

        # Control Button (Start/Pause)
        self.controlButton = QPushButton("", self)
        self.controlButton.setIcon(QIcon("play_icon.png"))  # Replace with your play icon file path
        self.controlButton.setIconSize(QSize(40, 40))
        self.controlButton.setStyleSheet("background-color: transparent; border: none;")
        self.controlButton.clicked.connect(self.startPauseTimer)
        self.controlButton.setFixedSize(60, 60)
        self.controlButtonsLayout.addWidget(self.controlButton)

        # Add Control Buttons Layout to Timer Layout
        self.timerLayout.addLayout(self.controlButtonsLayout)

        # Add Timer Layout to Main Layout
        self.mainLayout.addLayout(self.timerLayout)

        # Adding Buttons to the Frame
        self.addButtonsToFrame()

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.defaultPomodoroMinutes = 25
        self.defaultBreakMinutes = 5
        self.time = QTime(0, self.defaultPomodoroMinutes, 0)
        self.totalSeconds = self.defaultPomodoroMinutes * 60
        self.isPomodoro = True


    def addButtonsToFrame(self):
        buttonStyle = "QPushButton {background-color: #2E3440; color: #ECEFF4; border-radius: 20px; padding: 10px; margin: 5px;} QPushButton:hover {background-color: #4C566A;}"

        # Reset Button
        self.resetButton = QPushButton("Reset", self)
        self.resetButton.setStyleSheet(buttonStyle)
        self.resetButton.clicked.connect(self.resetTimer)
        self.settingsLayout.addWidget(self.resetButton)

        # Edit Time Button
        self.editButton = QPushButton("Edit Time", self)
        self.editButton.setStyleSheet(buttonStyle)
        self.editButton.clicked.connect(self.editTime)
        self.settingsLayout.addWidget(self.editButton)

        # Add Edit Break Timer Button in Settings
        self.editBreakButton = QPushButton("Edit Break Time", self)
        self.editBreakButton.setStyleSheet(buttonStyle)
        self.editBreakButton.clicked.connect(self.editBreakTime)
        self.settingsLayout.addWidget(self.editBreakButton)
    def startPauseTimer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.controlButton.setIcon(QIcon("play_icon.png"))  # Change to play icon
            self.activityTracker.stop_tracking()  # Stop activity tracking
        else:
            self.timer.start(1000)
            self.controlButton.setIcon(QIcon("pause_icon.png"))  # Change to pause icon
            self.activityTracker.start_tracking()  # Start activity tracking

        # If the timer is stopped, reset the icon to 'play'
        if not self.timer.isActive():
            self.controlButton.setIcon(QIcon("play_icon.png"))

    def switchToBreak(self):
        self.isPomodoro = False
        self.time.setHMS(0, self.defaultBreakMinutes, 0)
        self.totalSeconds = self.defaultBreakMinutes * 60
        self.label.setText(self.time.toString("mm:ss"))
        self.progressBar.setValue(0)
        self.timer.start(1000)

    def toggleMenu(self):
        self.settingsFrame.setVisible(not self.settingsFrame.isVisible())  

    def startTimer(self):
        self.timer.start(1000)

    def pauseTimer(self):
        self.timer.stop()
       
    def skipCurrentPhase(self):
        if self.isPomodoro:
            self.prepareForBreak()
        else:
            self.prepareForPomodoro()
    
    def prepareForBreak(self):
        self.isPomodoro = False
        self.time.setHMS(0, self.defaultBreakMinutes, 0)
        self.totalSeconds = self.defaultBreakMinutes * 60
        self.label.setText("Break Time: " + self.time.toString("mm:ss"))  # Indicate break time
        self.progressBar.setValue(0)
        self.controlButton.setIcon(QIcon("play_icon.png"))  # Set to play icon

    def prepareForPomodoro(self):
        self.isPomodoro = True
        self.time.setHMS(0, self.defaultPomodoroMinutes, 0)
        self.totalSeconds = self.defaultPomodoroMinutes * 60
        self.label.setText("Work Time: " + self.time.toString("mm:ss"))  # Indicate work time
        self.progressBar.setValue(0)
        self.controlButton.setIcon(QIcon("play_icon.png"))  # Reset to play icon

    
    def resetTimer(self):
        self.timer.stop()
        if self.isPomodoro:
            self.time.setHMS(0, self.defaultPomodoroMinutes, 0)
        else:
            self.time.setHMS(0, self.defaultBreakMinutes, 0)
        self.progressBar.setValue(0)
        self.label.setText(self.time.toString("mm:ss"))

    def updateTimer(self):
        self.time = self.time.addSecs(-1)
        remainingTime = QTime(0, 0, 0).secsTo(self.time)
        progress = (1 - remainingTime / self.totalSeconds) * 360
        self.progressBar.setValue(progress)
        # Update label text based on current phase
        if self.isPomodoro:
            self.label.setText("Work Time: " + self.time.toString("mm:ss"))
        else:
            self.label.setText("Break Time: " + self.time.toString("mm:ss"))

        if self.time.toString("mm:ss") == "00:00":
            if self.isPomodoro:
                QMessageBox.information(self, "Pomodoro Finished", "Starting break.")
                self.prepareForBreak()
            else:
                QMessageBox.information(self, "Break Finished", "Pomodoro session completed.")
                self.prepareForPomodoro()
    
    def switchToBreak(self):
        self.isPomodoro = False
        self.time.setHMS(0, self.defaultBreakMinutes, 0)
        self.totalSeconds = self.defaultBreakMinutes * 60
        self.label.setText(self.time.toString("mm:ss"))
        self.progressBar.setValue(0)
        self.controlButton.setIcon(QIcon("play_icon.png"))  # Set to play icon
        self.timer.start(1000)

    def resetToPomodoro(self):
        self.isPomodoro = True
        self.time.setHMS(0, self.defaultPomodoroMinutes, 0)
        self.totalSeconds = self.defaultPomodoroMinutes * 60
        self.label.setText(self.time.toString("mm:ss"))
        self.progressBar.setValue(0)
        self.controlButton.setIcon(QIcon("play_icon.png"))  # Reset to play icon

    def editTime(self):
        if self.isPomodoro:
            minutes, ok = QInputDialog.getInt(self, "Edit Timer", "Enter Pomodoro minutes:", self.defaultPomodoroMinutes, 1, 60)
            if ok:
                self.defaultPomodoroMinutes = minutes
        else:
            minutes, ok = QInputDialog.getInt(self, "Edit Timer", "Enter Break minutes:", self.defaultBreakMinutes, 1, 60)
            if ok:
                self.defaultBreakMinutes = minutes

        if ok:
            self.resetTimer()
            self.totalSeconds = minutes * 60
    
    def editBreakTime(self):
        minutes, ok = QInputDialog.getInt(self, "Edit Break Timer", "Enter break minutes:", self.defaultBreakMinutes, 1, 60)
        if ok:
            self.defaultBreakMinutes = minutes

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = PomodoroTimer()
    mainWin.show()
    sys.exit(app.exec_())
