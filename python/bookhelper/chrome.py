#from optparse import Option
import os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import bookhelper
import bookhelper.session


CHROME_SERVICE='chrome_service'

class ChromeService(Service):
    def __init__(self,driver_path,port,log):
        Service.__init__(self,driver_path, port=port, log_path=log)
    def send_remote_shutdown_command(self):
        pass

def start(cfg):
    session=bookhelper.session.instance
    pid = session.driver_pid
    if not pid or pid==0:
        session.driver_pid=start_service(cfg)
    #webdriver = Chrome(executable_path=r"chromedriver.exe",port=cfg[DRIVER_PORT], service_log_path=r'%s\chromedriver.log.txt' % bookhelper_path,options=opt)
    import selenium
    webdriver = selenium.webdriver.Remote('http://127.0.0.1:%s' % cfg.browser_port)
    return webdriver

def on_running(driver_pid):
    if not driver_pid or driver_pid == 0:
        raise Exception('driver PID is not valid(%s)' % bookhelper.session.instance.driver_pid)

def start_service(cfg):
    bookhelper_path=bookhelper.__path__[0]
    service = ChromeService(os.path.join(bookhelper_path,'chromedriver.exe'),cfg.driver_port,os.path.join(bookhelper_path,'chromedriver.log') )
    service.start()
    return service

def handle_alert(browser):
    try:
        print('handle_alert: start')
        wait = WebDriverWait(browser, 10)
        wait.until(EC.alert_is_present())
        print('handle_alert: switch to alert')
        alert = browser.switch_to.alert
        alert.send_keys('b13_17778490')
        alert.send_keys(Keys.TAB + 'tecste1')
        print('handle_alert: accept')
        alert.accept()

        wait = WebDriverWait(browser,10)
        wait.until_not(EC.alert_is_present())
        print('handle_alert: switch to default content')

        browser.switch_to.default_content()
    except Exception as e:
        print('Error handle_alert: %s' % repr(e))
