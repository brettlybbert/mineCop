#!/usr/bin/python3

import sys, os, glob, nbt, time, fnmatch,  _thread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QLineEdit, QInputDialog, QMessageBox
from Ui_minecop import Ui_MainWindow
from mcuuid.api import GetPlayerData
from logger import Logger

serverPath = "C:\\Users\\Brett_2\\Desktop\\Server 2\\"
logPath = serverPath + "player-logs\\"
text = ""


names = {}


places = {"Snowlight house":"-577,64,-68,50",
               " ":" "}


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, win):
        QMainWindow.__init__(self)
        self.setupUi(win)
        self.refreshButton.clicked.connect(self.refresh)
        self.serverButt.clicked.connect(self.getServer)
        self.pop_logs()
        _thread.start_new_thread(self.pop_players,() )
        self.load_boxes()
        self.filterBox.textChanged.connect(self.update_log)
        self.locBox.textChanged.connect(self.update_log)
        self.serverNameLabel.setText(serverPath)
        self.logButt.clicked.connect(self.startLogger)
        self.logButt.setEnabled(False)

    def load_boxes(self):
        self.locComboBox.addItems(sorted(list(places)))
        self.locComboBox.activated[str].connect(self.set_loc)

    def set_loc(self,loc):
        self.locBox.setText(places[loc])

    def pop_logs(self):
        self.fileList.clear()
        path = logPath
        os.chdir(path)
        self.fileList.addItems(sorted([x for x in glob.glob("*log") if not x.endswith('~')]))
        self.fileList.itemClicked.connect(self.update_log)

    def update_log(self):
        self.textEdit.clear()
        text=""
        for logfile in sorted(self.fileList.selectedItems()):
            filename = logPath + logfile.text()
            with open(filename, 'r') as myfile:
                text+=myfile.read()
        self.filter(text)

    def pop_players(self):
        self.playerList.clear()
        path = serverPath + "world\\playerdata\\"
        username = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".dat") and len(file) == 40:
                    uuid = file[0:36]
                    uuid_short = uuid.replace('-','')
                    if uuid in names:
                        username.append(names[uuid])
                    else: 
                        Player = GetPlayerData(uuid_short)
                        if Player.valid is True:
                           name = Player.username
                           username.append(name)
                           names[uuid] = name
                        else:
                            username.append(uuid)
                

        self.playerList.addItems(username)
        self.playerList.itemClicked.connect(self.update_player)
        if self.loggerRunning() == 1:
            self.logButt.setEnabled(False)
            self.logButt.setText("Running")
        else:
            self.logButt.setEnabled(True)

    def update_player(self):
        self.textEdit.clear()
        for player in self.playerList.selectedItems():
            playername = player.text()
            if len(playername) == 36:
                uuid = playername
            else:
                for uid, name in names.items():
                    if name == playername:
                        uuid = uid 
        datfile = serverPath + "world\\playerdata\\" + uuid + ".dat"
        modtime = str(time.ctime(os.path.getmtime(datfile)))
        nbtfile = nbt.nbt.NBTFile(datfile,'rb')
        x = str(nbtfile["Pos"][0]).split('.',1)[0]
        y = str(nbtfile["Pos"][1]).split('.',1)[0]
        z = str(nbtfile["Pos"][2]).split('.',1)[0]
        pos = str(x) +","+ str(y) +","+ str(z)
        text = playername + "  " + uuid + "\n" + modtime + "\n" + pos + "\n"
        for line in nbtfile["Inventory"]:
           temp = str(line)
           temp1 = temp.replace('}',',')
           temp2 = temp1.split(':')
           item = temp2[3].split(',')[0]
           count = temp2[4].split(',')[0]
           text += item + " " + count + "\n"
        self.textEdit.setText(text)

    def refresh(self):
        self.pop_logs()
        _thread.start_new_thread(self.pop_players,() )

    def getServer(self):
        serverPath = QFileDialog.getExistingDirectory(self, 'Select Server Folder', os.sep.join((os.path.expanduser('~'), 'Desktop'))  )
        self.serverNameLabel.setText(serverPath)

    def filter(self,text):
        lines = text.split("\n")
        lines = fnmatch.filter(lines,'*' + self.filterBox.text() + '*')
        if len(self.locBox.text().split(',')) == 4 and len(lines) > 0:
            flines = []
            sx =int(self.locBox.text().split(',')[0])
            sy =int(self.locBox.text().split(',')[1])
            sz =int(self.locBox.text().split(',')[2])
            sr =int(self.locBox.text().split(',')[3])
            for l in lines:
                if len(l) < 10:
                    break
                dx = int(l.split(' ')[3].split(',')[0])
                dy = int(l.split(' ')[3].split(',')[1])
                dz = int(l.split(' ')[3].split(',')[2])
                if dx > sx - sr and dx < sx + sr and dy > sy - sr and dy < sy + sr and dz > sz - sr and dz < sz + sr:
                    flines.append(l)
            self.textEdit.setText('\n'.join(flines))
        else:
            self.textEdit.setText('\n'.join(lines))

    def loggerRunning(self):
        currtime = int(time.time())
        loggertime = int(os.path.getmtime(logPath + "timestamp"))
        if currtime - loggertime < 10:
            return 1
        else:
            return 0

    def startLogger(self):
        if not os.path.exists(logPath):# make playerdata folder here. check if it was successfull
            try:
                os.mkdir(logPath)
            except OSError:
                print("Creation of the directory %s failed" % logPath)
        if  os.path.exists(logPath):
            logger = Logger(serverPath, names)
            logger.log()
            self.logButt.setEnabled(False)
            self.logButt.setText("Running")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QMainWindow()
    prog = MainWindow(win)
    win.show()
    sys.exit(app.exec_())


