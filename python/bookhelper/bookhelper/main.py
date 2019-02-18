from argparse import ArgumentParser
import psutil

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium.common.exceptions import UnexpectedAlertPresentException

import bookhelper.firefox
import bookhelper.chrome
import bookhelper.config
import bookhelper.apiway
import bookhelper.session
from bookhelper import ElementNames, FileTypes
from bookhelper.sites import extract_data


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

    try:
        data = extract_data(cmdargs.file)
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
