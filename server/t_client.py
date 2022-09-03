import pickle
import select
import socket

class Player:
    def __init__(self, _name, _x,_y,_vel,_angle,_bullets):
        self.name = _name
        self.x = _x
        self.y = _y
        self.vel = _vel
        self.angle = _angle
        self.bullets = _bullets

main_player = Player('arek', 0,0,0,0,0)

BUFFERSIZE = 2048

serverAddr = '127.0.0.1'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))

while True:  # aktualizuj ten caly kurwidole
    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins:
        gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
        if gameEvent[0] == 'id update':
            playerid = gameEvent[1]
            print(playerid)
        if gameEvent[0] == 'player locations':
            gameEvent.pop(0)
            players = []
            for player in gameEvent:
                if player[0] != playerid:
                    players.append(Player(player[0], player[1], player[2], player[3], player[4], player[5]))

    ge = ['position update', 'arek', main_player.x, main_player.y, main_player.vel, main_player.angle, main_player.bullets]
    s.send(pickle.dumps(ge)) 