#!/usr/bin/env python3
"""
Sort all active or paused downloads in aria2 server.

Usage:
    aria2-sort.py <URI> <TOKEN>
    URI - jsonrpc for aria2 server running in daemon mode
    TOKEN - `rpc-secret` configuration value in aria2

Note that this script has the following assumptions:
 - Aria2 is running in daemon mode
 - A secret is set in aria2
 - `requests` python library has been installed globally
"""
import json
import sys
from typing import List

import requests


class DownloadItem(object):
    """
    An download item in aria2

    Properties:
        gid - string of internal GID
        path - string of download path to local drive
    """

    def __init__(self, stat: dict) -> None:
        """
        Args:
            stat - Status object of this download item
        """
        self.gid = stat['gid']
        self.path = stat['files'][0]['path']


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

    def tell_active(self, keys: List[str] = []) -> List[DownloadItem]:
        """
        aria2.tellActive
        """
        res = self._call('aria2.tellActive', keys)['result']
        return [DownloadItem(item) for item in res]

    def tell_waiting(self, offset: int, num: int,
                     keys: List[str] = []) -> List[DownloadItem]:
        """
        aria2.tellWaiting
        """
        res = self._call('aria2.tellWaiting', offset, num, keys)['result']
        return [DownloadItem(item) for item in res]

    def multi_change_position(self, gids: List[str]) -> dict:
        """
        Change all gid position using aria2.changePosition and system.multicall

        Args:
            gids - New gid order
        """
        params = [{
            'methodName': 'aria2.changePosition',
            'params': [self._token, gid, i, 'POS_SET']
        } for (i, gid) in enumerate(gids)]
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
    keys = ['gid', 'files']
    downloads = aria.tell_active(keys) + aria.tell_waiting(0, 100, keys)

    sort = sorted(downloads, key=lambda x: x.path)
    gids = [x.gid for x in sort]
    aria.multi_change_position(gids)

    print(f'Sorted {len(gids)} downloads')


if __name__ == "__main__":
    main()
