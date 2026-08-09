"""
Firmware ESP8266 - Boucle principale de reception des commandes du Pi.

IMPORTANT : l'ESP8266 n'a qu'un seul UART materiel (UART0), partage entre
le REPL/Thonny/mpremote ET la communication reelle avec le Pi. Une fois ce
script lance comme boucle de production, il occupe ce canal pour parler au
Pi -- tu ne pourras plus utiliser Thonny/mpremote sur ce meme port pendant
que la boucle tourne. C'est normal et attendu : demain, le Pi remplacera
Thonny comme "interlocuteur" sur ce port.
"""

from machine import UART
import protocol

# UART(0) = le port physique relie au cable USB (le meme que Thonny utilise)
uart = UART(0, baudrate=115200)

print("Firmware pret, en attente de trames du Pi...")

while True:
    if uart.any():
        raw_line = uart.readline()
        if raw_line:
            try:
                frame = protocol.decode_frame(raw_line)
                print("Trame recue:", frame)

                # TODO demain : ici, piloter les moteurs/servos selon frame["cmd"]
                # Exemple a venir :
                # if frame["cmd"] == "drive":
                #     set_wheel_speeds(frame["fl"], frame["fr"], frame["bl"], frame["br"])
                #     set_servo_angle(frame["servo"])

            except ValueError as e:
                print("Trame invalide ignoree:", e)
