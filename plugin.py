#!/usr/bin/python

########################
import sys
import xbmcplugin
import pickle
import threading
import urllib.parse as urlparse
from resources.lib.plugin_listing import *
from resources.lib.plugin_content import *
from resources.lib.plugin_actions import *
from resources.lib.utils import get_pickle, save_pickle

########################




class Main:
    def __init__(self):
        self._parse_argv()
        self.info = self.params.get('info')
        self.action = self.params.get('action')
        if self.info:
            self.getinfos()
        elif self.action:
            self.actions()
        else:
            self.listing()

    def _parse_argv(self):
        # base_url = sys.argv[0]
        path = sys.argv[2]

        try:
            args = path[1:]
            self.params = dict(urlparse.parse_qsl(args))

            ''' workaround to get the correct values for titles with special characters
            '''
            if ('title=\'\"' and '\"\'') in args:
                start_pos=args.find('title=\'\"')
                end_pos=args.find('\"\'')
                clean_title = args[start_pos+8:end_pos]
                self.params['title'] = clean_title

        except Exception:
            self.params = {}

    def listing(self):
        li = list()
        PluginListing(self.params,li)
        self._additems(li)

    def getinfos(self):
        li = list()
        plugin = PluginContent(self.params,li)
        self._execute(plugin,self.info)
        self._additems(li)

    # def getinfos(self):
    #     li = list()
    #     plugin = PluginContent(self.params, li)
    #     if plugin.params.get('info') == 'getoscars':
    #         winner = plugin.params.get('winner')
    #         category = plugin.params.get('category')
    #         thread = threading.Thread(target=plugin.getoscars, kwargs={'category': category, 'winner': winner})
    #         # thread.daemon = True
    #         thread.start()
    #         thread = threading.Thread(target=self.grr, args=(plugin, li))
    #         # thread.daemon = True
    #         thread.start()
    #
    #
    # def grr(self, plugin, li):
    #         self._execute(plugin, self.info)
    #         self._additems(li)

    # def getinfos(self):
    #     li = list()
    #     plugin = PluginContent(self.params, li)
    #     # self._execute(plugin,self.info)
    #
    #     if plugin.params.get('info') == 'getoscars':
    #         category = plugin.params.get('category')
    #         winner = plugin.params.get('winner')
    #         if category is not None and winner is not None:
    #             if winner == 'no':
    #                 file_name = 'oscar.' + category + '.nominees.blob'
    #                 data = get_pickle(file_name)
    #                 # item_list = get_cache(cache_key)
    #             else:
    #                 file_name = 'oscar.' + category + '.winners.blob'
    #                 data = get_pickle(file_name)
    #                 # item_list = get_cache(cache_key)
    #             if data is None:
    #                 self._execute(plugin, self.info)
    #                 save_pickle(file_name, li)
    #                 self._additems(li)
    #                 log('category to pickle', INFO)
    #                 log(category, INFO)
    #             else:
    #                 log('category already pickle', INFO)
    #                 log(category, INFO)
    #                 self._additems(li)
    #     else:
    #         self._additems(li)

    def actions(self):
        plugin = PluginActions(self.params)
        self._execute(plugin,self.action)

    def _execute(self,plugin,action):
        getattr(plugin,action.lower())()

    def _additems(self,li):
        xbmcplugin.addDirectoryItems(int(sys.argv[1]), li)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))


if __name__ == '__main__':
    Main()
