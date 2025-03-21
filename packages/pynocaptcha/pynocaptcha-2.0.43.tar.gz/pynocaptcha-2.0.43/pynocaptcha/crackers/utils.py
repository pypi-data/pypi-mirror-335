# -*- coding: UTF-8 -*-

import re


def parse_client_hints(ua):
    version = int(re.search(r"(\d+)\.0\.0\.0", ua)[1])
    greasey_chars = [
        " ",
        "(",
        ":",
        "-",
        ".",
        "/",
        ")",
        ";",
        "=",
        "?",
        "_",
    ]
    greased_versions = ["8", "99", "24"]
    orders = [
        [0, 1, 2],
        [0, 2, 1],
        [1, 0, 2],
        [1, 2, 0],
        [2, 0, 1],
        [2, 1, 0],
    ][version % 6]
    brands = [
        {
            "brand": "".join([
                "Not",
                greasey_chars[version % 11],
                "A",
                greasey_chars[(version + 1) % 11],
                "Brand",
            ]),
            "version": greased_versions[version % 3],
        },
        { "brand": "Chromium", "version": str(version) },
        { "brand": "Google Chrome", "version": str(version) },
    ]
    _brands = [None, None, None]
    _brands[orders[0]] = brands[0]
    _brands[orders[1]] = brands[1]
    _brands[orders[2]] = brands[2]
    
    return ", ".join(map(lambda _: f'"{_["brand"]}";v="{_["version"]}"', _brands))
