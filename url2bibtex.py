#!/usr/bin/env python

import requests
import sys
import datetime

def getWaybackData(url):
    """
    Get data from the wayback machine at archive.org
    if feasible.

    :param url: URL to check
    :type url: str
    :returns: dict
    """
    if 0 == len(url):
        return {}

    p = {'url': url}
    r = requests.get('https://archive.org/wayback/available', params=p)
    if 200 == r.status_code:
        wb = r.json()
        try:
            wb = wb['archived_snapshots']
            if 0 == len(wb):
                return {}
            wb = wb['closest']
            if not wb['available']:
                return {}
            if '200' != wb['status']:
                return {}
            return {
                'url': wb['url'],
                'timestamp': wb['timestamp']
            }
        except KeyError:
            return {}
    return {}

urldata = {'urldate': str(datetime.date.today()), 'year': str(datetime.date.today().year)}
wbdata = getWaybackData(sys.argv[1])
if 0 != len(wbdata):
    # create ISO timestamp string
    datestring = wbdata['timestamp'][:4] \
                 + '-' + wbdata['timestamp'][4:6] \
                 + '-' + wbdata['timestamp'][6:8] \
                 + 'T' + wbdata['timestamp'][8:10] \
                 + ':' + wbdata['timestamp'][10:12] \
                 + ':' + wbdata['timestamp'][12:14]
    urldata['snapshot date'] = datestring
    urldata['snapshot url'] = wbdata['url']
print(urldata)
"""
@ONLINE{bla_foo:2023:Online,
author = {Doe, John},
title = {this is a test},
month = jun,
year = {2023},
url = {http://www.bla.foo},
urldate = {2023-05-42}
note = {Internet Archive Wayback Machine: \url{urldata['snapshot url']}, as of urldata['snapshot date']}
}
"""
