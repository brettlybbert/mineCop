#!/usr/bin/env python3


import threading, locale, os, sys, nbt, time, copy

class Logger():
    def __init__(self, path,  names):
        self.path = path
        self.datapath = path + "world\\playerdata\\"
        self.logfilepath = path + "player-logs/"
        self.timestamps = {}
        self.items = {}
        self.names = names
        

    def log(self):
        
       threading.Timer(1, self.log).start() # run once a second
       self.touch(self.logfilepath + "timestamp") #set timestamp so we can tell the logger is running
       file = self.new_files() 
       if file == "None":
           return
       filename = self.datapath + file
       uuid = file[0:36]
       nbtfile = nbt.nbt.NBTFile(filename,'rb')
       #Get current time
       currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
       #Get the current position
       x = str(nbtfile["Pos"][0]).split('.',1)[0]
       y = str(nbtfile["Pos"][1]).split('.',1)[0]
       z = str(nbtfile["Pos"][2]).split('.',1)[0]
       pos = str(x) +","+ str(y) +","+ str(z)
       #Get user name
       if uuid in self.names:
           username = self.names[uuid]
       else:
           username = uuid
       #Get items
       tempitems = {}
       tempitems[uuid] = {}
       for line in nbtfile["Inventory"]:
           temp = str(line)
           temp1 = temp.replace('}',',')
           temp2 = temp1.split(':')
           item = temp2[3].split(',')[0]
           count = int(temp2[4].split(',')[0])
           if uuid not in tempitems:
               tempitems[uuid] = {}
           if item not in tempitems[uuid]:
               tempitems[uuid][item] = count # add count to the item key
               #print("#{} {} {} {} {}".format(currtime,username,pos,item,count))
           else:
               tempitems[uuid][item] = tempitems[uuid][item] + count # found an additional slot of an item
           #print("##{} {} {} {} {}".format(currtime,username,pos,item,count))
       if uuid not in self.items:
           self.items[uuid] = copy.deepcopy(tempitems[uuid]) #this is the first check. Just store the items.
       else:
           old_keys = set(self.items[uuid].keys())
           new_keys = set(tempitems[uuid].keys())
           added = new_keys - old_keys
           removed = old_keys - new_keys
           intersect_keys = new_keys.intersection(old_keys)
           logfile = self.logfilepath  + time.strftime("%Y-%m-%d", time.localtime()) + "_Player.log"
           f = open(logfile,"a")
           for k in added:
               print("{} {} {} {} {}".format(currtime,username,pos,k,tempitems[uuid][k]), file=f)
               print("{} {} {} {} {}".format(currtime,username,pos,k,tempitems[uuid][k]))
               self.items[uuid][k] = tempitems[uuid][k]
           for k in removed:
               print("{} {} {} {} {}".format(currtime,username,pos,k,self.items[uuid][k] * -1), file=f)
               print("{} {} {} {} {}".format(currtime,username,pos,k,self.items[uuid][k] * -1))
               self.items[uuid][k] = 0
           for k in intersect_keys:
               if tempitems[uuid][k] != self.items[uuid][k]:
                   difference = tempitems[uuid][k] - self.items[uuid][k]
                   print("{} {} {} {} {}".format(currtime,username,pos,k,difference), file=f)
                   print("{} {} {} {} {}".format(currtime,username,pos,k,difference))
           self.items[uuid] = copy.deepcopy(tempitems[uuid])
           f.close()

    def new_files(self):  # look for and return a file that has changed
        
        for root, dirs, files in os.walk(self.datapath):
            for file in files:
                if file.endswith(".dat") and len(file) == 40:
                    uuid = file[0:36]
                    #Get the time of each file and add to the dict
                    time = os.path.getmtime(self.datapath + file)
                    
                    if uuid in self.timestamps:  # check stored timestamps
                       if self.timestamps[uuid] != time:
                           self.timestamps[uuid] = time
                           return(file)
                    else:
                       self.timestamps[uuid] = time # timestamp not stored
                       return(file) 
        return("None")

    def touch(self,path):
        with open(path, 'a'):
            os.utime(path, None)
