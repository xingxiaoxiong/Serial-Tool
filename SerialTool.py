__author__ = 'Xiaoxiong XING'

from PySide.QtGui import *
from PySide.QtCore import *
import sys
import glob
import serial
import time

__appname__ = "Serial Tool"

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setWindowTitle(__appname__)

        self.isConnected = False

        self.worker = Worker()
        self.connect(self.worker, SIGNAL("updateText(QString)"), self.updateText, Qt.DirectConnection)

        self.serialList = QComboBox()
        self.serialList.addItem("Choose a serial port")
        self.serialList.addItems(serial_ports())

        self.serialButton = QPushButton("Connect")
        self.serialButton.clicked.connect(self.connectPort)
        #self.connect(self.serialButton, SIGNAL("clicked()"), self.connectPort)

        self.openFileButton = QPushButton("Send Message...")
        self.openFileButton.clicked.connect(self.openFile)
        #self.connect(self.openFileButton, SIGNAL("clicked()"), self.openFile)

        #self.sendButton = QPushButton("Send")
        #self.connect(self.sendButton, SIGNAL("clicked()"), self.sendMessage)

        self.receivedText = QTextBrowser()

        layout = QGridLayout()
        layout.addWidget(self.serialList, 0, 0)
        layout.addWidget(self.serialButton, 0, 1)
        layout.addWidget(self.openFileButton, 0, 2)
        #layout.addWidget(self.sendButton, 0, 3)
        layout.addWidget(self.receivedText, 1, 0)
        self.setLayout(layout)

    def openFile(self):
        dir = "."
        fileObj = QFileDialog.getOpenFileName(self, __appname__ + "Open File Dialog", dir=dir, filter="*.csv")
        fileName = fileObj[0]
        file = open(fileName, "r")
        content = file.read()
        file.close()
        if self.worker.isConnected:
            self.serialConnection.write(content)
        else:
            QMessageBox.warning(self, __appname__, "Please connect a serial port!")

    def updateText(self, text):
        self.receivedText.append(text)

    def sendMessage(self):
        pass

    def connectPort(self):
        if self.serialButton.text() == "Connect":
            if not self.serialList.currentText() == "Choose a serial port":
                self.serialConnection = serial.Serial(self.serialList.currentText(), 9600, timeout=0.5)
                self.worker.isConnected = True
                self.serialButton.setText("Disconnect")
                self.worker.serialConnection = self.serialConnection
                self.worker.start()
            else:
                QMessageBox.warning(self, __appname__, "Please select a serial port!")
        else:
            self.serialButton.setText("Connect")
            self.serialConnection.close()
            self.worker.isConnected = False

class Worker(QThread):
    def __init__(self,parent=None):
        super(Worker, self).__init__(parent)

        self.serialConnection = None
        self.isConnected = False

    def run(self):
        while self.isConnected:
            data = self.serialConnection.read(255)
            if data == '':
                continue
            else:
                self.emit(SIGNAL("updateText(QString)"), data)
        self.emit(SIGNAL("updateText(QString)"), "End of communication.")

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()