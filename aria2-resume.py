#!/usr/bin/env python3
"""
Resume first 100 error downloads in Aria2 server.

Usage:
    aria2-resume.py <URI> <TOKEN>
    URI - jsonrpc for aria2 server running in daemon mode
    TOKEN - `rpc-secret` configuration value in aria2

Note that this script has the following assumptions:
 - Aria2 is running in daemon mode
 - A secret is set in aria2
 - For all downloads, there is only one result file (i.e. not BT downloads)
 - All error downloads has resolved their filename already
 - `requests` python library has been installed globally
"""
import json
import sys
from os import path
from typing import List, Tuple

import requests


class Aria(object):
    """
    Representing an aria2 endpoint.

    Use this object to create method calls.

    Properties:
        _endpoint - URI pointing to aria2 server jsonrpc api
        _token - rpc-secret value in the server
    """

    def __init__(self, uri: str, token: str) -> None:
        """
        Args:
            uri - URI pointing to jsonrpc endpoint of aria2 server
            token - rpc-secret token for the server
        """
        self._endpoint = uri
        self._token = 'token:' + token

    def tell_stopped(self, offset: int, num: int) -> dict:
        """
        aria2.tellStopped
        """
        return self._call('aria2.tellStopped', offset, num)['result']

    def multi_remove_download_result(self, gids: List[str]) -> dict:
        """
        aria2.removeDownloadResult, using system.multicall
        """
        params = [{
            'methodName': 'aria2.removeDownloadResult',
            'params': [self._token, gid]
        } for gid in gids]
        return self._multicall(params)

    def multi_add_uri(self, urls: List[Tuple[str, str]]) -> dict:
        """
        aria2.addUri, using system.multicall

        Args:
            urls - List of tuples. First element is url, second is filename
        """
        params = [{
            'methodName': 'aria2.addUri',
            'params': [self._token, [url], {
                'out': filename
            }]
        } for (url, filename) in urls]
        return self._multicall(params)

    def _req(self, data: dict) -> dict:
        """
        Sent request to aria2.
        """
        d = json.dumps(data)
        res = requests.post(self._endpoint, data=d)
        if not res.ok:
            print(res.json())
            res.raise_for_status()
        return res.json()

    def _call(self, method: str, *params) -> dict:
        """
        Call an aria2 method.
        """
        p = list(params)
        p.insert(0, self._token)
        jsonreq = {
            'jsonrpc': '2.0',
            'id': 'qwer',
            'method': method,
            'params': p
        }
        return self._req(jsonreq)

    def _multicall(self, params: List[dict]) -> dict:
        """
        Issue multicall request to aria.
        """
        jsonreq = {
            'jsonrpc': '2.0',
            'id': 'qwer',
            'method': 'system.multicall',
            'params': [params]
        }
        return self._req(jsonreq)


def main():
    uri = sys.argv[1]
    token = sys.argv[2]

    aria = Aria(uri, token)
    downloads = aria.tell_stopped(0, 100)
    errored = [x for x in downloads if int(x['errorCode']) > 0]

    # Remove all errored first
    aria.multi_remove_download_result(
        [stat['gid'] for stat in errored])
    print(f'Removed {len(errored)} errored downloads')

    # Create download requests
    urls = [(s['files'][0]['uris'][0]['uri'],
             path.relpath(s['files'][0]['path'], s['dir'])) for s in errored]
    aria.multi_add_uri(urls)
    print('New requests on removed download is added')


if __name__ == "__main__":
    main()
