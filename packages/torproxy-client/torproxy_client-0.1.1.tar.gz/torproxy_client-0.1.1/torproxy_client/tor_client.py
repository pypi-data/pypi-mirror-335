import requests
import socks
import socket
from requests.adapters import HTTPAdapter
from stem import Signal
from stem.control import Controller

class TorProxyClient:
    def __init__(self, tor_host='127.0.0.1', tor_port=9050, control_port=9051, control_password=None):
        self.tor_host = tor_host
        self.tor_port = tor_port
        self.control_port = control_port
        self.control_password = control_password
        self.session = requests.Session()

        # Tor接続の初期化
        if self.tor_initialize():
            self.session.proxies = {
                'http': f'socks5h://{self.tor_host}:{self.tor_port}',
                'https': f'socks5h://{self.tor_host}:{self.tor_port}',
            }
        else:
            print("Tor initialization failed. Falling back to direct connection.")

        # セッションのリトライ設定
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def tor_initialize(self):
        """
        Torの初期化と接続確認
        Returns:
            bool: True (成功) / False (失敗)
        """
        try:
            socks.set_default_proxy(socks.SOCKS4, addr=self.tor_host, port=self.tor_port)
            socket.socket = socks.socksocket
            response = requests.get('https://check.torproject.org')
        except Exception as e:
            print(f"Tor initialization error: {e}")
            return False

        if 'Congratulations. This browser is configured to use Tor.' in response.text:
            print("Tor initialization successful.")
            return True
        else:
            print("Tor initialization failed. Not connected to Tor network.")
            return False

    def change_ip(self):
        """Torネットワーク上でIPを切り替える"""
        with Controller.from_port(port=str(self.control_port)) as controller:
            controller.authenticate(self.control_password)
            controller.signal(Signal.NEWNYM)
            print("IP Address changed!")

    def make_request(self, url):
        """指定したURLに対してGETリクエストを送信"""
        try:
            response = self.session.get(url)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def close(self):
        """セッションを閉じる"""
        self.session.close()
