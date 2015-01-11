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

    p = {'url': stripSchema(url)}
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
    if 'title' in urldata.keys():
        bibtex.append('\ttitle = {' + urldata['title'] + '},')
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

def stripSchema(url):
    """
    Strip the schema from the given URL.

    :param url: URL to strip
    :type url: str
    :return: str
    """
    if 'https' == url[:5]:
        return url[8:]
    if 'http' == url[:4]:
        return url[7:]
    return url

def getTitle(url):
    """
    Get the title of a website.

    :param url: URL to query
    :type url: str
    :returns: str
    """
    from bs4 import BeautifulSoup

    try:
        r = requests.get(url)
    except requests.exceptions.MissingSchema:
        try:
            r = requests.get('http://' + url)
        except requests.exceptions.MissingSchema:
            try:
                r = requests.get('https://' + url)
            except requests.exceptions.MissingSchema:
                return ''
    if 200 != r.status_code:
        return ''
    soup = BeautifulSoup(r.text)
    t = soup.find_all("title")
    if 1 != len(t):
        return ''
    return str(t[0]).replace('<title>', '').replace('</title>', '')

testurl = sys.argv[1]
if 'http' != testurl[:4]:
    print("did you forget 'http(s)'?")
    sys.exit(3)

urldata = {'url': testurl,
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

title = getTitle(urldata['url'])
if 0 != len(title):
    urldata['title'] = title

for line in bibtex(urldata):
    print(line)
