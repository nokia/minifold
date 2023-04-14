#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

# ---------------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------------

import sys

if sys.version_info < (3, 5):  # async, await
    raise RuntimeError("asyncio requires python>=3.5")

try:
    import requests
except ImportError as e:
    from .log import Log
    Log.warning(
        "\n".join([
            "Please install requests",
            "  APT: sudo apt install python3-requests",
            "  PIP: sudo pip3 install --upgrade requests",
        ])
    )
    raise e

import asyncio, datetime, re
import concurrent.futures

from copy              import deepcopy
from functools         import partial
from .connector        import Connector
from .query            import ACTION_READ, Query
from .html             import html_to_text
from .log              import Log
from .proxy            import make_session
from .request_cache    import install_cache

DEFAULT_TIMEOUT = (1.0, 2.0)    # (connect timeout, read timeout)
# DEFAULT_TIMEOUT = (0.5, 1.0)  # (connect timeout, read timeout)

def now() -> str:
    """
    Crafts a string storing the current timestamp.

    Returns:
        A string containing current timestamp.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def download(url: str, timeout: tuple = DEFAULT_TIMEOUT, cache_filename: str = None):
    """
    Downloads the content related to a given URL.
    See also :py:func:`request_cache` to enable caching.

    Args:
        url (str): A string containing the target URL.
        timeout (tuple): A ``(float, float)`` tuple corresponding to the
            (connect timeout, read timeout).
        cache_filename (str): A string containing path to the cache to use.
            Pass ``None`` to use the default cache.

    Raises:
        requests.exceptions.ConnectionError
        requests.exceptions.ConnectTimeout
        requests.exceptions.ContentDecodingError
        requests.exceptions.ReadTimeout
        requests.exceptions.SSLError

    Returns:
        The corresponding response.
    """
    install_cache(cache_filename)
    try:
        # Log.debug("download: GET %s (timeout = %s)" % (url, timeout))
        # https://stackoverflow.com/questions/8287628/proxies-with-python-requests-module
        session = make_session()
        return session.get(
            url,
            timeout = timeout
        )
    except Exception as exc:
        Log.warning("download: GET %s (timeout = %s): %s" % (url, timeout, exc))
        return exc

def trim_http(url: str) -> str:
    """
    Discards the ``"http://"`` or `` "https://"`` prefix from an url.

    Args:
        url (str): A str containing an URL.

    Returns:
        The str corresponding to the trimmed URL.
    """
    return re.sub("https?://", "", url, flags = re.IGNORECASE)

# https://skipperkongen.dk/2016/09/09/easy-parallel-http-requests-with-python-and-asyncio/
async def downloads_async(
    urls: list,
    timeout: tuple = DEFAULT_TIMEOUT,
    return_exceptions: bool = True
):
    """
    Asynchronous download procedure.

    Args:
        urls (list): An iterable over strings, each of them corresponding to an URL.
        timeout (tuple): A tuple ``(float, float)`` corresponding to the
            (connect timeout, read timeout).
        return_exceptions (bool): Pass ``True`` if this function is allowed to raise
            exceptions or must be quiet, ``False`` otherwise. Defaults to ``True``.

    Raises:
        See the :py:func:`download` function for the list of possible exceptions.

    Returns:
        A ``dict({str : ?}}`` mapping for each queried URL the corresponding
        contents (if successful), the corresponding :py:class:`Exception` otherwise.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                partial(download, timeout=timeout, cache_filename=None),
                url
            ) for url in urls
        ]
        return {
            url : response
            for (url, response) in zip(
                urls,
                await asyncio.gather(*futures, return_exceptions = return_exceptions)
            )
        }

def downloads(*args) -> dict:
    """
    Performs multiple downloads in parallel. See downloads_async for further details.
    See also :py:func:`request_cache` to enable caching.

    Args:
        urls (list): An iterable over strings, each of them corresponding to an URL.
        timeout (tuple): A tuple ``(float, float)`` corresponding to the
            (connect timeout, read timeout).
        return_exceptions (bool): Pass ``True`` if this function is allowed to raise
            exceptions or must be quiet, ``False`` otherwise. Defaults to ``True``.

    Returns:
        A ``dict({str : ?}}`` mapping for each queried URL the corresponding
        contents (if successful), the corresponding :py:class:`Exception` otherwise.
    """
    Log.debug("[%s] downloads: start" % now())
    # https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
    # loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ret = loop.run_until_complete(downloads_async(*args))
    Log.debug("[%s] downloads: %d URLs fetched" % (now(), len(ret)))
    return ret

# ---------------------------------------------------------------------------------
# Minifold
# ---------------------------------------------------------------------------------

def extract_response(response: object, extract_text: bool = True) -> object:
    """
    Extracts from a response the corresponding contents or Exception.

    Args:
        response (object): A :py:class:`requests.Response` or an
            :py:class:`Exception` instance.
        extract_text (bool): A bool indicating if text must be extracted
            from HTML.

    Returns:
        The corresponding Exception or str.
    """
    if isinstance(response, Exception):
        return response  # Forward exception
    text = response.text
    return html_to_text(text) if extract_text else text

RE_VALID_URL = re.compile("https?://.*")

class DownloadConnector(Connector):
    """
    The :py:class:`DownloadConnector` allows to fetch data over HTTP.
    """
    def __init__(
        self,
        map_url_out: dict,
        child: Connector,
        downloads :callable = downloads,
        extract_response: callable = extract_response
        # TODO Pass downloads() parameters
    ):
        """
        Constructor.

        Args:
            map_url_out (dict): dict(str : str) entry attribute containing an URL to another
                entry attribute that will store the contents provided by this URL.
                Example: ``{"url" : "html_content"}``
            child (Connector): The child Connector.
            downloads (callable): ``Callback(urls) -> dict(url : content)`` where
                urls is an iterable of URLs and where.
                the returned dict maps each urls and the corresponding response.
                Note: You could pass ``partial(download, ...)`` to customize the timeouts.
            extract_response (callable): ``Callback(response) -> str`` callback used to extract
                data from an HTTP query.
        """
        super().__init__()
        self.map_url_out = map_url_out
        self.child = child
        self.downloads = downloads
        self.extract_response = extract_response

    def query(self, query :Query) -> list:
        """
        Handles an input :py:class:`Query` instance..

        Args:
            query: A :py:class:`Query` instance.

        Returns:
            The corresponding results.
        """
        if query.action == ACTION_READ:
            # Pull child records
            q_child = deepcopy(query)  # TODO: rework q_child like in LambdasConnector
            q_child.attributes = set(query.attributes) - set(self.map_url_out.values())
            entries = self.child.query(q_child)

            attributes = set(query.attributes) & set(self.map_url_out.values()) \
                if query.attributes else set(self.map_url_out.values())

            # If some URLs must be queried
            if attributes:
                # Fetch URLs
                urls = set()
                for attr_url in self.map_url_out.keys():
                    urls |= {
                        entry.get(attr_url)
                        for entry in entries
                        if (
                            isinstance(entry.get(attr_url), str)
                            and RE_VALID_URL.match(entry.get(attr_url))
                        )
                    }
                Log.debug("Starting fetching %d URLs" % len(urls))
                map_url_response = self.downloads(urls)
                if self.extract_response:
                    map_url_response = {
                        url : self.extract_response(response)
                        for (url, response) in map_url_response.items()
                    }

                # Dispatch responses in appropriate entry attributes
                for (attr_url, attr_out) in self.map_url_out.items():
                    for entry in entries:
                        url = entry.get(attr_url)
                        if url:
                            entry[attr_out] = map_url_response[url]

            # Forward to parent Connector once entry are reshaped.
            entries = self.reshape_entries(query, entries)
            return entries
        else:
            raise RuntimeError("Action not implemented: %s" % query.action)

    def attributes(self, object: str) -> set:
        """
        Lists available attributes related to a given collection of object
        stored in this :py:class:`DownloadConnector` instance.

        Args:
            object (str): The name of the collection of entries.

        Returns:
            The set of available attributes for ``object``.
        """
        return set(self.child.attributes(object)) | set(self.map_url_out.values())
