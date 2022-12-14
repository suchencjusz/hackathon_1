"""
main server script for running agar.io server
can handle multiple/infinite connections on the same
local network
"""
import socket
from _thread import *
import pickle
import time
import random
import math
import os
from datetime import datetime
# from bot import Bot

# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
os.system("fuser 5555/tcp -k")
PORT = 5555

LAST_POWERUP_DROP = datetime.now()
W, H = 1600, 830

HOST_NAME = socket.gethostname()
SERVER_IP = "0.0.0.0"

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()  # listen for connections

print(f"[SERVER] Server Started with local ip {SERVER_IP}")

# dynamic variables
players = {}
balls = []
connections = 0
_id = 0
colors = [(255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128), (0, 0, 0)]
start = False
stat_time = 0
game_time = "Starting Soon"
nxt = 1


def get_start_location():
    """
    picks a start location for a player based on other player
    locations. It wiill ensure it does not spawn inside another player
    :param players: dict
    :return: tuple (x,y)
    """
    x = random.randrange(0, W)
    y = random.randrange(0, H)
    return (x, y)


def check_collision():
    global players
    for player in players:
        for player2 in players:
            if player != player2:
                if player != "powerups" and player2 != "powerups":
                    if(math.sqrt(math.pow(players[player]['x'] - players[player2]['x'], 2) + math.pow(players[player]['y'] - players[player2]['y'], 2))) < 50:
                        players[player]['health'] -= 100
                        players[player2]['health'] -= 100

                        if players[player]['health'] <= 0:
                            print("player died")
                            players[player2]['score'] += 1
                            players[player]['health'] = 1000
                            players[player]['x'], players[player2]['y'] = get_start_location(
                            )

                        if players[player2]['health'] <= 0:
                            print("player2 died")
                            players[player2]['health'] = 1000
                            players[player2]['x'], players[player2]['y'] = get_start_location(
                            )
                            players[player]['score'] += 1

            if player != "powerups" and player2 != "powerups":
                for bullet in players[player]['bullets']:
                    if player != player2:
                        if math.sqrt(math.pow(bullet['x'] - players[player2]['x'], 2) + math.pow(bullet['y'] - players[player2]['y'], 2)) < 50:
                            print("[COLLISION]", players[player]['name'],
                                  "hit", players[player2]['name'])
                            players[player2]['health'] -= 25
                            if players[player2]['health'] <= 0:
                                players[player]['score'] += 1
                                players[player2]['health'] = 1000
                                players[player2]['x'], players[player2]['y'] = get_start_location(
                                )
                            break


def threaded_client(conn, _id):
    """
    runs in a new thread for each player connected to the server
    :param con: ip address of connection
    :param _id: int
    :return: None
    """
    global connections, players, game_time, LAST_POWERUP_DROP

    current_id = _id

    # recieve a name from the client
    data = conn.recv(128)
    name = data.decode("utf-8")
    print("[LOG]", name, "connected to the server.")

    # Setup properties for each new player
    color = colors[current_id]
    x, y = get_start_location()
    angle = random.randint(0, 360)
    players[current_id] = {"x": x, "y": y, "color": color, "score": 0,
                           "name": name, "angle": angle, "id": current_id}  # x, y color, score, name

    # pickle data and send initial info to clients
    conn.send(pickle.dumps((players[current_id])))

    # server will recieve basic commands from client
    # it will send back all of the other clients info
    '''
	commands start with:
	move
	get
	id - returns id of client
	'''
    # send_data = str.encode("1")
    while True:
        # if (datetime.now() - LAST_POWERUP_DROP) > timedelta(seconds=3):
        #     players['powerups'] = powerups()

        #     LAST_POWERUP_DROP = datetime.now()

        data = conn.recv(1024)
        data = data.decode("utf-8")

        # look for specific commands from recieved data
        if data.split(" ")[0] == "move":
            split_data = data.split(" ")
            players[current_id]['bullets'] = []
            x = float(split_data[1])
            y = float(split_data[2])
            angle = float(split_data[3])
            health = float(split_data[4])
            class_name = split_data[5]
            try:
                bullets_data = split_data[6:]
                players[current_id]['bullets'] = []
                dct = {}
                for bullet in bullets_data:
                    temp = bullet.split(",")
                    x_b = float(temp[0])
                    y_b = float(temp[1])
                    angle_b = float(temp[2])
                    dct = {"x": x_b, "y": y_b, "angle": angle_b}
                    players[current_id]["bullets"].append(dct)
            except Exception as e:
                pass

            players[current_id]["angle"] = angle
            players[current_id]["x"] = x
            players[current_id]["y"] = y
            players[current_id]["health"] = health
            players[current_id]["class"] = class_name

            check_collision()

            send_data = pickle.dumps((players))

        elif data.split(" ")[0] == "id":
            send_data = str.encode(str(current_id))
        else:

            print("[DISCONNECT] Name:", name,
                  ", Client Id:", current_id, "disconnected")

            connections -= 1
            # remove client information from players list
            del players[current_id]
            conn.close()  # close connection

            # send data back to clients
        try:
            conn.send(send_data)
        except Exception as e:
            print("[DISCONNECT] Name:", name,
                  ", Client Id:", current_id, "disconnected")

            connections -= 1
            del players[current_id]
            conn.close()  # close connection
        time.sleep(1/30)


# MAINLOOP
print("[GAME] Setting up level")
print("[SERVER] Waiting for connections")

# start_new_thread(threaded_bot, (0,))
# _id += 1

# Keep looping to accept new connections
while True:

    host, addr = S.accept()
    print("[CONNECTION] Connected to:", addr)

    # start game when a client on the server computer connects
    if addr[0] == SERVER_IP and not(start):
        start = True
        start_time = time.time()
        print("[STARTED] Game Started")

    # increment connections start new thread then increment ids
    connections += 1
    start_new_thread(threaded_client, (host, _id))
    _id += 1
