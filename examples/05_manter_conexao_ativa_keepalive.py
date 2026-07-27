#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 5: Conexão Persistente em Modo Servidor e KeepAlive Oficial da Henry (01+RH+00)
Método eficiente desenvolvido por estrelaex para evitar quedas no Modo Servidor.

COMO FUNCIONA O MÉTODO RECOMENDADO DE KEEPALIVE:
  1. O Python abre o socket TCP com o equipamento (ex: 192.168.0.179:3000).
  2. O socket escuta em loop continuo com timeout de leitura (1.0s).
  3. Toda vez que qualquer dado chega da catraca (bip, giro ou resposta RH), o timer de atividade é resetado.
  4. Se passarem mais de 30 segundos sem NENHUM tráfego, o Python envia o comando '01+RH+00' (Pedir Data/Hora).
  5. A resposta do '01+RH+00' chega no recv, confirmando que a catraca está viva e resetando o timer.
  6. Se o socket fechar ou cair, o sistema marca como OFFLINE e tenta reconectar em loop a cada 15s.
"""

import socket
import time
from henry8x.protocol import montar_pacote, extrair_payload

HENRY_IP   = "192.168.0.179"
HENRY_PORT = 3000

def manter_conexao_persistente_henry():
    print("=" * 75)
    print(f"  INICIANDO CONEXÃO PERSISTENTE COM MÉTODO RECOMENDADO DE KEEPALIVE (01+RH+00)")
    print(f"  Alvo: {HENRY_IP}:{HENRY_PORT} | KeepAlive: 01+RH+00 a cada 30s de inatividade")
    print("=" * 75)

    last_keepalive = time.time()

    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(8.0)
        try:
            print(f"[CONEXÃO] Conectando a {HENRY_IP}:{HENRY_PORT}...")
            s.connect((HENRY_IP, HENRY_PORT))
            print(f"✔ [ONLINE] Equipamento {HENRY_IP} conectado com sucesso!")

            last_keepalive = time.time()
            s.settimeout(1.0) # Timeout curto para permitir verificar o timer de 30s

            while True:
                # Se passaram 30s sem tráfego, dispara KeepAlive (01+RH+00)
                if time.time() - last_keepalive > 30.0:
                    try:
                        print(" [KEEPALIVE] > Enviando 01+RH+00 para manter o socket vivo...")
                        s.sendall(montar_pacote("01+RH+00"))
                        last_keepalive = time.time()
                    except Exception as e:
                        print(f" ✘ Erro ao enviar KeepAlive: {e}")
                        break

                # Leitura contínua dos dados enviados pela catraca
                try:
                    data = s.recv(1024)
                    if not data:
                        print(" ✘ Socket encerrado pelo equipamento.")
                        break
                    
                    payload = extrair_payload(data)
                    print(f" [RECV] Dados recebidos: {payload}")
                    
                    # Qualquer dado recebido atualiza o timestamp do KeepAlive
                    last_keepalive = time.time()

                except socket.timeout:
                    # Timeout normal de 1s, continua o loop
                    continue
                except Exception as e:
                    print(f" ✘ Erro na leitura do socket: {e}")
                    break

        except Exception as e:
            print(f"✘ [OFFLINE] Falha de conexão com {HENRY_IP}: {e}")
        finally:
            s.close()
            print("[RECONEXÃO] Conexão fechada. Tentando reconectar em 15 segundos...
")
            time.sleep(15)

if __name__ == "__main__":
    try:
        manter_conexao_persistente_henry()
    except KeyboardInterrupt:
        print("
Loop de KeepAlive encerrado pelo usuário.")
