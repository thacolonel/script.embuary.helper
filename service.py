# coding: utf-8

#################################################################################################

from resources.lib.helper import *
from resources.lib.service_monitor import *

#################################################################################################

if __name__ == "__main__":
    ''' Kodi startup tasks
    '''
    sync_library_tags()
    addon_data_cleanup()
    check_simplecache()

    ''' Start service
    '''
    Service()