#!/usr/bin/python
# -*- coding: utf-8 -*-

# api_test.py: automated tests for HTTP API
#   - not unit tests but ordered set of automated tests
#   - the database tables are cleaned on start
#
# Author: Tomi.Mickelsson@iki.fi

import unittest
import requests
import json

URL_BASE = "http://localhost:8100/api/"
#URL_BASE = "http://localhost:80/api/" # port is 80 inside docker

URL_SIGNUP     = 'signup'
URL_LOGIN      = 'login'
URL_LOGOUT     = 'logout'
URL_ME         = 'me'
URL_USERS      = 'users'
URL_TRUNCATE   = "../apitest/dbtruncate"
URL_HGMD        = 'hgmd'

URL_MOVIES     = 'movies/'


s = requests.Session() # remember session

headers = {'content-type': 'application/json',
           'User-Agent': 'Python API Test'}


class Tests(unittest.TestCase):

    inited = False

    
    def test_hgmd(self):
        self.call(URL_HGMD,200,payload = {"genId":"POLD1"})


    def call(self, url, httpcode=200, payload = None, request_method=False):
        """GET or POST to server REST API"""

        func = request_method if request_method else s.post if payload != None else s.get
        r = func(URL_BASE + url, data = json.dumps(payload or {}),
                headers = headers)

        self.assertEqual(r.status_code, httpcode)
        if not r.status_code in (401, 405):
            return r.json()


if __name__ == '__main__':
    unittest.main()

