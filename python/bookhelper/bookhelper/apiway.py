import bookhelper
import bookhelper.session
from bookhelper.session import SessionFields, Session
import bookhelper.config
from bookhelper import *

import subprocess
import psutil
import json
import http.client as request
import time
import traceback

host = 'localhost'

def check_error(data):
    if not data:
        return
    if type(data) is bytes:
        data = data.decode()
    if type(data) is str:
        try:
            data=json.loads(data)
        except:
            print("WARNING: cannot find error in string %s" % data)
            return
    if not type(data) is dict:
        print("WARNING: cannot find error in unknown data type=<%s> content=%s" % (str(type(data)),str(data)) )
    if SessionFields.VALUE in data:
        data = data[SessionFields.VALUE]
    if data and SessionFields.ERROR in data:
        raise Exception(str(data[SessionFields.ERROR]))


def json_loads(data):
    data_str = ''
    if type(data) is bytes:
        data_str = data.decode('utf-8')
    else:
        data_str = data
    return json.loads(data_str) 

         
def send_request(meth='GET',host='localhost',port=80,payload=None,path='/',headers={}):
    response_data=None
    err=None
    try:
        req = request.HTTPConnection(host, port=port)
        req.request(meth, path, body=payload,headers=headers)
        with req.getresponse() as rp:
            response_data = rp.read()
    except Exception as e:
        err = e
    finally:
        if not req is None:
            req.close()
    if not err is None:
        raise err
    return response_data


def postDataTobrowser(book_data):
    cfg = bookhelper.config.instance
    session=bookhelper.session.instance
    port = cfg.driver_port

    print('postDataTobrowser (session=%s)' % str(session))
    print('Search running DRIVER instance exe=%s, port=%d...(session file pid=%d)' % (cfg.driver_exe,cfg.driver_port,session.driver_pid if session.driver_pid else 0))
    running_driver=False
    if session.driver_pid and psutil.pid_exists(session.driver_pid):
        driver_process = psutil.Process(session.driver_pid)
        if driver_process.name() == cfg.driver_exe and bookhelper.session.has_opened_port(driver_process,cfg.driver_port):
            print('\tRunning DRIVER [%s] instance found from session file: pid=%d' % (cfg.driver_exe,session.driver_pid))
            running_driver = True
    if not running_driver :
        session.driver_pid=None
        #search running driver with right port opened
        for p in bookhelper.session.get_running_processes_by_name(cfg.driver_exe):
            running_driver = bookhelper.session.has_opened_port(p,cfg.driver_port)
            if running_driver:
                session.driver_pid=p.pid
                print("\t<%s> DRIVER running process (pid=%d) found with port %d by iterating running processes" % (
                cfg.driver_exe, session.driver_pid, cfg.driver_port))
                break
        if not running_driver:
            args = [cfg.driver_exe]
            args.extend(cfg.driver_args)

            driver_process = subprocess.Popen(args,shell=False,stdout=open( cfg.log_file ,'w+') )
            session.driver_pid = driver_process.pid
            print("\tNo running instance found. Create new DRIVER instance pid=(%d,%d)" % (session.driver_pid,driver_process.pid))

    print('Search running BROWSER instance exe=%s, port=%d...(session file pid=%d)' % (cfg.browser_exe,cfg.browser_port,session.browser_pid if session.browser_pid else 0))
    running_browser=False
    if  session.browser_pid and psutil.pid_exists(session.browser_pid):
        bp = psutil.Process(session.browser_pid)
        if bp.name() == cfg.browser_exe:
            running_browser=True
            print('\tRunning BROWSER [%s] instance found from session file: pid=%d' % (cfg.browser_exe, session.browser_pid))

    if not running_browser:
        session.browser_pid = None
        for p in bookhelper.session.get_running_processes_by_name(cfg.browser_exe):
            if bookhelper.session.has_opened_port(p,cfg.browser_port):
                session.browser_pid=p.pid
                print('\tRunning BROWSER [%s] instance found by iteration: pid=%d' % (cfg.browser_exe,session.browser_pid ))
                running_browser=True

    if running_browser:
        if not session.session_id or len(session.session_id)==0:
            print("\tBrowser is running but session ID lost: kill browser process")
            psutil.Process(session.browser_pid).kill()
            running_browser = False
        else:
            cfg.module.on_running(cfg)
    else:
        print('No running BROWSER found')

    
    if not running_browser:
        print('Create new session...')
        payload = '{"capabilities": {"alwaysMatch": {"acceptInsecureCerts": true, "unhandledPromptBehavior": "ignore"} }}'
        r = send_request(meth='POST',host=host,port=port,path='/session',payload=payload)
        http_resp=json_loads(r)
        if  SessionFields.Value in http_resp and SessionFields.Error in http_resp[SessionFields.VALUE]:
            raise Exception('Error while creating new session:', str(http_resp[SessionFields.VALUE][SessionFields.ERROR]))
        else:
            session.params.update(http_resp)
            print('\tSession successfully created (id=%s)' % session.session_id)

    session_id = session.session_id
    #session_id = session.params['value']['sessionId']
    if not session_id or len(session_id)==0:
        raise Exception("ERROR: session id is NULL")

    print('Session ID=%s' % session_id)

    payload = '{"url":"https://albertdupre.byethost13.com/books/home.php?upload=1"}'
    path='/session/%s/url' % session_id
    r = send_request(meth='POST',host=host,port=port,path=path,payload=payload)
    check_error(r)

    by='css selector'
    query='[name="%s"]'
    max=60
    while max>0:
        try:
            rep = get_element(session, (by, query % ElementNames.TITLE))
            print('waiting display of element got:', str(rep))
            if rep and len(rep)>0:
                for k in rep.keys():
                    if k.index(SessionFields.ELEMENT)==0:
                        max=-2
        except Exception as e:
            print('Exception trying loading page:',str(e))
        finally:
            time.sleep(1)
            max-=1
    if max==0:
        print('timeout and page not loaded => exit')
        return
    try:
        set_elem_text(session, (by, query % ElementNames.TITLE), book_data[ElementNames.TITLE])
        set_elem_text(session, (by, query % ElementNames.AUTHOR), book_data[ElementNames.AUTHOR])
        set_elem_text(session, (by, query % ElementNames.YEAR), book_data[ElementNames.YEAR])
        clear_elem_text(session, (by, query % ElementNames.DESCRIPTION))
        set_elem_text(session, (by, query % ElementNames.DESCRIPTION), book_data[ElementNames.DESCRIPTION])
    except Exception as e:
        traceback.print_exc()


def get_element(session, elem,subitem=None):
    print('get_element',elem,subitem)
    # curl -X POST http://127.0.0.1:4444/wd/hub/session/$s_id/element -d '{"using":"id","value":"gbqfb"}'
    # {"sessionId":"...","status":0,"value":{"ELEMENT":"element-object-id-here"}}
    cfg = bookhelper.config.instance
    payload = {"using": elem[0], "value": elem[1]}
    payload = json.dumps(payload)

    pl = send_request(meth='POST',port=cfg.driver_port,payload=payload,path=('/session/%s/element' % session.session_id))

    #print(pl)
    if not pl:
        raise Exception('No payload returned from request element %s' % str(elem))

    pl = json_loads(pl)

    val_tag=SessionFields.VALUE
    elem_tag=SessionFields.ELEMENT
    error_tag = SessionFields.ERROR
    if val_tag in pl:
        if error_tag in pl[val_tag]:
            raise Exception('Error get_elem %s: %s' % (elem,pl[val_tag][error_tag]))
        if subitem==SessionFields.ELEMENT_ID:
            for k in pl[val_tag].keys():
                if k.index(SessionFields.ELEMENT)==0:
                    return pl[val_tag][k]
        return pl[val_tag]
    return pl

def set_elem_text(session, elem, val):
    print('set_element',elem,val)
#curl - X POST http://127.0.0.1: 4444/wd/hub/session/$s_id/element/0/value - d {"text": "selenium"}
    cfg = bookhelper.config.instance
    elem_id=get_element(session,elem,subitem=SessionFields.ELEMENT_ID)
    payload=None
    if type(val) is str:
        payload = json.dumps({"text": val })
    elif type(val) is list:
        payload = json.dumps({"value": val})

    r = send_request(meth='POST', port=cfg.driver_port,path='/session/%s/element/%s/value' % (session.session_id,elem_id), payload=payload, headers={"Content-Type": "text/html; charset=utf-8"})
    check_error(r)

def clear_elem_text(session,elem):
# curl - X POST http://127.0.0.1: 4444/wd/hub/session/$s_id/element/$elem_id/clear - d {}
    cfg = bookhelper.config.instance
    elem_id = get_element(session, elem, subitem=SessionFields.ELEMENT_ID)
    r = send_request(meth='POST', port=cfg.driver_port, payload="{}", path=('/session/%s/element/%s/clear' % (session.session_id,elem_id)))
    check_error( r )

def close_session(session):
    from bookhelper.config import instance as cfg
    sid = session.session_id
    r = send_request(meth='DELETE', path='/session/%s' % sid, port=cfg.driver_port)
    print('session %s closed: %s' % (sid, r))
