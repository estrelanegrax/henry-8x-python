import socket
import threading
import time
from .protocol import montar_pacote, extrair_payload

class HenryServerDaemon:
    """
    Daemon de conexões TCP persistentes com KeepAlive (01+RH+00).
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 3000):
        self.host = host
        self.port = port
        self.equipamentos = {}
        self.running = False

    def adicionar_equipamento(self, ip: str, port: int = 3000, eh_catraca: bool = True):
        self.equipamentos[ip] = {"port": port, "eh_catraca": eh_catraca}

    def iniciar(self):
        self.running = True
        threads = []
        for ip, cfg in self.equipamentos.items():
            t = threading.Thread(target=self._worker_equipamento, args=(ip, cfg['port'], cfg['eh_catraca']), daemon=True)
            t.start()
            threads.append(t)

        print(f"[HenryServerDaemon] Iniciados {len(threads)} workers de monitoramento com KeepAlive.")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False

    def _worker_equipamento(self, ip: str, port: int, eh_catraca: bool):
        while self.running:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            try:
                sock.connect((ip, port))
                sock.settimeout(1.0)
                print(f"[HenryDaemon {ip}] Conectado e ativo.")

                last_keepalive = time.time()

                while self.running:
                    # Envia KeepAlive 01+RH+00 a cada 30 segundos de inatividade
                    if time.time() - last_keepalive > 30.0:
                        try:
                            sock.sendall(montar_pacote("01+RH+00"))
                            last_keepalive = time.time()
                        except Exception as e:
                            print(f"[HenryDaemon {ip}] Erro ao enviar KeepAlive: {e}")
                            break

                    try:
                        dados = sock.recv(4096)
                        if not dados:
                            break
                        
                        last_keepalive = time.time()
                        payload = extrair_payload(dados)

                        # Processa bips e eventos
                        if "+REON+000+0" in payload:
                            if eh_catraca:
                                cmd = "01+REON+00+5]5]Acesso Liberado}Seja Bem-vindo]1"
                            else:
                                cmd = "01+REON+00+1]4]Porta Liberada}Seja Bem-vindo]1"
                            sock.sendall(montar_pacote(cmd))
                        elif "+REON+000+81" in payload:
                            print(f"[HenryDaemon {ip}] Giro confirmado (+81 TURN RIGHT/LEFT)")
                        elif "+REON+000+82" in payload:
                            print(f"[HenryDaemon {ip}] Desistência de giro (+82 GIVE UP)")

                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"[HenryDaemon {ip}] Erro de leitura socket: {e}")
                        break

            except Exception as e:
                print(f"[HenryDaemon {ip}] Erro na conexão: {e}")
            finally:
                sock.close()
                print(f"[HenryDaemon {ip}] Desconectado. Reconectando em 15s...")
                time.sleep(15)
