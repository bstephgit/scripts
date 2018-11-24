import http.client as request
from argparse import ArgumentParser
from urllib.parse import urlparse
from lxml import html, etree
import re
import os
import time
from configparser import ConfigParser
import psutil

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException

import bookhelper.firefox
import bookhelper.chrome
import bookhelper.config
import bookhelper.apiway
import bookhelper.session
from bookhelper import ElementNames, FileTypes

class FormatException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

    def __str__(self):
        return "FormatException: " + Exception.__str__(self)


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


def extract_data(content):
    children = html.fromstring(content).xpath('.//div[@class="thecontent"]/child::*')
    title = ''
    author = ''
    year=''
    node = children[2]
    str = node.xpath('b/text()')
    if not str:
        msg = 'Error retrieving title/author in [%s]' % etree.tostring(node)
        raise FormatException(msg)
    str = str[0]
    regexp = re.compile(r'(.+) by (.+)')
    res = regexp.search(str)
    try:
        if res and len(res.groups()) == 2:
            title, author = res.groups()
            print(res.groups())
            print('Successfully got title/author title=[%s], author=[%s]' % (title, author))
        else:
            raise FormatException('Error retrieving title/author from string %s' % str)
    except FormatException:
        print('Error extracting from %s. String cannot be split to Title/Author. Assign to title.' % str)
        title=str

    str = node.xpath('text()')

    try:
        if not str:
            msg = 'Error retrieving year in [%s]' % str
            raise FormatException(msg)
    except FormatException:
        print('Error extracting year and description. Left year and description unassigned')

    str = str[0] if len(str[0]) > 4 else str[1]
    regexp = re.compile(r'.+\s+\|\s+(19[0-9]{2}|20[0,1][0-9])\s+\|')
    res = regexp.search(str)

    try:
        if not res:
            raise FormatException('Date not found in \'%s\'' % str)
        year = res.groups()[0]
        print('Date successfully retrieved %s' % year)
    except FormatException:
        print('Cannot extract date. Left unassingned.')

    descr = ''
    children = children[3:]
    for child in children:
        if child.tag == 'div':
            break
        descr += etree.tostring(child, encoding='UTF-8').replace(b'\n', b'').decode('utf-8')

    # print('description=%s',descr)

    return {ElementNames.TITLE: title.strip(), ElementNames.AUTHOR: author.strip(), ElementNames.YEAR: year, \
                ElementNames.DESCRIPTION: descr}


def postDataTobrowser(data):
    cfg = bookhelper.config.instance

    session=bookhelper.session.instance
    print('webdriver pid found=\'%s\'' % cfg.driver_pid)

    pid = cfg.browser_pid
    if pid and psutil.pid_exists(pid):
        p=psutil.Process(pid)
        if p.name()==cfg.browser_exe:
            cfg.module.on_running(cfg)

    #start browser
    webdriver = cfg.module.start(cfg)
    cfg.driver_pid=webdriver.service.process.pid

    session.browser_pid=bookhelper.session.get_browser_pid(cfg)
    bookhelper.session.write_session_file()

    def reset_text(element, text):
        element.send_keys(Keys.CONTROL + 'a')
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def handle_starting():
            webdriver.get('https://albertdupre.byethost13.com/books/home.php?upload=1')
            cfg.module.handle_alert(webdriver)

    handle_starting()
    wait = WebDriverWait(webdriver, 60)
    wait.until(EC.presence_of_element_located((By.NAME, 'title')))
    reset_text(webdriver.find_element_by_name(ElementNames.TITLE), data[ElementNames.TITLE])
    reset_text(webdriver.find_element_by_name(ElementNames.AUTHOR), data[ElementNames.AUTHOR])
    reset_text(webdriver.find_element_by_name(ElementNames.YEAR), data[ElementNames.YEAR])
    reset_text(webdriver.find_element_by_name(ElementNames.DESCRIPTION), data[ElementNames.DESCRIPTION])

    print('Browser capabilities', webdriver.capabilities)

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

def format_types_str(types):
    if types:
        if not type(types) is list:
            types = types.split(" ")

        root=list()
        current=root
        if FileTypes.ZIP in types:
            current.append(FileTypes.me.ZIP.name)
        elif FileTypes.RAR in types:
            current.append(FileTypes.me.RAR.name)

        if len(current) > 0:
            current=list()
            root.append(current)

        current.extend( [ t.name for t in [ FileTypes.me.EPUB,   \
                                            FileTypes.me.PDF,    \
                                            FileTypes.me.AZW3,   \
                                            FileTypes.me.MOBI,   \
                                            FileTypes.me.CODE  ] \
                          if t.value in types  ] )

        if len(root)>0:
            substr='%s Format' % root[0]
            if len(root)>1 and len(root[1])>0:
                substr += '('
                sep=''
                for subtypes in root[1]:
                    substr+=''.join([sep,subtypes])
                    sep='+'
                substr += ')'
            return '<h3>%s</h3><hr>' % substr

    return ''



def doMain():
    parser = ArgumentParser(prog="http-content")
    parser.add_argument("-f", "--file", help="file to read", required=True)
    parser.add_argument("-o", "--output", help="output file name", default="data.txt")
    parser.add_argument("-t","--types",help="file types",choices=['epub','pdf','azw3','mobi','rar','zip','code'],nargs='*')

    cmdargs = parser.parse_args()
    url = parseUrlLink(cmdargs.file)
    if len(url) > 0:
        try:
            content = get_http_content(url)
            data = extract_data(content)
            file_types=cmdargs.types if hasattr(cmdargs,"types") else None
            data[ ElementNames.DESCRIPTION ] = '<div class=\'scrollable\'>%s</div>' %  \
                                               (format_types_str(file_types) + data[ ElementNames.DESCRIPTION ])
            bookhelper.session.read_session_file()
            #postDataTobrowser(data)
            bookhelper.apiway.postDataTobrowser(data)
            bookhelper.session.write_session_file()
        except Exception as e:
            bookhelper.session.check_session_state()
            raise (e)


if __name__ == "__main__":
    doMain()

"""
    parser.add_argument("-r","--remote",help="remote folder source path", required=True)
    parser.add_argument("-l","--local",help="local destination path", required=True)
    parser.add_argument("-u","--user",help="ftp user", required=True)
    parser.add_argument("-p","--password",help="ftp password", required=True)
    parser.add_argument("-o","--override",help="force override folders/files")
    parser.add_argument("-g","--guessbyext",help="guess if folder or file with extension")
"""
"""
    try:
        print('trying open remote session url=\'%s\' id=\'%s\'...' % (session_url,session_id))
        browser=Remote(command_executor=session_url, desired_capabilities={})
        browser.session_id = session_id
    except Exception as e:
        print('\t...failed to open remote session with url=%s id=%s: %s' % (session_url, session_id, e))

        browser=None
"""
"""
    options = FirefoxOptions()
    options.set_capability("browserConnectionEnabled", True)
    options.set_capability("marionette",True)
    binary = FirefoxBinary()
    binary.add_command_line_options('--marionette')
    binary.add_command_line_options('--foreground')
"""

# with open(session_file_name, 'w+') as file:
#     print('save in file \'%s\' session url=\'%s\' id=\'%s\'' % (
#     session_file_name, browser.command_executor._url, browser.session_id))
#     file.writelines([browser.command_executor._url, '\n', browser.session_id])
