#!/usr/bin/env python3

import http.client as request
from urllib.parse import urlparse
from configparser import ConfigParser

def parseUrlLink(url_link_file):
    config = ConfigParser()
    config.read(url_link_file)
    section_name = 'InternetShortcut'
    if section_name in config:
        url_tag = 'URL'
        if url_tag in config[section_name]:
            url = config[section_name][url_tag]
            return url
        else:
            raise Exception('%s entry not found in [%s] section (file %s)' % (url_tag, section_name, url_link_file))
    else:
        raise Exception('[%s] section not in URL shortcut file (%s).' % (section_name, url_link_file))

def get_http_content(url):
    r = None
    content = None
    try:
        urlobj = urlparse(url)
        scheme = urlobj.scheme
        req = None
        if scheme == 'https':
            req = request.HTTPSConnection(urlobj.netloc)
        else:
            req = request.HTTPConnection(url.netloc)
        path = urlobj.path
        if len(urlobj.query) > 0:
            path += '?' + urlobj.query
        req.putrequest('GET', path)
        req.endheaders()
        r = req.getresponse()
    except Exception as e:
        print(e)
    else:
        content = r.read()
    return content

def get_host(url):
    return urlparse(url).netloc
