#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 3: Servidor TCP Online em Tempo Real (Eventos de Cartão e Confirmação de Giro)
"""
from henry8x import HenryServerDaemon

# Instancia o Servidor Daemon
daemon = HenryServerDaemon(host="0.0.0.0", port=3000)

# Registra os equipamentos cadastrados
daemon.adicionar_equipamento(ip="192.168.0.179", port=3000, eh_catraca=True)

print("Iniciando Servidor TCP Online em tempo real na porta 3000...")
print("Pressione Ctrl+C para encerrar.")

try:
    daemon.iniciar()
except KeyboardInterrupt:
    print("Servidor encerrado.")
