#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/10
# @Author  : jiangwen04
# @File    : afs_config.py
"""
import base64

CONFIG = ("c3RvcmFnZV90eXBlPSJhZnMiCgpmc19uYW1lPSJhZnM6Ly9zenRoLmFmcy5iYWlkdS5jb206OTkwMiIKZnNfdWdpPSJpcWktZGF0YSxMamI"
          "xMjEwMjAjIgphZnNfcmVtb3RlX21vdW50X3BvaW50PSIvdXNlci9pcWktZGF0YSIKCiMg5ZCv55SocHl0aG9uMwp1c2VfcHl0aG9uMz0xCi"
          "Mg5oyC6L29IGFmcyDnmoTlvIDlhbMKbW91bnRfYWZzPSJ0cnVlIgojIGFmcyDot6/lvoTnmoTov5znq6/mjILovb3ngrkKIyDkvZzkuJro"
          "v5DooYznjq/looPnmoTmnKzlnLDmjILovb3ngrkKYWZzX2xvY2FsX21vdW50X3BvaW50PSIvcm9vdC9wYWRkbGVqb2Ivd29ya3NwYWNlL2V"
          "udl9ydW4vYWZzLyIKb3V0cHV0X3BhdGg9Ii91c2VyL2lxaS1kYXRhL291dHB1dCI=")


def write_afs_config(path):
    """
    write afs config file
    """
    with open(path, 'w') as f:
        f.write(base64.b64decode(CONFIG).decode())