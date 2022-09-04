# requirements
```
  python 3.6+
  pygame 4.8+
```
# Play locally
Playing locally mean you need to host server on your local IP

Windows
------
```
pip install -r requirements.txt
python local_server.py
```

```
python local_game.py
```

Linux
-----
```
pip install -r requirements.txt
python3 local_server.py
```

```
python3 local_game.py
```

# Play online
You will be able to play online only if server is up

Windows
------
```
pip install -r requirements.txt
python game.py
```

Linux
-----
```
pip install -r requirements.txt
python3 game.py
```

# Controls
* **W** : increase velocity
* **S** : decrease velocity
* **A** : turn left
* **D** : turn right
* **SPACE** : fire

# Classes
* Kamikaze
_health: 280, maximum velocity: 18 (can't fire, only way to kill is to flight into another player)_

* Scout
_health: 70, maximum velocity 24, ammo: 8, reload time: 0.3s_

* Heavy
_health:200, maximum velocity: 12, ammo:15, reload time: 2s_

* Fighter
_health: 100, maximum velocity: 15, ammo: 10, reload time: 1s_
