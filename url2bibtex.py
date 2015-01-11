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

def bibtex(urldata):
    """
    Create an array with all the data for the bibTex file.

    :param urldata: all the data collected
    :type urldata: dict
    :returns: list
    """
    bibtex = []
    bibtex.append('@ONLINE{' + urldata['url'].replace('.', '_') \
                  + ':' + urldata['year'] + ':Online')
    bibtex.append('\tauthor = {},')
    bibtex.append('\ttitle = {this is a test},')
    bibtex.append('\tmonth = jun,')
    bibtex.append('\tyear = {' + urldata['year'] + '},')
    bibtex.append('\turl = {' + urldata['url'] + '},')
    bibtex.append('\turldate = {' + urldata['urldate'] + '}')
    if 'snapshot url' in urldata.keys():
        bibtex[-1] += ','
        bibtex.append('\tnote = {Internet Archive Wayback Machine: \url{' \
                      + urldata['snapshot url'] + '}, as of ' \
                      + urldata['snapshot date'] + '}')
    bibtex.append('}')
    return bibtex

urldata = {'url': sys.argv[1],
           'urldate': str(datetime.date.today()),
           'year': str(datetime.date.today().year)}
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

for line in bibtex(urldata):
    print(line)
