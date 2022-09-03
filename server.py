import socket
import asyncore
import select
import random
import pickle
import time

airplanemap = {}
BUFFERSIZE = 512
outgoing = []

class AirPlane():
    def __init__(self, x, y, width, height, velocity, angle, acceleration, playerid):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.angle = angle
        self.acceleration = acceleration
        self.turn = 1  # -1: left, 1: right
        self.bullets = []
        self.playerid = playerid

def updateWorld(message):
    arr = pickle.loads(message)

    playerid = arr[1]
    x = arr[2]
    y = arr[3]
    angle = arr[4]
    turn = arr[5]
    velocity = arr[6]
    acceleration = arr[7]
    bullets = arr[8]
    
    if playerid == 0: return

    airplanemap[playerid].x = x
    airplanemap[playerid].y = y
    airplanemap[playerid].angle = angle
    airplanemap[playerid].turn = turn
    airplanemap[playerid].velocity = velocity
    airplanemap[playerid].acceleration = acceleration
    airplanemap[playerid].bullets = bullets

    remove = []

    for i in outgoing:
        update = ['player locations']

        for key, value in airplanemap.items():
            update.append([value.playerid, value.x, value.y, value.angle, value.turn, value.velocity, value.acceleration, value.bullets])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        for i in remove:
            outgoing.remove(i)

class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    self.listen(10)
  def handle_accept(self):
    conn, addr = self.accept()
    print ('Connection address:' + addr[0] + " " + str(addr[1]))
    outgoing.append(conn)
    playerid = random.randint(1000, 1000000)
    playerminion = AirPlane(50, 50, 40, 40, 1,30,1,playerid) # acc = 1
    airplanemap[playerid] = playerminion
    conn.send(pickle.dumps(['id update', playerid]))
    SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
  def handle_read(self):
    recievedData = self.recv(BUFFERSIZE)
    if recievedData:
      updateWorld(recievedData)
    else: self.close()

MainServer(4126)
asyncore.loop()