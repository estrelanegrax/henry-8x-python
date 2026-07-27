#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 2: Cadastrar e Remover Usuário na Memória Flash
"""
from henry8x import HenryClient

client = HenryClient(ip="192.168.0.179", port=3000)

# Cadastrar novo usuário
print("Cadastrando usuário na memória Flash...")
ok_cad, resp_cad = client.enviar_usuario(
    user_id="2050",
    nome="JOAO DA SILVA",
    cartao="2050"
)
print(f"Resultado Cadastro: {ok_cad} | Payload: {resp_cad}")

# Remover usuário
print("Removendo usuário da memória Flash...")
ok_rem, resp_rem = client.remover_usuario(user_id="2050")
print(f"Resultado Remoção: {ok_rem} | Payload: {resp_rem}")
