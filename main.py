import sys,time
from PyQt4 import QtGui, QtCore
import cv2
import numpy as np
import guiMainWindow
import Speed,NRec

class frmMainWindow(QtGui.QMainWindow, guiMainWindow.Ui_frmMainWindow):
    def __init__(self, opMode=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.currentFrame = np.array([])
        self.showFullScreen()
        #self.camPreview = CamDisplay(self)

        self.ReadPlate = False

        self.speed = Speed.Speed()
        self.speed.Measured.connect(self.SpeedUpdated)
        self.speed.start()

        self.btnOff.clicked.connect(self.close)
        self.btnRead.clicked.connect(self.ReadPlateClicked)

        self.capture = cv2.VideoCapture(0)
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            print('stating')

    def update_frame(self):
        ret, readFrame = self.capture.read()
        if ret:
            self.currentFrame = cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)
            height, width = self.currentFrame.shape[:2]
            image = QtGui.QImage(self.currentFrame, width, height, QtGui.QImage.Format_RGB888)
            if self.ReadPlate:
                self.ReadPlate = False
                plateRecodnition = NRec.NRec(image)
                plateRecodnition.Analyzed.connect(self.PlateAnalyzed)
                plateRecodnition.start()
            image = image.scaled(480, 340)
            self.lblImg.setPixmap(QtGui.QPixmap.fromImage(image))
            #self.camPreview.setImage(image)

    def SpeedUpdated(self,speed):
        self.lblSpeed.setText("{0:.2f}".format(speed) + " km/h")
        if speed >= self.numLimit.value():
            self.lblStatus.setText('Over Speed')
            self.ReadPlate = True

    def ReadPlateClicked(self):
        self.lblStatus.setText('Reading Plate')
        self.ReadPlate = True

    def PlateAnalyzed(self, state, number, confidance):
        if state:
            self.lblNumber.setText(number)
            self.lblAccurcy.setText(confidance)
            self.lblDetection.setText('Yes')
        else:
            self.lblNumber.setText('')
            self.lblAccurcy.setText('')
            self.lblDetection.setText('No')
        self.lblStatus.setText('Monitoring')


class CamDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CamDisplay, self).__init__(parent)
        self.image = None
        self.setGeometry(5, 5, 480, 340)

    def setImage(self, image):
        self.image = image
        self.image = self.image.scaled(480, 340)
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


def main():
    app = QtGui.QApplication(sys.argv)
    form = frmMainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
