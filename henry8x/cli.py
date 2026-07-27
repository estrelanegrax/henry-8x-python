#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI (Command Line Interface) da biblioteca henry8x.
Permite executar comandos diretos na catraca/controlador pelo terminal.
"""

import argparse
import sys
from .client import HenryClient

def main():
    parser = argparse.ArgumentParser(description="CLI Henry 8X - Controle de Catracas e Acesso")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # ping
    p_ping = subparsers.add_parser("ping", help="Testa conectividade TCP com o equipamento")
    p_ping.add_argument("--ip", required=True, help="IP do equipamento")
    p_ping.add_argument("--porta", type=int, default=3000, help="Porta TCP (padrão: 3000)")

    # liberar
    p_lib = subparsers.add_parser("liberar", help="Libera o giro da catraca ou relé da porta")
    p_lib.add_argument("--ip", required=True, help="IP do equipamento")
    p_lib.add_argument("--porta", type=int, default=3000, help="Porta TCP (padrão: 3000)")
    p_lib.add_argument("--sentido", default="entrada", choices=["entrada", "saida", "porta"], help="Sentido da liberação")
    p_lib.add_argument("--mensagem", default="Acesso Liberado", help="Texto do display")
    p_lib.add_argument("--tempo", type=int, default=5, help="Tempo de acionamento em segundos")

    # hora
    p_hora = subparsers.add_parser("hora", help="Lê ou sincroniza a data e hora do relógio")
    p_hora.add_argument("--ip", required=True, help="IP do equipamento")
    p_hora.add_argument("--porta", type=int, default=3000, help="Porta TCP (padrão: 3000)")
    p_hora.add_argument("--sincronizar", action="store_true", help="Sincroniza com a hora atual do PC")

    # cadastrar
    p_cad = subparsers.add_parser("cadastrar", help="Cadastra um usuário na memória Flash")
    p_cad.add_argument("--ip", required=True, help="IP do equipamento")
    p_cad.add_argument("--porta", type=int, default=3000, help="Porta TCP (padrão: 3000)")
    p_cad.add_argument("--id", required=True, help="Matrícula/ID do usuário")
    p_cad.add_argument("--nome", required=True, help="Nome do usuário")
    p_cad.add_argument("--cartao", required=True, help="Número do cartão RFID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = HenryClient(ip=args.ip, port=args.porta)

    if args.command == "ping":
        ok, msg = client.ler_data_hora()
        if ok:
            print(f"✔ CONECTADO! Equipamento em {args.ip}:{args.porta} respondeu com sucesso.")
        else:
            print(f"✘ ERRO: Não foi possível conectar em {args.ip}:{args.porta} - {msg}")

    elif args.command == "liberar":
        print(f"-> Enviando liberação para {args.ip} (Sentido: {args.sentido}, Mensagem: '{args.mensagem}')...")
        ok, resp = client.liberar_remoto(sentido=args.sentido, mensagem=args.mensagem, tempo_segundos=args.tempo)
        if ok:
            print("✔ Giro / Relé acionado com sucesso!")
        else:
            print(f"✘ Falha na liberação: {resp}")

    elif args.command == "hora":
        if args.sincronizar:
            ok, resp = client.atualizar_data_hora()
            print("✔ Relógio sincronizado!" if ok else f"✘ Erro: {resp}")
        else:
            ok, resp = client.ler_data_hora()
            print(f"Hora no equipamento: {resp}")

    elif args.command == "cadastrar":
        ok, resp = client.enviar_usuario(user_id=args.id, nome=args.nome, cartao=args.cartao)
        if ok:
            print(f"✔ Usuário {args.nome} (ID: {args.id}) cadastrado com sucesso!")
        else:
            print(f"✘ Falha no cadastro: {resp}")

if __name__ == "__main__":
    main()
