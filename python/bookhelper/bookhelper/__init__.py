import enum

FIREFOX_CFG=0
CHROME_CFG=1

SELECTED_CONFIG=FIREFOX_CFG

class Singleton(object):
    def __init__(self,instance):
        setattr(self,'_inst', instance)
    def __getattr__(self, item):
        item = getattr( self._inst(),item )
        return item

def enumadapter(enum):
    class enum_value:
        def __init__(self):
            self._en = enum
        def __getattr__(self, item):
            if item in self._en.__members__.keys():
                return self._en[item].value
            if hasattr(self._en,item):
                return getattr(self._en,item)
            if str(item) == 'me':
                return self._en
            if str(item) == 'members':
                return self._en.__members__
            return None
    return enum_value()

@enumadapter
class ElementNames(enum.Enum):
    TITLE='title'
    AUTHOR='author'
    YEAR='year'
    DESCRIPTION='descr'

@enumadapter
class FileTypes(enum.Enum):
    EPUB = 'epub'
    PDF  = 'pdf'
    MOBI = 'mobi'
    AZW3 = 'azw3'
    RAR  = 'rar'
    ZIP  = 'zip'
    CODE = 'code'

class FormatException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

    def __str__(self):
        return "FormatException: " + Exception.__str__(self)

from .main import doMain
