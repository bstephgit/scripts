import enum
import sys
from bookhelper import *
import bookhelper
import os


@enumadapter
class CONFIG_ITEMS(enum.Enum):
    NAME='name'
    BROWSER_EXE= "browser_exe"
    DRIVER_EXE="driver_exe"
    MODULE="module"
    DRIVER_PORT="driver_port"
    DRIVER_ARGS="driver_args"
    BROWSER_PORT = "browser_port"
    LOG_FILE = "log_file"

MARIONETTE_PORT=9876
CHROME_BROWSER_PORT=7654

if os.name == 'posix':
    print('Linux/Unix/MacOS detected')

    supported_browsers_configs = [
        {CONFIG_ITEMS.NAME: "firefox", CONFIG_ITEMS.BROWSER_EXE: "firefox", CONFIG_ITEMS.DRIVER_EXE: "geckodriver", CONFIG_ITEMS.MODULE: bookhelper.firefox, \
            CONFIG_ITEMS.DRIVER_PORT: 25234, CONFIG_ITEMS.BROWSER_PORT: MARIONETTE_PORT, CONFIG_ITEMS.DRIVER_ARGS: [], CONFIG_ITEMS.LOG_FILE: "geckodriver.log"},
        {CONFIG_ITEMS.NAME: "chrome", CONFIG_ITEMS.BROWSER_EXE: "chrome", CONFIG_ITEMS.DRIVER_EXE: "chromedriver", CONFIG_ITEMS.MODULE: bookhelper.chrome, \
            CONFIG_ITEMS.DRIVER_PORT: 25134, CONFIG_ITEMS.BROWSER_PORT: CHROME_BROWSER_PORT, CONFIG_ITEMS.DRIVER_ARGS: [], CONFIG_ITEMS.LOG_FILE: "chromedriver.log"}]
else:
    print(os.name, 'Windows os')
    supported_browsers_configs = [
        {CONFIG_ITEMS.NAME: "firefox", CONFIG_ITEMS.BROWSER_EXE: "firefox.exe", CONFIG_ITEMS.DRIVER_EXE: "geckodriver.exe", CONFIG_ITEMS.MODULE: bookhelper.firefox, \
            CONFIG_ITEMS.DRIVER_PORT: 15234, CONFIG_ITEMS.BROWSER_PORT: MARIONETTE_PORT, CONFIG_ITEMS.DRIVER_ARGS: [], CONFIG_ITEMS.LOG_FILE: "geckodriver.log"},
        {CONFIG_ITEMS.NAME: "chrome", CONFIG_ITEMS.BROWSER_EXE: "chrome.exe", CONFIG_ITEMS.DRIVER_EXE: "chromedriver.exe", CONFIG_ITEMS.MODULE: bookhelper.chrome, \
            CONFIG_ITEMS.DRIVER_PORT: 25134, CONFIG_ITEMS.BROWSER_PORT: CHROME_BROWSER_PORT, CONFIG_ITEMS.DRIVER_ARGS: [], CONFIG_ITEMS.LOG_FILE: "chromedriver.log"}]

def init():
    cfg = supported_browsers_configs[FIREFOX_CFG]
    cfg[CONFIG_ITEMS.DRIVER_ARGS].extend(  ["--port=%d" % cfg[CONFIG_ITEMS.DRIVER_PORT], "--log=debug", "--marionette-port=%d" % MARIONETTE_PORT])
    cfg = supported_browsers_configs[CHROME_CFG]
    cfg[CONFIG_ITEMS.DRIVER_ARGS].extend(["--port=%d" % cfg[CONFIG_ITEMS.DRIVER_PORT], "--log-level=ALL"])

class Config(object):
    def __init__(self,cfg):
        if not cfg:
            raise "Error %: Configuration dictionary is None" % (__file__,)
        self._cfg=cfg

    @property
    def name(self):
        return self._cfg[CONFIG_ITEMS.NAME]

    @property
    def browser_exe(self):
        return self._cfg[CONFIG_ITEMS.BROWSER_EXE]

    @property
    def driver_exe(self):
        return self._cfg[CONFIG_ITEMS.DRIVER_EXE]

    @property
    def module(self):
        return self._cfg[CONFIG_ITEMS.MODULE]

    def get_driver_port(self):
        return self._cfg[CONFIG_ITEMS.DRIVER_PORT]
    def set_driver_port(self,port):
        if str(port).isdigit():
            self._cfg[CONFIG_ITEMS.DRIVER_PORT] = int(port)
    driver_port = property(get_driver_port,set_driver_port)

    def get_driver_pid(self):
        return self._driver_pid
    def set_driver_pid(self,pid):
        self._driver_pid = int(pid)
    driver_pid=property(get_driver_pid,set_driver_pid)

    def get_browser_port(self):
        return self._cfg[CONFIG_ITEMS.BROWSER_PORT]
    def set_browser_port(self,port):
        if str(port).isdigit():
            self._cfg[CONFIG_ITEMS.BROWSER_PORT] = int(port)
    browser_port = property(get_browser_port,set_browser_port)

    def get_browser_pid(self):
        return self._browser_pid
    def set_browser_pid(self,pid):
        self._browser_pid = int(pid)
    browser_pid=property(get_browser_pid,set_browser_pid)

    @property
    def driver_args(self):
        if CONFIG_ITEMS.DRIVER_ARGS in self._cfg:
            return self._cfg[CONFIG_ITEMS.DRIVER_ARGS]
        return None

    @property
    def log_file(self):
        return self._cfg[CONFIG_ITEMS.LOG_FILE]

CONFIG_SINGLETON=None

def create_config(config):
    this_mod=sys.modules[__name__]
    init()
    if config in [FIREFOX_CFG,CHROME_CFG]:
        if not this_mod.CONFIG_SINGLETON:
            this_mod.CONFIG_SINGLETON = Config(supported_browsers_configs[config])

    return this_mod.CONFIG_SINGLETON

create_config(bookhelper.SELECTED_CONFIG)

module_property=bookhelper.Singleton

@module_property
def instance():
    return globals()['CONFIG_SINGLETON']


