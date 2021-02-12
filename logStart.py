#!/usr/bin/python3

import sys, os, glob, nbt, time, fnmatch,  _thread
from mcuuid.api import GetPlayerData
from logger import Logger

serverPath = "C:\\Users\\Brett_2\\Desktop\\Server 2\\"
logPath = serverPath + "player-logs\\"
names = {}



# get the players names from the uuids
def pop_players():
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
            

#check if logger is already running
def loggerRunning():
    currtime = int(time.time())
    loggertime = int(os.path.getmtime(logPath + "timestamp"))
    if currtime - loggertime < 10:
        return 1
    else:
        return 0

#start the logger
def startLogger():
    if not os.path.exists(logPath):# make playerdata folder here. check if it was successfull
        try:
            os.mkdir(logPath)
        except OSError:
            print("Creation of the directory %s failed" % logPath)
    if  os.path.exists(logPath):
        logger = Logger(serverPath, names)
        logger.log()

if loggerRunning() == 1:
    print("logger already running")
else:
    pop_players()
    startLogger()
    print(" Logger Running")




