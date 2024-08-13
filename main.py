

import threading
import os.path

import pyftpdlib.authorizers
import pyftpdlib.servers
from pyftpdlib.handlers import FTPHandler

import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import ImageTk, Image
from pillow_heif import register_heif_opener

import configparser

register_heif_opener()

config = configparser.ConfigParser()

config.read('PhotoFtpServer.ini')

config_default = config['DEFAULT']
DEST_FOLDER = config_default.get('DESTINATION_FOLDER', '')
SERVER_ADDR = config_default.get('SERVER_ADDRESS','172.0.0.1')
SERVER_PORT = config_default.get('SERVER_PORT', '24621')

FTPSERVER_USER = config_default.get('FTPSERVER_USERNAME','ftpuser')
FTPSERVER_PASSWORD = config_default.get('FTPSERVER_PASSWORD','ftppass')

print (DEST_FOLDER)
print (SERVER_ADDR,SERVER_PORT)
print (FTPSERVER_USER, FTPSERVER_PASSWORD)

MAX_STATUS = 30

HEIGHT_MAINWIN = 590
WIDTH_MAINWIN = 740
MARGIN = 10
HIGHT_TEXTPANEL = 80


class MainGui :

    def __init__(self):
        self.rootWin = None
        self.canvas = None
        self.textPanel = None
        self.image = None
        self.imageTk = None
        self.imagePanelSize = (0, 0)
        self.height_mainwin = HEIGHT_MAINWIN
        self.width_mainwin = WIDTH_MAINWIN
        self.stateList = []
        self.reShow = None

    def init(self):
        self.rootWin = tk.Tk()
        self.rootWin.option_add('*font', ('FixedSys', 14))
        self.rootWin.title('Photo Ftp Server')
        self.rootWin.geometry("740x590")
        self.rootWin.resizable(1, 1)
        self.rootWin.minsize(300, 200)

        # image
        self.setImagePanelSize()
        self.canvas = tk.Canvas(self.rootWin, width = self.imagePanelSize[0], height = self.imagePanelSize[1])

        # Text
        self.textPanel = tkst.ScrolledText()

        self.place()

    def setImagePanelSize(self):
        self.imagePanelSize = (
            self.width_mainwin - MARGIN * 2,
            self.height_mainwin - HIGHT_TEXTPANEL - MARGIN * 3
        )

    def place(self):
        self.textPanel.place(height=HIGHT_TEXTPANEL, width=self.width_mainwin - MARGIN * 2, x=MARGIN, y=self.height_mainwin - HIGHT_TEXTPANEL - MARGIN)
        self.canvas.place(height=self.imagePanelSize[1], width=self.imagePanelSize[0], x=MARGIN, y=MARGIN)

    def start(self):
        self.addStatus("MainGui start.")
        self.rootWin.bind('<Configure>', handler_changeSize)
        self.rootWin.mainloop()

    def _renewStatus(self) :
        dispStr = ""
        for str in self.stateList:
            dispStr += str + "\n"
        self.textPanel.delete('1.0', 'end')
        self.textPanel.insert('end', dispStr)
        self.textPanel.see('end')
        self.rootWin.update_idletasks()

    def addStatus(self, str):
        self.stateList.append(str)
        if len(self.stateList) > MAX_STATUS :
            del self.stateList[0]
        self._renewStatus()

    def setImage(self, img):
        self.image = img
        self.showImage()

    def showImage(self, fast = False):
        imgSize = self.image.size
        resizeFactor = max(imgSize[0] / self.imagePanelSize[0], imgSize[1] / self.imagePanelSize[1])
        resampling = Image.Resampling.NEAREST if fast else Image.Resampling.BILINEAR
        img = self.image.resize((int(imgSize[0] / resizeFactor), int(imgSize[1] / resizeFactor)), resampling)
        # setImage
        self.imgTk = ImageTk.PhotoImage(img)
        self.canvas.create_image(MARGIN,MARGIN,anchor = tk.NW, image=self.imgTk)

    def resizeWindow(self):
        self.height_mainwin = self.rootWin.winfo_height()
        self.width_mainwin = self.rootWin.winfo_width()
        self.setImagePanelSize()
        self.canvas.configure(width=self.imagePanelSize[0], height=self.imagePanelSize[1])
        self.place()
        if self.image :
            if self.reShow :
                self.reShow.cancel()
            self.reShow = threading.Timer(1,self.showImage)
            self.reShow.start()
            self.showImage(fast=True)


class JtFtpHandler(FTPHandler):
    def on_connect(self) :
        print("connect")
        theMainGui.addStatus("Connect from FTP Client")

    def on_login(self, username):
        print("login User : " + username)
        theMainGui.addStatus("login User : " + username)

    def on_logout(self, username):
        print("Logout User : " + username)
        theMainGui.addStatus("Logout User : " + username)

    def on_disconnect(self):
        print("disconnect from Ftp Client")
        theMainGui.addStatus("disconnect from Ftp Client")

    def on_file_received(self, path):
        print("received file!",path)
        name = os.path.basename(path)
        theMainGui.addStatus("Received File " + name)

        showPhotoTh = threading.Timer(1, showPhoto, args=(path,))
        showPhotoTh.start()

        #super(Handler, self).ftp_RETR(file)

def showPhoto(path) :
    try :
        img = Image.open(path)
    except Exception as e:
        theMainGui.addStatus("Load error image file.")
        print(e)
        return

    theMainGui.setImage(img)

class FtpServer :
    server = None

    def __init__(self) :
        # 認証ユーザーを作る
        authorizer = pyftpdlib.authorizers.DummyAuthorizer()
        authorizer.add_user(FTPSERVER_USER, FTPSERVER_PASSWORD, DEST_FOLDER, perm='elradfmw')

        # 個々の接続を管理するハンドラーを作る
        handler = JtFtpHandler
        handler.authorizer = authorizer

        # FTPサーバーを立ち上げる
        self.server = pyftpdlib.servers.FTPServer((SERVER_ADDR, SERVER_PORT), handler)

    def startServer(self):
        self.server.serve_forever()


######
## instance

theFtpServer = FtpServer()
theMainGui = MainGui()

######
## Thread function

def thFtpServer() :
    theFtpServer.startServer()

def thGui() :
    theMainGui.init()
    theMainGui.start()

#######
## handler

def handler_changeSize(event):
    theMainGui.resizeWindow()

#######
## main routine

def main() :
    eventFtpStop = threading.Event()
    eventFtpStop.clear()

    ithFtpServer = threading.Thread(target=thFtpServer)
    ithFtpServer.start()

    thGui()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

