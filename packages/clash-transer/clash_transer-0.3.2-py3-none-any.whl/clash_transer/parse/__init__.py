import base64
import json

from ..log import LOGGER
from urllib.parse import unquote, urlparse
from ..worker.vars import dist_file_v


class Parse:
    @classmethod
    def parse(cls, text: str, suffix: str):
        return cls(text, suffix)

    def __init__(self, text: str, suffix: str) -> None:
        self.server_ports = set()
        match suffix.lower():
            case "ssr":
                self.res = self.parse_ssr(text)
            case "ss":
                self.res = self.parse_ss(text)
            case "vmess":
                self.res = self.parse_vmess(text)
            case "list":
                self.res = self.parse_list(text)
        LOGGER.info("解析完成 %s", dist_file_v.get().name)

    @staticmethod
    def b64decode(text):
        if isinstance(text, str):
            byte = text.encode("utf-8")
        else:
            byte = text
        if not byte.endswith(b"="):
            byte = byte + b"=" * (4 - (len(byte) % 4))
        res = base64.urlsafe_b64decode(byte)
        return res

    def parse_ssr(self, text):
        decoded_str = self.b64decode(text)
        links = decoded_str.splitlines()
        for link in links:
            # LOGGER.debug(link)
            parsed_url = urlparse(link)
            if parsed_url.scheme != "ssr":
                continue
            f_str = self.b64decode(parsed_url.netloc).decode("utf-8")
            link_obj = urlparse(f_str)
            server = link_obj.scheme
            try:
                port, protocol, cipher, obfs, password_base64 = link_obj.path.strip(
                    "/"
                ).split(":")
            except ValueError:
                server, port, protocol, cipher, obfs, password_base64 = (
                    link_obj.path.strip("/").split(":")
                )
            password = self.b64decode(password_base64).decode("utf-8")
            query_pairs = (i.split("=", 1) for i in link_obj.query.split("&"))
            query_dict = {key: value for key, value in query_pairs}
            protoparam = self.b64decode(query_dict["protoparam"]).decode("utf-8")
            name = self.b64decode(query_dict["remarks"]).decode("utf-8")
            obfsparam = self.b64decode(query_dict["obfsparam"]).decode("utf-8")
            obfsparam = obfsparam if obfsparam else "none"
            link_dict = {
                "name": name,
                "type": "ssr",
                "server": server,
                "port": port,
                "cipher": cipher,
                "password": password,
                "protocol": protocol,
                "protocol-param": protoparam,
                "obfs": obfs,
                "obfs-param": obfsparam,
            }
            if (server, port) not in self.server_ports:
                self.server_ports.add((server, port))
                yield link_dict

    def parse_ss(self, text):
        decoded_str = self.b64decode(text)
        links = decoded_str.splitlines()
        for link in links:
            link = urlparse(link.decode("utf-8"))
            if link.scheme != "ss":
                continue
            cipher, password = self.b64decode(link.username).split(b":")
            server = link.hostname
            port = link.port
            name = unquote(link.fragment)
            link_dict = {
                "name": name,
                "type": "ss",
                "server": server,
                "port": port,
                "cipher": cipher.decode("utf-8"),
                "password": password.decode("utf-8"),
                "udp": True,
                "protocol": "origin",
            }
            if (server, port) not in self.server_ports:
                self.server_ports.add((server, port))
                yield link_dict

    def parse_vmess(self, text):
        decoded_str = self.b64decode(text)
        links = decoded_str.splitlines()
        for link in links:
            link = urlparse(link.decode("utf-8"))
            if link.scheme != "vmess":
                continue
            netloc = self.b64decode(link.netloc).decode("utf-8")
            info = json.loads(netloc)
            server = info["add"]
            port = int(info["port"])
            link_dict = {
                "name": info["ps"],
                "type": "vmess",
                "server": server,
                "port": port,
                "uuid": info["id"],
                "alterId": info["aid"],
                "cipher": "auto",
                "udp": True,
                "tls": True,
                "skip-cert-verify": True,
                "servername": info["sni"],
                "network": info["net"],
                "grpc-opts": {"grpc-service-name": info["path"]},
            }
            if (server, port) not in self.server_ports:
                self.server_ports.add((server, port))
                yield link_dict

    def parse_list(self, text):
        for line in text.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("/"):
                continue
            try:
                rule, addr, do = line.split(",")
            except ValueError:
                continue
            match rule:
                case "host":
                    rule = "DOMAIN"
                case "ip-cidr":
                    rule = "IP-CIDR"
                case "host-suffix":
                    rule = "DOMAIN-SUFFIX"
                case "host-keyword":
                    rule = "DOMAIN-KEYWORD"
                case _:
                    continue
            match do:
                case "DIRECT":
                    do = "直连"
                case "Proxy":
                    do = "PROXY"
                case "REJECT":
                    do = "禁连"
                case "OutSide":
                    do = "Apple OutSide"
                case _:
                    pass
            # LOGGER.debug("%s,%s,%s", rule, addr, do)
            yield (rule, addr, do)
