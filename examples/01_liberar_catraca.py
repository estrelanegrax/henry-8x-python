#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 1: Liberação Remota de Giro de Catraca / Relé de Porta
"""
from henry8x import HenryClient

# Instancia o cliente com IP da catraca/porta
client = HenryClient(ip="192.168.0.179", port=3000)

print("Enviando liberação remota para catraca...")
ok, resp = client.liberar_remoto(
    sentido="Entrada",           # 'Entrada', 'Saida' ou 'Porta'
    mensagem="Acesso Liberado",   # Linha 1 do display
    tempo_segundos=5              # Tempo de liberação
)

if ok:
    print("✔ Sucesso! Catraca liberada para giro.")
else:
    print(f"✘ Falha na liberação: {resp}")
