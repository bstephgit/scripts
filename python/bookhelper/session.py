import os
import psutil
import json
import enum
from bookhelper import Singleton,enumadapter

SESSION_FILE_NAME = 'selenium_browser_session.txt'

@enumadapter
class SessionFields(enum.Enum):
    DRIVER_PID  = 'driver_pid'
    BROWSER_PID = 'browser_pid'
    PARAMS = 'params'
    VALUE = 'value'
    SESSION_ID = "sessionId"
    ELEMENT = "element"
    ELEMENT_ID  = "element_id"
    ERROR = 'error'


class Session(object):
    def __init__(self,*args,**kwargs):
        self._driver_pid = None
        self._browser_pid = None
        self._session_params = dict()
    @property
    def driver_pid(self):
        return self._driver_pid
    @driver_pid.setter
    def driver_pid(self,val):
        self._driver_pid = None if not val or not str(val).isdigit() else int(val)
    @property
    def browser_pid(self):
        return self._browser_pid
    @browser_pid.setter
    def browser_pid(self,val):
        self._browser_pid = None if not val or not str(val).isdigit() else int(val)
    @property
    def params(self):
        return self._session_params
    @params.setter
    def params(self,params):
        self._session_params = params
    @property
    def session_id(self):
        p=self._session_params
        val_tag = SessionFields.VALUE
        sid_tag = SessionFields.SESSION_ID
        if p and val_tag in p and sid_tag in p[val_tag]:
            return p[val_tag][sid_tag]
        return None

SESSION_SINGLETON = Session()

# aliasing for better syntax
module_property = Session

@module_property
def instance():
    return globals()['SESSION_SINGLETON']

def read_session_file():
    session = instance
    print('loading session file...(session=%s)' % str(session))

    if os.path.exists(SESSION_FILE_NAME):
        with open(SESSION_FILE_NAME, 'r') as file:
            try:
                session_obj = json.load(file)
                if SessionFields.DRIVER_PID in session_obj:
                    session.driver_pid = session_obj[SessionFields.DRIVER_PID]
                    print('\tloading driver_pid=%d' % session.driver_pid)
                if SessionFields.BROWSER_PID in session_obj:
                    session.browser_pid = session_obj[SessionFields.BROWSER_PID]
                    print('\tloading browser_pid=%d' % session.browser_pid)
                if SessionFields.PARAMS in session_obj:
                    session.params.update(session_obj[SessionFields.PARAMS])
                    print('\tloading session params=%s' % str(session.params))
            except:
                session.browser_pid = session.driver_pid = None
                print('\tWarning: Bad format while reading session file => setting browser_pid and driver_pid reset to none')

def write_session_file():
    print('saving session file...')
    with open(SESSION_FILE_NAME, 'w+') as file:
        import bookhelper
        from bookhelper.config import  instance as cfg, CONFIG_ITEMS as cfg_items
        obj = dict()
        print('\tsaving session name=%s' % cfg.name)
        obj[cfg_items.NAME] = cfg.name
        print('\tsaving session driver_pid=%s' % instance.driver_pid)
        obj[SessionFields.DRIVER_PID] = instance.driver_pid
        if not instance.browser_pid or not psutil.pid_exists(instance.browser_pid):
            get_browser_pid(cfg)
        print('\tsaving session browser_pid=%s' % instance.browser_pid)
        obj[SessionFields.BROWSER_PID] = instance.browser_pid
        print('\tsaving extra session params=%s' % instance.params)
        obj[SessionFields.PARAMS] = instance.params
        json.dump(obj,file)

def check_session_state():
    print('Error occured => check consistent data to save in session file')
    with open(SESSION_FILE_NAME, 'w+') as file:
        session=instance
        from bookhelper.config import instance as cfg
        #cannot recover if session ID is lost
        if session.session_id is None:
            session.params = session.driver_pid = session.browser_pid = None
            for exe_name in [cfg.driver_exe,cfg.browser_exe]:
                for p in get_running_processes_by_name(exe_name):
                    if has_opened_port(p,cfg.driver_port):
                        try:
                            print("\tkill <%s> pid=%d" % (exe_name,p.pid))
                            p.terminate()
                            p.wait(5)
                        except psutil.TimeoutExpired as e:
                            print('Error killing <%s> process. timeout expired', exe_name)
        else:
            write_session_file()

def get_browser_pid(cfg):
    from bookhelper.session import instance as session
    p = psutil.Process( session.driver_pid )
    port = cfg.browser_port
    plist = p.children(recursive=True)
    for p in plist:
        for con in p.connections():
            if con.laddr.port == port:
                print("found process \'%s\' with port %d opened: pid=%d saved" % (
                p.name(), port, p.pid))
                session.browser_pid = p.pid
                return p.pid
    raise Exception('Session pid not found for port=%d' % port)

def get_running_processes_by_name(name):
    for p in psutil.process_iter():
        if p.name()==name:
            yield p
def has_opened_port(process_obj,port):
    for con in process_obj.connections():
        if con.laddr.port == port:
            return True
    return False
