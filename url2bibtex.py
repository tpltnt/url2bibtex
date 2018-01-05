#!/usr/bin/env python

import requests
import sys
import datetime
import argparse
import re
import traceback

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

    p = {'url': stripSchema(url), 'verify': False}
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

def getWikipediaData(url):
    """
    Get data from the wikipedia if applicable.

    :param url: URL to check
    :type url: str
    :returns: dict
    """
    from bs4 import BeautifulSoup

    if 0 == len(url):
        return {}
    r = requests.get(url, verify=False)
    if 200 == r.status_code:
        soup = BeautifulSoup(r.text, 'html.parser')
        quotepath = ''
        historpath = ''
        for a in soup.find_all("a"):
            if 'href' in a.attrs:
                if '/w/index.php?title=Special:CiteThisPage' == a['href'][:39]:
                    quotepath = a['href']
                if '&action=history' == a['href'][-15:]:
                    historypath = a['href']

        chunks = r.url.split('/')
        citeurl = chunks[0] + '//' + chunks[2] + quotepath
        citeurl = citeurl.replace('Special:CiteThisPage&page=', '')
        citeurl = citeurl.replace('&id=', '&oldid=')
        chunks = r.url.split('/')
        historyurl = chunks[0] + '//' + chunks[2] + historypath

        year = ''
        r = requests.get(historyurl, verify=False)
        if 200 == r.status_code:
            soup = BeautifulSoup(r.text, 'html.parser')
            hdate = soup.find("a", class_='mw-changeslist-date')
            year = str(hdate).split('">')[1].split(' ')[3][:4]
        return {'url': citeurl, 'author': 'Wikipedia', 'year': year}
    return {}

def bibtex(urldata):
    """
    Create an array with all the data for the bibTex file.

    :param urldata: all the data collected
    :type urldata: dict
    :returns: list
    """
    bibtex = []
    url = stripSchema(urldata['url']).replace('.', '_')
    if '/' == url[-1]:
        url = url[:-1]
#    link_id = re.sub(r'[\[\]{}:\'",. |-]', '_', urldata['title'])
    if 'title' not in urldata:
        title = url
    else:
        title = urldata['title']
    link_id = re.sub(r'[^a-zA-Z0-9]', '_', title)
    link_id = re.sub(r'_+', '_', link_id)

    bibtex.append('@ONLINE{' + link_id + ':' + urldata['year'] + ':Online' + ',')
    bibtex.append('\tauthor = {},')
    title_filtered = re.sub(r'[^a-zA-Z0-9]', ' ', title)
    title_filtered = re.sub(r'\s+', ' ', title_filtered)
#    if 'title' in urldata.keys():
    bibtex.append('\ttitle = {' + title_filtered + '},')
    bibtex.append('\tmonth = jun,')
    bibtex.append('\tyear = {' + urldata['year'] + '},')
    bibtex.append('\turl = {' + urldata['url'] + '},')
    bibtex.append('\turldate = {' + urldata['urldate'] + '}')
    if 'snapshot url' in urldata.keys():
        bibtex[-1] += ','
        bibtex.append('\tnote = {Internet Archive Wayback Machine: \\url{' \
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
        r = requests.get(url, verify=False)
    except requests.exceptions.MissingSchema:
        try:
            r = requests.get('http://' + url)
        except requests.exceptions.MissingSchema:
            try:
                r = requests.get('https://' + url, verify=False)
            except requests.exceptions.MissingSchema:
                return ''
    if 200 != r.status_code:
        return ''
    soup = BeautifulSoup(r.text, 'html.parser')
    t = soup.find_all("title")
    if 1 == len(t):
        return str(t[0]).replace('<title>', '').replace('</title>', '')
    soup.find_all("p", "title")
    if 1 == len(t):
        return str(t[0]).replace('<p class="title">', '').replace('</p>', '')
    return ''


parser = argparse.ArgumentParser()
parser.add_argument('--file', help='Read urls from file', type=str)
parser.add_argument('url', type=str, nargs='?')
args = parser.parse_args()


def get_urldata(testurl):
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

    if -1 != urldata['url'].find('wikipedia.org'):
        wpdata = getWikipediaData(urldata['url'])
        urldata['author'] = wpdata['author']
        urldata['url'] = wpdata['url']
        urldata['year'] = wpdata['year']

    title = getTitle(urldata['url'])
    if 0 != len(title):
        urldata['title'] = title.replace(',', '{,}')

    return urldata


if __name__ == '__main__':
    if args.url:
        if 'http' != args.url[:4]:
            print("did you forget 'http(s)'?")
            sys.exit(3)
        for line in bibtex(get_urldata(args.url)):
            print(line)

    elif args.file:
        with open(args.file) as urls:
            for url in urls.readlines():
                url_clean = url.strip()
                print(f'{url_clean}', file=sys.stderr)
                try:
                    for line in bibtex(get_urldata(url_clean)):
                        print(line)
                    print()
                except Exception as e:
                    print(f'Error: {str(e)}', file=sys.stderr)
                    traceback.print_exc()

