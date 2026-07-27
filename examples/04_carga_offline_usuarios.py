#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 4: Carga Offline de Usuários (Push para Memória Flash)
"""
from henry8x import HenryClient

client = HenryClient(ip="192.168.0.179", port=3000)

lista_usuarios = [
    {"id": "1001", "nome": "USUARIO TESTE 01", "cartao": "4510994730"},
    {"id": "1002", "nome": "USUARIO TESTE 02", "cartao": "4510994731"},
    {"id": "1003", "nome": "USUARIO TESTE 03", "cartao": "4510994739"},
]

print("1. Sincronizando data e hora...")
client.atualizar_data_hora()

print("2. Enviando lista de usuários em massa...")
for u in lista_usuarios:
    ok, resp = client.enviar_usuario(user_id=u['id'], nome=u['nome'], cartao=u['cartao'])
    print(f" -> Envio {u['nome']}: {'OK' if ok else 'FALHA'}")

print("3. Verificando quantidade total salva na catraca...")
ok, qtd = client.consultar_qtd_usuarios()
print(f"Total na memória: {qtd}")
