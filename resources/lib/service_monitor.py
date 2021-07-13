#!/usr/bin/python
# coding: utf-8

########################

import xbmc
import random

from resources.lib.helper import ADDON, ADDON_ID, DIALOG, condition, json_call, log, reload_widgets, sync_library_tags, winprop, DEBUG, check_simplecache
from resources.lib.image import ImageBlur
from resources.lib.player_monitor import PlayerMonitor
from resources.lib.plugin_content import update_top250

########################

NOTIFICATION_METHOD = ['VideoLibrary.OnUpdate',
                       'VideoLibrary.OnScanFinished',
                       'VideoLibrary.OnCleanFinished',
                       'AudioLibrary.OnUpdate',
                       'AudioLibrary.OnScanFinished', 'Other.LibraryChanged',  'Other.DatabaseReset'
                       ]

########################

class Service(xbmc.Monitor):
    def __init__(self):
        self.player_monitor = False

        self.restart = False
        self.screensaver = False
        self.service_enabled = ADDON.getSettingBool('service')

        if self.service_enabled:
            self.start()
        else:
            self.keep_alive()

    def onNotification(self, sender, method, data):
        log('Notify change', DEBUG)
        log(data, DEBUG)
        # DIALOG.notification(ADDON_ID, method)
        if ADDON_ID in sender and 'restart' in method:
            self.restart = True

        if method == 'Other.DatabaseReset':
            check_simplecache()

        if method in NOTIFICATION_METHOD:
            sync_library_tags()
            update_top250()

            if method.endswith('Finished'):
                reload_widgets(instant=True, reason=method)
            else:
                reload_widgets(reason=method)

    def onSettingsChanged(self):
        log('Service: Addon setting changed', force=True)
        self.restart = True

    def onScreensaverActivated(self):
        self.screensaver = True

    def onScreensaverDeactivated(self):
        self.screensaver = False

    def stop(self):
        if self.service_enabled:
            del self.player_monitor
            log('Service: Player monitor stopped', force=True)
            log('Service: Stopped', force=True)

        if self.restart:
            log('Service: Applying changes', force=True)
            xbmc.sleep(500) # Give Kodi time to set possible changed skin settings. Just to be sure to bypass race conditions on slower systems.
            DIALOG.notification(ADDON_ID, ADDON.getLocalizedString(32006))
            self.__init__()

    def keep_alive(self):
        log('Service: Disabled', force=True)

        while not self.abortRequested() and not self.restart:
            self.waitForAbort(5)

        self.stop()

    def start(self):
        log('Service: Started', force=True)

        self.player_monitor = PlayerMonitor()

        service_interval = xbmc.getInfoLabel('Skin.String(ServiceInterval)') or ADDON.getSetting('service_interval')
        service_interval = float(service_interval)
        background_interval = xbmc.getInfoLabel('Skin.String(BackgroundInterval)') or ADDON.getSetting('background_interval')
        background_interval = int(background_interval)
        widget_refresh = 0
        get_backgrounds = 200

        while not self.abortRequested() and not self.restart:

            ''' Only run timed tasks if screensaver is inactive to avoid keeping NAS/servers awake
            '''
            if not self.screensaver:

                ''' Grab fanarts
                '''
                if get_backgrounds >= 200:
                    log('Start new fanart grabber process')
                    arts = self.grabfanart()
                    get_backgrounds = 0

                else:
                    get_backgrounds += service_interval

                ''' Set background properties
                '''
                if background_interval >= 10:
                    if arts.get('all'):
                        self.setfanart('EmbuaryBackground', arts['all'])
                    if arts.get('videos'):
                        self.setfanart('EmbuaryBackgroundVideos', arts['videos'])
                    if arts.get('music'):
                        self.setfanart('EmbuaryBackgroundMusic', arts['music'])
                    if arts.get('movies'):
                        self.setfanart('EmbuaryBackgroundMovies', arts['movies'])
                    if arts.get('tvshows'):
                        self.setfanart('EmbuaryBackgroundTVShows', arts['tvshows'])
                    if arts.get('musicvideos'):
                        self.setfanart('EmbuaryBackgroundMusicVideos', arts['musicvideos'])
                    if arts.get('artists'):
                        self.setfanart('EmbuaryBackgroundMusic', arts['artists'])

                    background_interval = 0

                else:
                    background_interval += service_interval

                ''' Blur backgrounds
                '''
                if condition('Skin.HasSetting(BlurEnabled)'):
                    radius = xbmc.getInfoLabel('Skin.String(BlurRadius)') or ADDON.getSetting('blur_radius')
                    saturation = xbmc.getInfoLabel('Skin.String(BlurSaturation)') or '1.0'
                    ImageBlur(radius=radius, saturation=saturation)

                ''' Refresh widgets
                '''
                if widget_refresh >= 600:
                    reload_widgets(instant=True)
                    widget_refresh = 0

                else:
                    widget_refresh += service_interval

            self.waitForAbort(service_interval)

        self.stop()

    def grabfanart(self):
        arts = {'movies': [], 'tvshows': [], 'musicvideos': [], 'artists': [], 'all': [], 'videos': []}

        for item in ['movies', 'tvshows', 'artists', 'musicvideos']:
            dbtype = 'Video' if item != 'artists' else 'Audio'
            query = json_call('%sLibrary.Get%s' % (dbtype, item),
                              properties=['art'],
                              sort={'method': 'random'}, limit=40
                              )

            try:
                for result in query['result'][item]:
                    if result['art'].get('fanart'):
                        data = {'title': result.get('label', '')}
                        data.update(result['art'])
                        arts[item].append(data)

            except KeyError:
                pass

        arts['videos'] = arts['movies'] + arts['tvshows']

        for cat in arts:
            if arts[cat]:
                arts['all'] = arts['all'] + arts[cat]

        return arts

    def setfanart(self,key,items):
        arts = random.choice(items)
        winprop(key, arts.get('fanart', ''))
        for item in ['clearlogo', 'landscape', 'banner', 'poster', 'discart', 'title']:
            winprop('%s.%s' % (key, item), arts.get(item, ''))
