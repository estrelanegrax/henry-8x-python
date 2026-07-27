import unittest
from henry8x.protocol import montar_pacote, extrair_payload
from henry8x.errors import HENRY_ERROS

class TestHenryProtocol(unittest.TestCase):

    def test_montar_pacote_estrutura(self):
        cmd = "01+RH+00"
        pacote = montar_pacote(cmd)
        
        # STX deve ser 0x02
        self.assertEqual(pacote[0], 0x02)
        # ETX deve ser 0x03 no último byte
        self.assertEqual(pacote[-1], 0x03)
        # Payload retido na posição correta
        self.assertEqual(pacote[3:-2].decode('latin-1'), cmd)

    def test_checksum_xor_calculo(self):
        cmd = "01+EU+00+1+L["
        pacote = montar_pacote(cmd)
        
        # Recalcula XOR localmente
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
