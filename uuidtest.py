from mcuuid.api import GetPlayerData

player = GetPlayerData("489178c645bb4f3382f110f7f0d7381a")

print(player.username)
if player.valid is True:
    uuid = player.uuid
    print(player.username)
    
print ("Hello")
