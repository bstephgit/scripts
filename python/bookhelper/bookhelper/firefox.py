import os
import psutil
import bookhelper.session

from configparser import ConfigParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from bookhelper import *
from selenium.webdriver import Firefox, FirefoxProfile, Remote, FirefoxOptions, DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def start(cfg):
# https://support.mozilla.org/en-US/kb/profile-manager-create-and-remove-firefox-profiles#w_starting-the-profile-manager
    # more Simple: FirefoxProfile myprofile = profile.getProfile("Selenium_Bookstore");
    ff_profile_path = os.path.join(os.environ['appdata'], 'Mozilla', 'Firefox')
    inifile = os.path.join(os.environ['appdata'], 'Mozilla', 'Firefox', 'profiles.ini')

    session = bookhelper.session.instance

    if os.path.exists(inifile):
        config = ConfigParser()
        config.read(inifile)
        name_tag = 'Name'
        for section in config.sections():
            if section.startswith('Profile') and config[section][name_tag] == 'Selenium_Bookstore':
                path_tag = 'Path'
                if path_tag in config[section]:
                    ff_profile_path = os.path.join(ff_profile_path, config[section][path_tag])

    print('profile path', ff_profile_path)
    profile = FirefoxProfile(ff_profile_path)
    profile.accept_untrusted_certs = True
    profile.assume_untrusted_cert_issuer = True
    profile.native_events_enabled = True

    cfg.driver_args.extend(['--marionette-port=%d' % cfg.driver_port, '--log=debug'])
    print('launching firefox webdriver pid=%s, args=%s' % (session.driver_pid, cfg.driver_args))
    caps = DesiredCapabilities().FIREFOX.copy()
    caps['acceptSslCerts'] = True
    caps['acceptInsecureCerts'] = True
    webdriver = Firefox(firefox_profile=profile, service_args=cfg.driver_args,capabilities=caps)
    return webdriver;

def on_running(cfg):
    print('running version found \'%s\' (pid=%d) add marionette \'--connect-existing\' argument' % (cfg.browser_exe, bookhelper.session.instance.browser_pid))
    cfg.driver_args.append('--connect-existing')

def handle_alert(browser):
    try:
        wait1 = WebDriverWait(browser, 10)
        wait1.until(EC.alert_is_present())
        alert = browser.switch_to.alert
        alert.send_keys('b13_17778490')
        alert.send_keys(Keys.TAB + 'tecste1')
        alert.send_keys(Keys.TAB )
        alert.send_keys('b13_17778490')
        alert.accept()

        wait2 = WebDriverWait(browser,10)
        wait2.until_not(EC.alert_is_present())
        browser.switch_to.default_content()
    except:
        print('Error handle_alert')
