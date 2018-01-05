# url2bibtex
Create a [bibtex](https://en.wikipedia.org/wiki/BibTeX) entry for a given
[URL](https://en.wikipedia.org/wiki/Uniform_resource_locator). It also
applies some magic for more persistent citations where possible.

usage:
```
$ ./url2bibtex.py http://www.github.com/
@ONLINE{www_github_com:2015:Online
	author = {},
	title = {GitHub · Build software better, together.},
	month = jun,
	year = {2015},
	url = {http://www.github.com/},
	urldate = {2015-01-11},
	note = {Internet Archive Wayback Machine: \url{http://web.archive.org/web/20150111022818/https://github.com}, as of 2015-01-11T02:28:18}
}
```

```
$ ./url2bibtex.py --file=links.txt > bibliography.bib
```

# references
* [BibTeX: How to cite a website](http://nschloe.blogspot.de/2009/06/bibtex-how-to-cite-website_21.html)
* [Requests: HTTP for Humans](http://docs.python-requests.org/en/latest/)
* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
* [Wayback Machine APIs](https://archive.org/help/wayback_api.php)
