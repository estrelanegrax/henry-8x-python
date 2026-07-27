import socket
import time
import threading
from datetime import datetime
from .protocol import montar_pacote, extrair_payload

class HenryClient:
    """
    Cliente TCP síncrono para comunicação com equipamentos Henry Primme SF (Catracas e Acesso).
    """
    def __init__(self, ip: str, port: int = 3000, timeout: float = 4.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self._persistent_sock = None
        self._keepalive_running = False
        self._keepalive_thread = None

    def _enviar(self, cmd_txt: str) -> tuple:
        if self._persistent_sock:
            try:
                self._persistent_sock.sendall(montar_pacote(cmd_txt))
                buf = b""
                t0 = time.time()
                while time.time() - t0 < 1.2:
                    try:
                        chunk = self._persistent_sock.recv(4096)
                        if chunk:
                            buf += chunk
                            if b"\x03" in chunk: break
                        else: break
                    except socket.timeout: break
                return True, extrair_payload(buf)
            except Exception as e:
                try:
                    self._persistent_sock.close()
                except: pass
                self._persistent_sock = None

        pacote = montar_pacote(cmd_txt)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(self.timeout)
            s.connect((self.ip, self.port))
            s.sendall(pacote)
            buf = b""
            t0 = time.time()
            while time.time() - t0 < 1.2:
                try:
                    chunk = s.recv(16384)
                    if chunk:
                        buf += chunk
                        t0 = time.time()
                    else: break
                except socket.timeout: break
            payload = extrair_payload(buf)
            return True, payload
        except Exception as e:
            return False, str(e)
        finally:
            s.close()

    def iniciar_keepalive(self, intervalo_segundos: int = 15):
        """Mantém um socket TCP ativo enviando pings 01+RH+00 periodicamente."""
        self._keepalive_running = True
        self._keepalive_thread = threading.Thread(target=self._loop_keepalive, args=(intervalo_segundos,), daemon=True)
        self._keepalive_thread.start()

    def parar_keepalive(self):
        """Encerra a thread de KeepAlive e fecha a conexão persistente."""
        self._keepalive_running = False
        if self._persistent_sock:
            try:
                self._persistent_sock.close()
            except: pass
            self._persistent_sock = None

    def _loop_keepalive(self, intervalo: int):
        while self._keepalive_running:
            if not self._persistent_sock:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(self.timeout)
                    s.connect((self.ip, self.port))
                    self._persistent_sock = s
                except Exception as e:
                    time.sleep(5)
                    continue

            try:
                self._persistent_sock.sendall(montar_pacote("01+RH+00"))
                self._persistent_sock.settimeout(2.0)
                try:
                    self._persistent_sock.recv(1024)
                except socket.timeout: pass
            except Exception as e:
                try:
                    self._persistent_sock.close()
                except: pass
                self._persistent_sock = None

            for _ in range(intervalo):
                if not self._keepalive_running: break
                time.sleep(1)

    def ler_data_hora(self) -> tuple:
        return self._enviar("01+RH+00")

    def atualizar_data_hora(self, dt=None) -> tuple:
        if dt is None: dt = datetime.now()
        dt_str = dt.strftime("%d/%m/%y %H:%M:%S")
        ok, resp = self._enviar(f"01+EH+00+{dt_str}]]")
        return ok and ("+EH+000" in resp or "+EH+00" in resp), resp

    def consultar_qtd_usuarios(self) -> tuple:
        return self._enviar("01+RQ+00+U")

    def enviar_usuario(self, user_id: str, nome: str, cartao: str) -> tuple:
        cmd = f"01+EU+00+1+I[{user_id}[{nome[:32]}[[1[{cartao}"
        ok, resp = self._enviar(cmd)
        sucesso = ok and ("+EU+000+1+0" in resp or "+EU+00" in resp and not "00]22" in resp)
        return sucesso, resp

    def remover_usuario(self, user_id: str) -> tuple:
        cmd = f"01+EU+00+1+E[{user_id}"
        ok, resp = self._enviar(cmd)
        sucesso = ok and ("+EU+000+1+12" in resp or "+EU+000+1+0" in resp)
        return sucesso, resp

    def liberar_remoto(self, sentido: str = "Entrada", mensagem: str = "Acesso Liberado", mensagem_linha2: str = "BEM-VINDO", tempo_segundos: int = 5) -> tuple:
        """
        Envia comando de liberação remota (REON) configurável sem texto fixo de software.
        """
        codigo = "5" if sentido.lower() in ["entrada", "e"] else "6" if sentido.lower() in ["saida", "s"] else "1"
        cmd = "01+REON+00+" + str(codigo) + "]" + str(tempo_segundos) + "]" + mensagem + "}" + mensagem_linha2 + "]1"
        ok, resp = self._enviar(cmd)
        sucesso = ok and ("+REON+000" in resp or "+REON+00" in resp)
        return sucesso, resp
