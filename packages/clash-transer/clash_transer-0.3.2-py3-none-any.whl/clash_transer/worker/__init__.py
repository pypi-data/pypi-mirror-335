import datetime
import os
import re
import sys
from pathlib import Path
from typing import Iterable

from yaml import dump

from ..config import CONFIG
from ..downloader import Downloader, DownloadRequest, DownloadText
from ..log import LOGGER
from ..parse import Parse
from .detail import get as get_proxy_groups
from .vars import dist_file_v, rules_v, servers_v


class Worker:
    def __init__(self) -> None:
        self.configs = CONFIG.configs

    def download(self) -> Iterable[DownloadText]:
        downloader = Downloader(default_store_path=self.configs["store_path"])
        d = [i for i in CONFIG.configs["subscriptions"]]
        s = [
            DownloadRequest(
                i["url"], i["dist"], datetime.timedelta(seconds=i["expire"])
            )
            for i in d
        ]
        download_resps: Iterable[DownloadText] = downloader.downloads(s)
        return download_resps

    def parse(self, download_resps: Iterable[DownloadText]):
        servers = []
        rules = []
        erros = 0
        for resp in download_resps:
            if resp.text is None:
                LOGGER.error("下载失败 %s", resp.url)
                erros += 1
                continue
            suffix = resp.dist.suffix.strip(".")
            dist_file_v.set(resp.dist)
            if suffix.lower() == "list":
                for i in Parse.parse(resp.text, suffix).res:
                    rules.append(i)
            else:
                for i in Parse.parse(resp.text, suffix).res:
                    i["name"] = i["name"].replace(" ", "")
                    servers.append(i)
        if erros:
            sys.exit(1)
        # store_map = {
        #     "DST-PORT": 10,
        #     "SRC-IP-CIDR": 20,
        #     "IP-CIDR": 30,
        #     "DOMAIN": 40,
        #     "DOMAIN-KEYWORD": 60,
        #     "DOMAIN-SUFFIX": 50,
        # }
        # rules = sorted(rules, key=lambda x: store_map[x[0]])
        exclude_server_regex = re.compile(
            r"|".join(
                [re.escape(keyword) for keyword in self.configs["servers"]["exclude"]]
            )
        )
        # LOGGER.debug(servers)
        servers = [
            server
            for server in servers
            if not re.findall(exclude_server_regex, server["name"])
        ]
        return servers, rules

    def check(self, proxy_group, rules):
        action_set = set()
        group_set = set()
        for _, _, action in rules[:-1]:
            action_set.add(action)
        for group in proxy_group:
            group_set.add(group["name"])
        if "DIRECT" in action_set:
            action_set.remove("DIRECT")
        if "REJECT" in action_set:
            action_set.remove("REJECT")
        diffs = action_set.difference(group_set)
        if diffs:
            LOGGER.error("这些转发组没有设置：%s", ",".join(list(diffs)))
            raise TypeError()

    def combine(self):
        frame = CONFIG.configs["frame"]
        frame["proxies"] = self.server
        frame["proxy-groups"] = self.proxy_groups
        frame["rules"] = self.rules
        return frame
        # cellphone_rule = {
        #     "name": "ssid-group",
        #     "type": "select",
        #     "proxies": ["PROXY", "DIRECT"],
        #     "ssid-policy": {
        #         "ChinaNet-Tn9y_5G": "DIRECT",
        #         "aaaTop1_5G": "DIRECT",
        #         "a13101_5G": "DIRECT",
        #         "cellular": "PROXY",
        #         "default": "PROXY",
        #     },
        # }
        # res["proxy-groups"].append(cellphone_rule)
        # return yaml.dump(res, allow_unicode=True)

    def do(self):
        download_resps = self.download()
        servers, rules = self.parse(download_resps)
        servers_v.set(servers)
        rules_v.set(rules)

        self.proxy_groups = get_proxy_groups()
        self.server = servers
        _rules = (
            [i.split(",") for i in self.configs["rules"]["add_before"]]
            + rules
            + [i.split(",") for i in self.configs["rules"]["add_last"]]
        )
        self.check(self.proxy_groups, _rules)
        self.rules = [",".join(rule) for rule in _rules]
        res = self.combine()
        dist_file = Path(self.configs.get("dist_file"))
        if not dist_file.is_absolute():
            dist_file = Path(os.getcwd()) / dist_file
        with open(dist_file, "w") as f:
            dump(res, f, allow_unicode=True)
            LOGGER.info("新的 clash 配置文件写入 %s", dist_file.as_posix())
