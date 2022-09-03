import socket
import asyncore
import select
import random
import pickle
import time

BUFFERSIZE = 512

outgoing = []


class Player:
    def __init__(self, _name, _x, _y, _vel, _angle, _bullets):
        self.name = _name
        self.x = _x
        self.y = _y
        self.vel = _vel
        self.angle = _angle
        self.bullets = _bullets


players = {}


def updateWorld(message):
    arr = pickle.loads(message)
    print(str(arr))
    plr_name = arr[1]
    x = arr[2]
    y = arr[3]
    vel = arr[4]
    angle = arr[5]
    bullets = arr[6]

    players[plr_name].x = x
    players[plr_name].y = y
    players[plr_name].vel = vel
    players[plr_name].angle = angle
    players[plr_name].bullets = bullets

    # ge = ['position update', 'arek', main_player.x, main_player.y, main_player.vel, main_player.angle, main_player.bullets]

    remove = []

    for i in outgoing:
        update = ['player locations']

        for key, value in players.items():
          update.append([value.ownerid, value.x, value.y])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        print('sent update data')

        for r in remove:
            outgoing.remove(r)


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        outgoing.append(conn)
        playerid = random.randint(1000, 1000000)
        playerminion = Minion(playerid)
        minionmap[playerid] = playerminion
        conn.send(pickle.dumps(['id update', playerid]))
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        recievedData = self.recv(BUFFERSIZE)
        if recievedData:
            updateWorld(recievedData)
        else:
            self.close()


MainServer(4321)
asyncore.loop()
