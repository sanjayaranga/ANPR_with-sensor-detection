import sys,time
from PyQt4 import QtCore
from openalpr import Alpr

class NRec(QtCore.QThread):
    Analyzed = QtCore.pyqtSignal(bool, str, str)

    def __init__(self,image):
        QtCore.QThread.__init__(self)
        self.image = image

    def run(self):
        #saves the image

        fname = '/home/pi/VNPRS-Cap/' + time.strftime("%m-%d-%H-%M-%S", time.localtime()) + '.jpg'
        self.image.save(fname, 'JPG', 100)
        print('file saved')

        alpr = Alpr("eu","/etc/openalpr/openalpr.conf","/usr/local/share/openalpr/runtime_data/")
        if not alpr.is_loaded():
            print("Error loading OpenALPR")
            self.Analyzed.emit(False, '', '')
            sys.exit(1)

        #alpr.set_top_n(20)
        #alpr.set_default_region("md")

        found = False
        results = alpr.recognize_file(fname)
        try:
            for plate in results['results']:
                for candidate in plate['candidates']:
                    #print(str(candidate['plate']) + "  Confi" + str(candidate['confidence']))
                    self.Analyzed.emit(True,str(candidate['plate']),"{0:.2f}".format(candidate['confidence'])+' %')
                    found = True
                    break
                break

            if not found:
                self.Analyzed.emit(False, '', '')

        except Exception as ex:
            self.Analyzed.emit(False, '', '')

        alpr.unload()
