import requests
from urllib.parse import urlencode, urljoin
from endpoints import endpoints
import urllib3

urllib3.disable_warnings()
class Client:
    def __init__(self, ip, username, password):
        self.base_url = f"https://{ip}"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })
        self.config:str = None
        
        if self.authenticate():
            self.config = self.get_config()

    def authenticate(self):
        payload = {
            'username': self.username,
            'password': self.password
        }

        url = urljoin(self.base_url, endpoints["auth_url"])
        response = self.session.post(url, data=payload)

        if response.ok:
            self.session.cookies.update(response.cookies)
            self.session.headers.update({'X-CSRF-ID': response.headers.get('X-CSRF-ID')})
            return True
        else:
            print(f"[!] Authentication failed ({response.status_code}): {response.text}")
            return False

    def get_config(self):
        url = urljoin(self.base_url, endpoints["readCfgUrl"])
        response = self.session.get(url)
        if not response.ok:
            print(f"[!] Failed to get config ({response.status_code})")
        else:
            self.confg = response.text
    
    def activate_ssh(self):
        self.config.replace("sshd.status=enabled", "sshd.status=disabled", 1)

    def write_config(self):
        url = urljoin(self.base_url, endpoints["writeCfgUrl"])
        data = urlencode({'cfgData': self.config})
        response = self.session.post(url, data=data)
        if not response.ok:
            print(f"[!] Failed to write config ({response.status_code}): {response.text}")
        return response.ok


client = Client("ip","user","password")
print(client.confg)
client.activate_ssh()
client.write_config()