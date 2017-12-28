import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDesktopWidget, QLineEdit, QFileDialog
from shiftvector import ShiftVector

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Поиск векторов смещения')

        layout = QVBoxLayout()
        self.firstFrameBtn = QPushButton("1 кадр")
        self.secondFrameBtn = QPushButton("2 кадр")
        self.firstFrameLine = QLineEdit(self)
        self.secondFrameLine = QLineEdit(self)

        self.blockSize = QLineEdit(self)
        self.stepSize = QLineEdit(self)
        self.windowSize = QLineEdit(self)

        self.blockSizeLabel = QLabel("Размер блока")
        self.stepSizeLabel = QLabel("Шаг поиска")
        self.windowSizeLabel = QLabel("Окно поиска")

        self.startBtn = QPushButton("Старт!")

        self.firstFrameBtn.clicked.connect(self.selectFile)
        self.secondFrameBtn.clicked.connect(self.selectFile)
        self.startBtn.clicked.connect(self.start)

        h1l = QHBoxLayout()
        h1l.addWidget(self.firstFrameLine)
        h1l.addWidget(self.firstFrameBtn)

        h2l = QHBoxLayout()
        h2l.addWidget(self.secondFrameLine)
        h2l.addWidget(self.secondFrameBtn)

        v1l = QVBoxLayout()
        v1l.addWidget(self.blockSizeLabel)
        v1l.addWidget(self.blockSize)

        v2l = QVBoxLayout()
        v2l.addWidget(self.stepSizeLabel)
        v2l.addWidget(self.stepSize)

        v3l = QVBoxLayout()
        v3l.addWidget(self.windowSizeLabel)
        v3l.addWidget(self.windowSize)

        h3l = QHBoxLayout()
        h3l.addLayout(v1l)
        h3l.addLayout(v2l)
        h3l.addLayout(v3l)

        layout.addLayout(h1l)
        layout.addLayout(h2l)
        layout.addLayout(h3l)
        layout.addWidget(self.startBtn)
        self.setLayout(layout)
        
        self.setGeometry(0, 0, 400, 100)
        window = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        window.moveCenter(centerPoint)
        self.move(window.topLeft())

        self.show()

    def selectFile(self):
        sender = self.sender()
        name = QFileDialog.getOpenFileName(self, 'Выберите {}'.format(sender.text()))[0]
        if sender.text() == '1 кадр':
            self.firstFrameLine.setText(name)
        else:
            self.secondFrameLine.setText(name)

    def start(self):
        self.startBtn.setEnabled(False)
        self.startBtn.setText("Пожалуйста, подождите пару минут...")
        
        sv = ShiftVector(
            [self.firstFrameLine.text(), self.secondFrameLine.text()],
            self.blockSize.text(),
            self.stepSize.text(),
            self.windowSize.text())
        sv.find_vectors()
        
        self.startBtn.setText("Старт!")
        self.startBtn.setEnabled(True)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())