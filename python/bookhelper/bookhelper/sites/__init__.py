#!/usr/bin/env python3
from . import http_request as hr
import importlib
import sys

name = 'sites'

sites_modules = { 'coderprog.com': 'coderprog', 'sanet.st' : 'sanet' }

def extract_data(url_link):

    url = hr.parseUrlLink(url_link)
    host = hr.get_host(url)
    if host in sites_modules:
        mod = importlib.import_module('bookhelper.sites.%s' % sites_modules[host])
        if mod:
            return mod.extract_data(hr.get_http_content(url))
        else:
            raise Exception('cannot load site module %s' % sites_modules[host])
    else:
        raise Exception("module for site %s not found" % host)


