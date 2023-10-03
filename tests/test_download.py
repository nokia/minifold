#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import requests
from minifold.entries_connector import EntriesConnector
from minifold.query import Query
from minifold.download import DownloadConnector, download

# ============================================================
# NOTE: If you require proxy, see minifold.proxy
#
# Example:
#
# from minifold.proxy import enable_proxy_localhost
# enable_proxy_localhost()
# ============================================================

URLS = [
    "https://apple.com",
    "https://microsoft.com",
    "https://www.google.com",
    "https://play.google.com",
    "https://plus.google.com",
    "https://support.google.com",
    "https://youtube.com",
    "https://www.blogger.com",
    "https://accounts.google.com",
    "https://mozilla.org",
    "https://docs.google.com",
    "https://en.wikipedia.org",
    "https://wordpress.org",
    "https://sites.google.com",
    "https://adobe.com",
    "http://googleusercontent.com",
    "https://vimeo.com",
]


def test_download():
    success = 0
    for url in URLS:
        response = download(url)
        if isinstance(response, requests.models.Response):
            success += 1
    assert success >= 1


def test_download_connector():
    entries = [{"url": url} for url in URLS]
    c = DownloadConnector(
        {"url": "response"},  # Means entry["response"] = download(entry["url"])
        EntriesConnector(entries)
    )
    entries = c.query(Query())

    success = 0
    for entry in entries:
        if isinstance(entry["response"], str):
            success += 1
    assert success >= 1


def test_download_select():
    entries = [{"url": url} for url in URLS]
    c = DownloadConnector(
        {"url": "response"},
        EntriesConnector(entries)
    )
    entries = c.query(Query(attributes=("url", "response")))

    success = 0
    for entry in entries:
        if isinstance(entry["response"], str):
            success += 1
    assert success >= 1


def test_html_to_text():
    urls = [
        "https://www.merriam-webster.com/dictionary/tapir"
    ]
    entries = [{"url": url} for url in urls]
    c = DownloadConnector(
        {"url": "response"},
        EntriesConnector(entries)
    )
    entries = c.query(Query(attributes=("url", "response")))

    success = 0
    for entry in entries:
        response = entry["response"]
        if isinstance(entry["response"], str):
            assert "</" not in response, "Found </ in %r" % response
            success += 1
    assert success >= 1


# ----------------------------------------------------------------------------
#  Example:
# ----------------------------------------------------------------------------
#
# import requests
#
# def responses_to_files(urls: list, map_url_response: dict, output_dir: str = ".") -> tuple:
#     new_urls = list()
#     changed = False
#     for (i, url) in enumerate(urls):
#         response = map_url_response[url]
#         if not isinstance(response, Exception):
#             with open("%s/%03d_%s.html" % (output_dir, i, trim_http(url)), "w") as f:
#                 print(response.text, file = f)
#                 new_urls.append(url)
#         else:
#             print("%s failed (%s): %s" % (url, type(response), response))
#             if isinstance(response, requests.exceptions.SSLError):
#                 new_urls.append(url.replace("https", "http"))
#             else:
#                 new_urls.append(url.replace("http", "#http"))
#                 changed = True
#     return (new_urls, changed)
#
# def load_urls(filename: str) -> list:
#     with open(filename) as f:
#         return [line.strip() for line in f if not line.startswith("#")]
#
# def main():
#     urls = load_urls("urls.txt")
#     map_url_response = downloads(urls)
#     (new_urls, changed) = responses_to_files(urls, map_url_response)
#     if changed:
#        with open(filename, "w") as f:
#            print("\n".join(self.new_urls), file = f)
