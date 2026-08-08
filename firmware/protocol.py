"""
Protocole de communication Pi4 <-> ESP8266 (robot de tri industriel, EEIA 2026)

Format de trame : JSON + '\\n' comme delimiteur de fin de trame
Un checksum simple (somme des bytes du payload, modulo 256) permet de
detecter une corruption sur le lien serie.

IMPORTANT sur l'ordre des cles :
ujson (MicroPython/ESP8266) NE SUPPORTE PAS sort_keys, contrairement a json
(CPython/Pi). On ne trie donc JAMAIS les cles explicitement -- on s'appuie
sur le fait que les dictionnaires Python (CPython et MicroPython recents)
preservent l'ordre d'INSERTION. Tant que les deux cotes construisent le
payload dans le meme ordre (cmd, puis les champs dans l'ordre donne, puis
chk en dernier), le JSON genere sera identique des deux cotes.
NE PAS ajouter sort_keys=True ici : ca casserait la compatibilite ESP8266.

IMPORTANT : ce fichier existe en DEUX exemplaires strictement identiques :
- src/comm/protocol.py   (tourne sur le Pi, CPython, module 'json')
- firmware/protocol.py   (tourne sur l'ESP8266, MicroPython, module 'ujson' -
  importe ici sous le nom 'json' pour garder un code identique des deux cotes)
Toute modification du format de trame doit etre reportee dans les DEUX fichiers.
"""

import json


def _checksum(payload: dict) -> int:
    """Calcule un checksum simple sur la representation JSON du payload
    (sans le champ 'chk' lui-meme), somme des bytes modulo 256."""
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return sum(raw) % 256


def encode_frame(cmd: str, **fields) -> bytes:
    """Construit une trame prete a etre envoyee sur le lien serie.

    L'ordre d'insertion (cmd, puis les fields dans l'ordre donne, puis chk)
    doit rester identique a chaque appel pour que le checksum soit coherent.

    Exemple:
        encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
        -> b'{"cmd":"drive","fl":120,"fr":118,"bl":115,"br":122,"servo":45,"chk":231}\\n'
    """
    payload = {"cmd": cmd}
    payload.update(fields)
    payload["chk"] = _checksum(payload)
    line = json.dumps(payload, separators=(",", ":")) + "\n"
    return line.encode("utf-8")


def decode_frame(raw_line: bytes) -> dict:
    """Parse une ligne recue sur le lien serie et verifie son checksum.

    Leve ValueError si la trame est malformee ou si le checksum ne correspond pas.
    Retourne le dict decode (avec le champ 'chk' toujours present) si valide.
    """
    try:
        text = raw_line.decode("utf-8").strip()
        payload = json.loads(text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("Trame illisible: " + str(exc))

    if "chk" not in payload:
        raise ValueError("Trame sans champ 'chk'")

    received_chk = payload["chk"]
    payload_without_chk = {}
    for k, v in payload.items():
        if k != "chk":
            payload_without_chk[k] = v
    expected_chk = _checksum(payload_without_chk)

    if received_chk != expected_chk:
        raise ValueError(
            "Checksum invalide: recu=" + str(received_chk) + ", attendu=" + str(expected_chk)
        )

    return payload
