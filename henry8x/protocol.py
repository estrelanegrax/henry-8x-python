import socket

def montar_pacote(cmd_txt: str) -> bytes:
    payload = cmd_txt.encode('latin-1')
    tam = len(payload)
    b_lo = tam & 0xFF
    b_hi = (tam >> 8) & 0xFF
    chk = b_lo ^ b_hi
    for b in payload:
        chk ^= b
    return bytes([0x02, b_lo, b_hi]) + payload + bytes([chk, 0x03])

def extrair_payload(raw: bytes) -> str:
    if len(raw) >= 5:
        return raw[3:-2].decode('latin-1', 'ignore')
    return raw.decode('latin-1', 'ignore')
