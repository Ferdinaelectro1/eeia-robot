"""
Tests unitaires du protocole - aucun materiel requis.
Lancer avec : python -m pytest tests/test_protocol.py -v
ou : python -m unittest tests/test_protocol.py
"""

import unittest
from src.comm.protocol import encode_frame, decode_frame


class TestProtocol(unittest.TestCase):

    def test_encode_produit_une_trame_terminee_par_newline(self):
        frame = encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
        self.assertTrue(frame.endswith(b"\n"))

    def test_roundtrip_encode_decode(self):
        frame = encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
        decoded = decode_frame(frame)
        self.assertEqual(decoded["cmd"], "drive")
        self.assertEqual(decoded["fl"], 120)
        self.assertEqual(decoded["fr"], 118)
        self.assertEqual(decoded["bl"], 115)
        self.assertEqual(decoded["br"], 122)
        self.assertEqual(decoded["servo"], 45)

    def test_checksum_invalide_leve_erreur(self):
        frame = encode_frame("drive", fl=120, fr=118, bl=115, br=122, servo=45)
        # On corrompt volontairement la trame (change une valeur sans recalculer le chk)
        corrupted = frame.replace(b'"fl":120', b'"fl":999', 1)
        with self.assertRaises(ValueError):
            decode_frame(corrupted)

    def test_trame_illisible_leve_erreur(self):
        with self.assertRaises(ValueError):
            decode_frame(b"ceci n'est pas du json\n")

    def test_trame_sans_checksum_leve_erreur(self):
        with self.assertRaises(ValueError):
            decode_frame(b'{"cmd":"drive","fl":120}\n')

    def test_commande_arret_urgence_simple(self):
        frame = encode_frame("stop")
        decoded = decode_frame(frame)
        self.assertEqual(decoded["cmd"], "stop")


if __name__ == "__main__":
    unittest.main()
