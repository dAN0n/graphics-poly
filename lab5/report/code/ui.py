# PyQt5 Video player
#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QLineEdit, QDesktopWidget
from PyQt5.QtGui import QIcon
import sys
from tracker import ObjectRectangle, Tracker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Трекер движения объекта')

        layout = QVBoxLayout()
        self.firstFrameBtn = QPushButton("1ый кадр")
        self.firstFrameLine = QLineEdit(self)
        self.secondFrameLine = QLineEdit(self)

        self.xObjectLine = QLineEdit(self)
        self.yObjectLine = QLineEdit(self)
        self.xOffsetObjectLine = QLineEdit(self)
        self.yOffsetObjectLine = QLineEdit(self)

        self.frameCount = QLineEdit(self)

        self.frameCountLabel = QLabel("Кол-во кадров")

        self.selectBtn = QPushButton("Выбрать объект")
        self.selectBtn.setEnabled(False)
        self.startBtn = QPushButton("Старт!")

        self.firstFrameBtn.clicked.connect(self.selectFile)
        self.selectBtn.clicked.connect(self.selectObject)
        self.startBtn.clicked.connect(self.start)

        self.firstFrameLine.textChanged.connect(self.enableSelectBtn)
        self.secondFrameLine.textChanged.connect(self.enableSelectBtn)

        h1l = QHBoxLayout()
        h1l.addWidget(self.firstFrameLine, 3)
        h1l.addWidget(self.secondFrameLine, 1)
        h1l.addWidget(self.firstFrameBtn, 1)

        h2l = QHBoxLayout()
        h2l.addWidget(self.xObjectLine)
        h2l.addWidget(self.yObjectLine)
        h2l.addWidget(self.xOffsetObjectLine)
        h2l.addWidget(self.yOffsetObjectLine)
        h2l.addWidget(self.selectBtn)

        v1l = QVBoxLayout()
        v1l.addWidget(self.frameCountLabel)
        v1l.addWidget(self.frameCount)

        h3l = QHBoxLayout()
        h3l.addLayout(v1l)

        layout.addLayout(h1l)
        layout.addLayout(h2l)
        layout.addLayout(h3l)
        layout.addWidget(self.startBtn)
        self.setLayout(layout)

        self.player = VideoWindow(self)
        
        self.setGeometry(0, 0, 500, 100)
        window = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        window.moveCenter(centerPoint)
        self.move(window.topLeft())

        self.show()

    def selectFile(self):
        self.player.show()

    def enableSelectBtn(self):
        if self.firstFrameLine.text() != "" and self.secondFrameLine.text() != "":
            self.selectBtn.setEnabled(True)
        else:
            self.selectBtn.setEnabled(False)

    def selectObject(self):
        obj = ObjectRectangle(self.firstFrameLine.text(), int(self.secondFrameLine.text()))
        obj.showFrame()
        coord = obj.getCoordinates()

        self.xObjectLine.setText(str(coord[0]))
        self.yObjectLine.setText(str(coord[1]))
        self.xOffsetObjectLine.setText(str(coord[2]))
        self.yOffsetObjectLine.setText(str(coord[3]))

    def start(self):
        self.startBtn.setEnabled(False)
        self.selectBtn.setEnabled(False)
        self.firstFrameBtn.setEnabled(False)
        self.startBtn.setText("Пожалуйста, подождите пару минут...")
        
        coord = [
            int(self.xObjectLine.text()),
            int(self.yObjectLine.text()),
            int(self.xOffsetObjectLine.text()),
            int(self.yOffsetObjectLine.text()),
        ]

        t = Tracker(
            self.firstFrameLine.text(),
            int(self.secondFrameLine.text()),
            int(self.frameCount.text()),
            coord)
        t.find_object()
        t.draw_frames()
        
        self.startBtn.setText("Старт!")
        self.startBtn.setEnabled(True)
        self.selectBtn.setEnabled(True)
        self.firstFrameBtn.setEnabled(True)

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Выберите первый кадр")
        self.resize(800, 600)
        
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.fileName = None

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.okBtn = QPushButton("OK")
        self.okBtn.clicked.connect(self.selectFrame)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.okBtn)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie")

        if self.fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.fileName)))
            self.playButton.setEnabled(True)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def selectFrame(self):
        if self.fileName is not None:
            self.parent().firstFrameLine.setText(self.fileName)
            self.parent().secondFrameLine.setText(str(self.positionSlider.value()))
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())