print("TKV/2 V1.1\nCreated By Alex Hall\n")
import sys
assert sys.version_info >= (3, 6), "please use python version 3.6 or higher"
import os, json, time, random

def tprint(a):
  for i in a:
    sys.stdout.write(i)
    sys.stdout.flush()
    time.sleep(.004)

def findinmap(x1,y1): 
  out = ""
  for y in range(len(mapdata["main"])):
    for x in range(len(mapdata["main"][y])):
      if y == y1 and x == x1:
        out += ("\033[31m"+str(mapdata["main"][y][x])+"\033[0m")
      else:
        out += (str(mapdata["main"][y][x]))
    out += ("\n")
  return out

def canmove(curmap, loc):
  try:
    if curmap[loc[1]][loc[0]] != 1:
      return True
    else:
      return False
  except IndexError:
    return False


# loads story
with open("data/story.json", "r") as txt:
  story = json.loads(txt.read())
# loads commands decoding pack
with open("data/commands.json", "r") as txt:
  commands = json.loads(txt.read())

if input("would you like the intro? ") in commands["logic"]["yes"]:
  for i in story["start"]:
    tprint(i)
    input()

inventory = {"fist":{"inf":"your bare hands","mndmg":1,"mxdmg":2,"hp":-1}}
health = 10
playerLOC = [13,8]

if input("load save? ") in commands["logic"]["yes"]:
  try:
    with open(input("savename: ")+".TKV","r") as txt:
      dic = json.loads(txt.read())
    mapdata = dic["mapdata"]
    locDATA = dic["locDATA"]
    health = dic["player"]["hp"]
    inventory = dic["player"]["inv"]
    playerLOC = tuple(dic["player"]["loc"])
  except FileNotFoundError:
    print("file not found")
    input()
    os._exit(4)
else:
  # loads maps
  with open("data/mapdata.json", "r") as txt:
    mapdata = json.loads(txt.read())
  with open("data/LOI.json", "r") as txt:
    locDATA = json.loads(txt.read())



def movenpc(chrLOC):
  d = random.randint(0,3)
  if d == 0 and canmove(mapdata["main"], (chrLOC[0], chrLOC[1]-1) ):
    chrLOC = [chrLOC[0], chrLOC[1]-1]
  elif d == 1 and canmove(mapdata["main"], (chrLOC[0]+1, chrLOC[1]) ):
    chrLOC = [chrLOC[0]+1, chrLOC[1]]
  elif d == 2 and canmove(mapdata["main"], (chrLOC[0], chrLOC[1]+1) ):
    chrLOC = [chrLOC[0], chrLOC[1]+1]
  elif d == 3 and canmove(mapdata["main"], (chrLOC[0]-1, chrLOC[1]) ):
    chrLOC = [chrLOC[0]-1, chrLOC[1]]
  return chrLOC

def gametick():
  # move per npc
  for i in locDATA["npc"]:
    if random.randint(0,5) == 1 and locDATA["npc"][i]["hp"] > 0:
      locDATA["npc"][i]["loc"] = movenpc(locDATA["npc"][i]["loc"])
    if tuple(locDATA["npc"][i]["loc"]) != playerLOC and random.randint(0,3) == 1 and locDATA["npc"][i]["agro"] > 0:
      locDATA["npc"][i]["agro"] = locDATA["npc"][i]["agro"] - 1

# commands for parsecmd
def moveMC(cmd):
  global playerLOC
  if len(cmd) >= 2:
    if cmd[1] in commands["move"]["north"] and canmove(mapdata["main"], (playerLOC[0],playerLOC[1]-1)):
      playerLOC = (playerLOC[0],playerLOC[1]-1)
    elif cmd[1] in commands["move"]["south"] and canmove(mapdata["main"], (playerLOC[0],playerLOC[1]+1)):
      playerLOC = (playerLOC[0],playerLOC[1]+1)
    elif cmd[1] in commands["move"]["east"] and canmove(mapdata["main"], (playerLOC[0]+1,playerLOC[1])):
      playerLOC = (playerLOC[0]+1,playerLOC[1])
    elif cmd[1] in commands["move"]["west"] and canmove(mapdata["main"], (playerLOC[0]-1,playerLOC[1])):
      playerLOC = (playerLOC[0]-1,playerLOC[1])
    mapdata["discovery"][playerLOC[1]+1][playerLOC[0]] = 1
    mapdata["discovery"][playerLOC[1]-1][playerLOC[0]] = 1
    mapdata["discovery"][playerLOC[1]][playerLOC[0]+1] = 1
    mapdata["discovery"][playerLOC[1]][playerLOC[0]-1] = 1
    mapdata["discovery"][playerLOC[1]][playerLOC[0]] = 1

def grabitem(cmd):
  if mapdata["main"][playerLOC[1]][playerLOC[0]] == 3:
    item = locDATA["locations"]["[%s,%s]"%playerLOC]
    if len(cmd) >= 2 and item == cmd[1]:
      if item in inventory.keys():
        inventory[item]["hp"] = inventory[item]["hp"] + locDATA["items"][item]["hp"]
        tprint("multiple of same item, adding durabilites together\n")
      else:
        inventory[item] = dict(locDATA["items"][item])
        tprint("colleted %s\n"%item)
      mapdata["main"][playerLOC[1]][playerLOC[0]] = 0
    else:
      tprint("there is no item of that name here\n")
  else:
    tprint("there is no item here\n")

def hitNPC(cmd):
  if len(cmd) >= 3:
    if cmd[1] in locDATA["npc"].keys() and cmd[2] in inventory.keys():
      wep = cmd[2]
      stat = inventory[cmd[2]]
      hit = True
      violence = random.randint(stat["mndmg"],stat["mxdmg"])
      if cmd[1] in locDATA["npc"].keys() and playerLOC == tuple(locDATA["npc"][cmd[1]]["loc"]):
        locDATA["npc"][cmd[1]]["hp"] = locDATA["npc"][cmd[1]]["hp"] - violence
        locDATA["npc"][cmd[1]]["agro"] = locDATA["npc"][cmd[1]]["agro"] + 1 
        tprint("hit %s for %s damage\n"%(cmd[1], violence))
        if locDATA["npc"][cmd[1]]["hp"] <= 0:
          locDATA["npc"][cmd[1]]["loc"] = []
          tprint("%s is dead\n"%cmd[1])
      else:
        tprint("enemy not in range\n")
        hit = False
      if hit:
        stat["hp"] = stat["hp"]-1
        inventory[wep] = stat
        if stat["hp"] == 0:
          del inventory[wep]
          tprint("%s broke\n"%wep)
    else:
      tprint("enemy does not exist/ item not in inventory\n")
  else:
    tprint("not enough arguments (your \033[34mfist\033[0m is a weapon)\n")

def printmap(a):
  for y in range(len(mapdata["main"])):
    for x in range(len(mapdata["main"][y])):
      if mapdata["discovery"][y][x] == 1:
        if playerLOC == (x,y):
          sys.stdout.write("\033[47m  \033[0m")
        elif mapdata["main"][y][x] == 2:
          sys.stdout.write("\033[45m  \033[0m")
        elif mapdata["main"][y][x] == 1:
          sys.stdout.write("\033[41m  \033[0m")
        else:
          sys.stdout.write("\033[43m  \033[0m")
      else:
        sys.stdout.write("\033[40m  \033[0m")
    sys.stdout.write("\n")
  sys.stdout.flush()

def stat(a):
  tprint("health: %s\n"%health)
  tprint("inv: \n")
  for i in inventory:
    if i != "fist":
      inf = "  %s\n    desc: %s\n    dmg range: %s\n    hp: %s\n"
      tprint(inf%(i, inventory[i]["inf"], "%s-%s"%(inventory[i]["mndmg"],inventory[i]["mxdmg"]), inventory[i]["hp"]))

def savestate(cmd):
  if len(cmd) > 1:
    filename = cmd[1]+".TKV"
  else:
    filename = "auto.TKV"
  savedat = {}
  savedat["mapdata"] = dict(mapdata)
  savedat["locDATA"] = dict(locDATA)
  savedat["player"] = {"hp":health, "inv":inventory, "loc":playerLOC}
  with open(filename,"w+") as txt:
    txt.write(json.dumps(savedat))
  tprint("saved as %s\n" %filename.replace(".TKV",""))

def parsecmd(cmd):
  if cmd[0] in commands["commands"].keys():
    exec(commands["commands"][cmd[0]].format(cmd))

def playermoves():
  retur = []
  if canmove(mapdata["main"], (playerLOC[0],playerLOC[1]-1)):
    retur.append("north")
  if canmove(mapdata["main"], (playerLOC[0],playerLOC[1]+1)):
    retur.append("south")
  if canmove(mapdata["main"], (playerLOC[0]+1,playerLOC[1])):
    retur.append("east")
  if canmove(mapdata["main"], (playerLOC[0]-1,playerLOC[1])):
    retur.append("west")
  if len(retur) > 1:
    fin = "you can move "
    for i in range(len(retur)):
      if i+1 == len(retur):
        fin += "and "+retur[i]
      else:
        fin+= retur[i]+", "
    return fin
  else:
    return "you can move "+retur[0]
  return retur

def nearbyLOI():
  retur = ""
  if mapdata["main"][playerLOC[1]-1][playerLOC[0]] == 2:
    retur += "north you can see a %s, "%locDATA["locations"]["[%s,%s]"%(playerLOC[0],playerLOC[1]-1)]
  if mapdata["main"][playerLOC[1]+1][playerLOC[0]] == 2:
    retur += "south you can see a %s, "%locDATA["locations"]["[%s,%s]"%(playerLOC[0],playerLOC[1]+1)]
  if mapdata["main"][playerLOC[1]][playerLOC[0]-1] == 2:
    retur += "west you can see a %s, "%locDATA["locations"]["[%s,%s]"%(playerLOC[0]-1,playerLOC[1])]
  if mapdata["main"][playerLOC[1]][playerLOC[0]+1] == 2:
    retur += "east you can see a %s, "%locDATA["locations"]["[%s,%s]"%(playerLOC[0]+1,playerLOC[1])]
  return retur
  
#mainloop
while True:
  gametick()
  info = ""
  if mapdata["main"][playerLOC[1]][playerLOC[0]] == 2: # if in LOI
    info += "you are in a "+locDATA["locations"]["[%s,%s]"%playerLOC]+", "
  if playerLOC in [tuple(locDATA["npc"][i]["loc"]) for i in locDATA["npc"]]:
    for i in locDATA["npc"]:
      d = locDATA["npc"][i]
      if tuple(d["loc"]) == playerLOC:
        info += "there is a %s here, "%i
        if d["agro"] >= 1:
          violence = random.randint(d["damage"][0],d["damage"][1])
          health -= violence
          info += "the %s hit your for %s damage, "%(i,violence)
  if mapdata["main"][playerLOC[1]][playerLOC[0]] == 3: # if on itemmap
    info += "there is a "+locDATA["locations"]["[%s,%s]"%playerLOC]+" here, "
  info += nearbyLOI()
  info += playermoves()
  tprint(info+"\n")
  if health <= 0:
    tprint("\n--------\nyou died\n")
    input()
    break
  command = input("> ").split(" ")
  if command[0] == "exit":
    tprint("bye bye\n")
    input()
    break
  if command == ["_dbug"]:
    try:
      exec("print(%s)"%input("$ "))
    except:
      pass
  parsecmd(command)
