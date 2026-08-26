#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/26 16:02
# @File  : proxy.py

import requests
import yaml
from flask import Flask

with open("cfg.yaml", "r", encoding="utf-8") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)
app = Flask(__name__)


@app.route("/get-proxy", methods=["GET"])
def get_proxy():
    # ip = requests.get('http://proxy-extract-url').text
    ip = '127.0.0.1:7899'
    return ip, 200, {
        "Content-Type": "text/plain"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=cfg['proxy_backend_port'])
