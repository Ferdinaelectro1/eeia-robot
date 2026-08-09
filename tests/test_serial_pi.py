"""
Script de test cote Pi - envoie une trame de commande a l'ESP8266 et
affiche ce qu'il renvoie en retour (les print() du firmware).

A lancer demain, une fois l'ESP8266 branche en USB sur le Pi et
firmware/main.py deja copie dessus (via mpremote).

Usage:
    python scripts/test_serial_pi.py
"""

import serial
import time
from src.comm.protocol import encode_frame

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=2)
time.sleep(2)  # laisse le temps a l'ESP8266 de finir son boot avant d'envoyer

frame = encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
print("Envoi de la trame:", frame)
ser.write(frame)

# Lit tout ce que l'ESP8266 renvoie pendant les 3 prochaines secondes
# (ses print(), pas une vraie reponse structuree pour l'instant)
start = time.time()
while time.time() - start < 3:
    line = ser.readline()
    if line:
        print("Recu de l'ESP8266:", line.decode("utf-8", errors="replace").strip())

ser.close()
