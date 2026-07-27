import unittest
from henry8x.protocol import montar_pacote, extrair_payload
from henry8x.errors import HENRY_ERROS

def test_montar_e_extrair_payload_simple():
    cmd = "01+RH+00"
    pkt = montar_pacote(cmd)
    assert pkt[0] == 0x02
    assert pkt[-1] == 0x03
    payload = extrair_payload(pkt)
    assert payload == cmd

class TestHenryProtocol(unittest.TestCase):

    def test_montar_pacote_estrutura(self):
        cmd = "01+RH+00"
        pacote = montar_pacote(cmd)
        self.assertEqual(pacote[0], 0x02)
        self.assertEqual(pacote[-1], 0x03)
        self.assertEqual(pacote[3:-2].decode('latin-1'), cmd)

    def test_checksum_xor_calculo(self):
        cmd = "01+EU+00+1+L["
        pacote = montar_pacote(cmd)
        payload_bytes = cmd.encode('latin-1')
        tam = len(payload_bytes)
        b_lo = tam & 0xFF
        b_hi = (tam >> 8) & 0xFF
        chk_esperado = b_lo ^ b_hi
        for b in payload_bytes:
            chk_esperado ^= b
        self.assertEqual(pacote[-2], chk_esperado)

    def test_extrair_payload(self):
        pacote_valido = bytes([0x02, 0x08, 0x00]) + b"01+RH+00" + bytes([0x50, 0x03])
        payload = extrair_payload(pacote_valido)
        self.assertEqual(payload, "01+RH+00")

    def test_erros_dicionario(self):
        self.assertIn("000", HENRY_ERROS)
        self.assertIn("012", HENRY_ERROS)
        self.assertEqual(HENRY_ERROS["000"], "Sucesso Total - Operação executada")

if __name__ == '__main__':
    unittest.main()
