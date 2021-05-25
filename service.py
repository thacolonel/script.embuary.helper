# coding: utf-8

#################################################################################################

from resources.lib.helper import addon_data_cleanup, sync_library_tags
from resources.lib.service_monitor import Service

#################################################################################################

if __name__ == "__main__":
    ''' Kodi startup tasks
    '''
    sync_library_tags()
    addon_data_cleanup()

    ''' Start service
    '''
    Service()