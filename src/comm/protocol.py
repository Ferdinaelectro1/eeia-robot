"""
Protocole de communication Pi4 <-> ESP32 (robot de tri industriel, EEIA 2026)

Format de trame : JSON + '\\n' comme delimiteur de fin de trame
Un checksum simple (somme des bytes du payload, modulo 256) permet de
detecter une corruption sur le lien serie.

IMPORTANT : ce fichier existe en DEUX exemplaires strictement identiques :
- src/comm/protocol.py   (tourne sur le Pi, CPython)
- firmware/protocol.py   (tourne sur l'ESP32, MicroPython)
Toute modification du format de trame doit etre reportee dans les DEUX fichiers.
"""

import json


def _checksum(payload: dict) -> int:
    """Calcule un checksum simple sur la representation JSON du payload
    (sans le champ 'chk' lui-meme), somme des bytes modulo 256."""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sum(raw) % 256


def encode_frame(cmd: str, **fields) -> bytes:
    """Construit une trame prete a etre envoyee sur le lien serie.

    Exemple:
        encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
        -> b'{"bl":115,"br":122,"chk":231,"cmd":"drive","fl":120,"fr":118,"servo":45}\\n'
    """
    payload = {"cmd": cmd, **fields}
    payload["chk"] = _checksum(payload)
    line = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    return line.encode("utf-8")


def decode_frame(raw_line: bytes) -> dict:
    """Parse une ligne recue sur le lien serie et verifie son checksum.

    Leve ValueError si la trame est malformee ou si le checksum ne correspond pas.
    Retourne le dict decode (avec le champ 'chk' toujours present) si valide.
    """
    try:
        text = raw_line.decode("utf-8").strip()
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Trame illisible: {exc}") from exc

    if "chk" not in payload:
        raise ValueError("Trame sans champ 'chk'")

    received_chk = payload["chk"]
    payload_without_chk = {k: v for k, v in payload.items() if k != "chk"}
    expected_chk = _checksum(payload_without_chk)

    if received_chk != expected_chk:
        raise ValueError(
            f"Checksum invalide: recu={received_chk}, attendu={expected_chk}"
        )

    return payload
