#!/usr/bin/python
# coding: utf-8

########################

from __future__ import division

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import datetime
import random
import os
import locale
import pickle

from resources.lib.helper import (ADDON, ADDON_ID, ADDON_DATA_IMG_PATH, DIALOG, INFO, OSCARS_PATH, addon_data, clear_playlists, condition, execute,
                                  get_bool, get_library_tags, go_to_path, json_call, log, remove_quotes, set_library_tags,
                                  sync_library_tags, url_quote, url_unquote, winprop)
from resources.lib.library import get_unwatched
from resources.lib.json_map import JSON_MAP
from resources.lib.image import ImageBlur, image_info
from resources.lib.cinema_mode import CinemaMode
from resources.data.oscars import OSCAR_DATA
from resources.data.emmys import EMMY_DATA
from resources.lib.downloaders import RadarrAPI, SonarrAPI, RADARR_ICON, SONARR_ICON, get_default_folder, get_default_quality, get_default_search

########################

''' Classes
'''
def blurimg(params):
    ImageBlur(prop=params.get('prop', 'output'),
              file=remove_quotes(params.get('file')),
              radius=params.get('radius', None)
              )


def playcinema(params):
    CinemaMode(dbid=params.get('dbid'),
               dbtype=params.get('type')
               )


''' Dialogs
'''
def createcontext(params):
    selectionlist = []
    indexlist = []
    splitby = remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')

    for i in range(1, 100):
        label = xbmc.getInfoLabel('Window(%s).Property(Context.%d.Label)' % (window, i))

        if label == '':
            break

        elif label != 'none' and label != '-':
            selectionlist.append(label)
            indexlist.append(i)

    if selectionlist:
        index = DIALOG.contextmenu(selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Context.%d.Builtin)' % (window, indexlist[index]))
            for builtin in value.split(splitby):
                execute(builtin)
                xbmc.sleep(30)

    for i in range(1, 100):
        if window:
            execute('ClearProperty(Context.%d.Builtin,%s)' % (i, window))
            execute('ClearProperty(Context.%d.Label,%s)' % (i, window))
        else:
            execute('ClearProperty(Context.%d.Builtin)' % i)
            execute('ClearProperty(Context.%d.Label)' % i)


def createselect(params):
    selectionlist = []
    indexlist = []
    headertxt = remove_quotes(params.get('header', ''))
    splitby = remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')
    usedetails = True if params.get('usedetails') == 'true' else False
    preselect = int(params.get('preselect', -1))

    for i in range(1, 100):
        label = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Label)' % (window, i))
        label2 = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Label2)' % (window, i))
        icon = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Icon)' % (window, i))

        if label == '':
            break

        elif label != 'none' and label != '-':
            li_item = xbmcgui.ListItem(label=label, label2=label2)
            li_item.setArt({'icon': icon})
            selectionlist.append(li_item)
            indexlist.append(i)

    if selectionlist:
        index = DIALOG.select(headertxt, selectionlist, preselect=preselect, useDetails=usedetails)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Builtin)' % (window, indexlist[index]))
            for builtin in value.split(splitby):
                execute(builtin)
                xbmc.sleep(30)

    for i in range(1, 100):
        if window:
            execute('ClearProperty(Dialog.%d.Builtin,%s)' % (i, window))
            execute('ClearProperty(Dialog.%d.Label,%s)' % (i, window))
            execute('ClearProperty(Dialog.%d.Label2,%s)' % (i, window))
            execute('ClearProperty(Dialog.%d.Icon,%s)' % (i, window))
        else:
            execute('ClearProperty(Dialog.%d.Builtin)' % i)
            execute('ClearProperty(Dialog.%d.Label)' % i)
            execute('ClearProperty(Dialog.%d.Label2)' % i)
            execute('ClearProperty(Dialog.%d.Icon)' % i)


def splitandcreateselect(params):
    headertxt = remove_quotes(params.get('header', ''))
    seperator = remove_quotes(params.get('seperator', ' / '))
    splitby = remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')

    selectionlist = remove_quotes(params.get('items')).split(seperator)

    if selectionlist:
        index = DIALOG.select(headertxt, selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Dialog.Builtin)' % window)
            value = value.replace('???', selectionlist[index])
            for builtin in value.split(splitby):
                execute(builtin)
                xbmc.sleep(30)

    if window:
        execute('ClearProperty(Dialog.Builtin,%s)' % window)
    else:
        execute('ClearProperty(Dialog.Builtin)')


def dialogok(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    DIALOG.ok(headertxt, bodytxt)


def dialogyesno(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    yesactions = params.get('yesaction', '').split('|')
    noactions = params.get('noaction', '').split('|')

    if DIALOG.yesno(headertxt, bodytxt):
        for action in yesactions:
            execute(action)
    else:
        for action in noactions:
            execute(action)


def textviewer(params):
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    DIALOG.textviewer(headertxt, bodytxt)


''' Functions
'''
def restartservice(params):
    execute('NotifyAll(%s, restart)' % ADDON_ID)


def calc(params):
    prop = remove_quotes(params.get('prop', 'CalcResult'))
    formula = remove_quotes(params.get('do'))
    result = eval(str(formula))
    winprop(prop, str(result))


def settimer(params):
    actions = remove_quotes(params.get('do'))
    time = params.get('time', '50')
    delay = params.get('delay')
    busydialog = get_bool(params.get('busydialog', 'true'))

    if busydialog:
        execute('ActivateWindow(busydialognocancel)')

    xbmc.sleep(int(time))
    execute('Dialog.Close(all,true)')

    while condition('Window.IsVisible(busydialognocancel)'):
        xbmc.sleep(10)

    for action in actions.split('||'):
        execute(action)
        if delay:
            xbmc.sleep(int(delay))


def encode(params):
    string = remove_quotes(params.get('string'))
    prop = params.get('prop', 'EncodedString')
    winprop(prop, url_quote(string))


def decode(params):
    string = remove_quotes(params.get('string'))
    prop = params.get('prop', 'DecodedString')
    winprop(prop, url_unquote(string))


def getaddonsetting(params):
    addon_id = params.get('addon')
    addon_setting = params.get('setting')
    prop = addon_id + '-' + addon_setting

    try:
        setting = xbmcaddon.Addon(addon_id).getSetting(addon_setting)
        winprop(prop,str(setting))
    except Exception:
        winprop(prop, clear=True)


def togglekodisetting(params):
    settingname = params.get('setting', '')
    value = False if condition('system.getbool(%s)' % settingname) else True

    json_call('Settings.SetSettingValue',
              params={'setting': '%s' % settingname, 'value': value}
              )


def getkodisetting(params):
    setting = params.get('setting')
    strip = params.get('strip')

    json_query = json_call('Settings.GetSettingValue',
                           params={'setting': '%s' % setting}
                           )

    try:
        result = json_query['result']
        result = result.get('value')

        if strip == 'timeformat':
            strip = ['(12h)', ('(24h)')]
            for value in strip:
                if value in result:
                    result = result[:-6]

        result = str(result)
        if result.startswith('[') and result.endswith(']'):
           result = result[1:-1]

        winprop(setting,result)

    except Exception:
        winprop(setting, clear=True)


def setkodisetting(params):
    settingname = params.get('setting', '')
    value = params.get('value', '')

    try:
        value = int(value)
    except Exception:
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False

    json_call('Settings.SetSettingValue',
              params={'setting': settingname, 'value': value}
              )


def toggleaddons(params):
    addonid = params.get('addonid').split('+')
    enable = get_bool(params.get('enable'))

    for addon in addonid:

        try:
            json_call('Addons.SetAddonEnabled',
                      params={'addonid': addon, 'enabled': enable}
                      )
            log(f'{addon} - enable: {enable}')
        except Exception:
            pass


def playsfx(params):
    xbmc.playSFX(remove_quotes(params.get('path', '')))


def stopsfx(params):
    xbmc.stopSFX()


def imginfo(params):
    prop = remove_quotes(params.get('prop', 'img'))
    img = remove_quotes(params.get('img'))
    if img:
        width,height,ar = image_info(img)
        winprop(prop + '.width', str(width))
        winprop(prop + '.height', str(height))
        winprop(prop + '.ar', str(ar))


def playitem(params):
    clear_playlists()
    execute('Dialog.Close(all,true)')

    dbtype = params.get('type')
    dbid = params.get('dbid')
    resume = params.get('resume', True)
    file = remove_quotes(params.get('item'))

    if dbtype == 'song':
        param = 'songid'

    elif dbtype == 'episode':
        method_details = 'VideoLibrary.GetEpisodeDetails'
        param = 'episodeid'
        key_details = 'episodedetails'

    else:
        method_details = 'VideoLibrary.GetMovieDetails'
        param = 'movieid'
        key_details = 'moviedetails'

    if dbid:
        if dbtype == 'song' or not resume:
            position = 0

        else:
            result = json_call(method_details,
                               properties=['resume', 'runtime'],
                               params={param: int(dbid)}
                               )

            try:
                result = result['result'][key_details]
                position = result['resume'].get('position') / result['resume'].get('total') * 100
                resume_time = result.get('runtime') / 100 * position
                resume_time = str(datetime.timedelta(seconds=resume_time))
            except Exception:
                position = 0
                resume_time = None

            if position > 0:
                resume_string = xbmc.getLocalizedString(12022)[:-5] + resume_time
                contextdialog = DIALOG.contextmenu([resume_string, xbmc.getLocalizedString(12021)])

                if contextdialog == 1:
                    position = 0
                elif contextdialog == -1:
                    return

        json_call('Player.Open',
                  item={param: int(dbid)},
                  options={'resume': position},
                  )

    elif file:
        # playmedia() because otherwise resume points get ignored
        execute(f'PlayMedia({file})')


def playfolder(params):
    clear_playlists()

    dbid = int(params.get('dbid'))
    shuffled = get_bool(params.get('shuffle'))

    if shuffled:
        winprop('script.shuffle.bool', True)

    if params.get('type') == 'season':
        json_query = json_call('VideoLibrary.GetSeasonDetails',
                               properties=['title', 'season', 'tvshowid'],
                               params={'seasonid': dbid}
                               )
        try:
            result = json_query['result']['seasondetails']
        except Exception as error:
            log(f'Play folder error getting season details: {error}')
            return

        json_query = json_call('VideoLibrary.GetEpisodes',
                               properties=JSON_MAP['episode_properties'],
                               query_filter={'operator': 'is', 'field': 'season', 'value': result['season']},
                               params={'tvshowid': int(result['tvshowid'])}
                               )
    else:
        json_query = json_call('VideoLibrary.GetEpisodes',
                               properties=JSON_MAP['episode_properties'],
                               params={'tvshowid': dbid}
                               )

    try:
        result = json_query['result']['episodes']
    except Exception as error:
        log(f'Play folder error getting episodes: {error}')
        return

    for episode in result:
        json_call('Playlist.Add',
                  item={'episodeid': episode['episodeid']},
                  params={'playlistid': 1}
                  )

    execute('Dialog.Close(all)')

    json_call('Player.Open',
              item={'playlistid': 1, 'position': 0},
              options={'shuffled': shuffled}
              )


def playall(params):
    clear_playlists()

    container = params.get('id')
    method = params.get('method')

    playlistid = 0 if params.get('type') == 'music' else 1
    shuffled = get_bool(method,'shuffle')

    if shuffled:
        winprop('script.shuffle.bool', True)

    if method == 'fromhere':
        method = f'Container({container}).ListItemNoWrap'
    else:
        method = f'Container({container}).ListItemAbsolute'

    for i in range(int(xbmc.getInfoLabel(f'Container({container}).NumItems'))):

        if condition(f'String.IsEqual({method}({i}).DBType,movie)'):
            media_type = 'movie'
        elif condition(f'String.IsEqual({method}({i}).DBType,episode)'):
            media_type = 'episode'
        elif condition(f'String.IsEqual({method}({i}).DBType,song)'):
            media_type = 'song'
        else:
            media_type = None

        dbid = xbmc.getInfoLabel(f'{method}({i}).DBID')
        url = xbmc.getInfoLabel(f'{method}({i}).Filenameandpath')

        if media_type and dbid:
            json_call('Playlist.Add',
                      item={f'{media_type}id': int(dbid)},
                      params={'playlistid': playlistid}
                      )
        elif url:
            json_call('Playlist.Add',
                      item={'file': url},
                      params={'playlistid': playlistid}
                      )

    json_call('Player.Open',
              item={'playlistid': playlistid, 'position': 0},
              options={'shuffled': shuffled}
              )


def playrandom(params):
    clear_playlists()
    container = params.get('id')
    dbid = params.get('dbid')

    i = random.randint(1,int(xbmc.getInfoLabel(f'Container({container}).NumItems')))

    if condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,movie)' % (container, i)):
        media_type = 'movie'
    elif condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,episode)' % (container, i)):
        media_type = 'episode'
    elif condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,song)' % (container, i)):
        media_type = 'song'
    else:
        media_type = None

    item_dbid = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).DBID' % (dbid, i))
    url = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).Filenameandpath' % (dbid, i))

    playitem({'type': media_type, 'dbid': item_dbid, 'item': url, 'resume': False})


def jumptoshow_by_episode(params):
    episode_query = json_call('VideoLibrary.GetEpisodeDetails',
                              properties=['tvshowid'],
                              params={'episodeid': int(params.get('dbid'))}
                              )
    try:
        tvshow_id = str(episode_query['result']['episodedetails']['tvshowid'])
    except Exception:
        log('Could not get the TV show ID')
        return

    go_to_path('videodb://tvshows/titles/%s/' % tvshow_id)


def goto(params):
    go_to_path(remove_quotes(params.get('path')),params.get('target'))


def resetposition(params):
    containers = params.get('container').split('||')
    only_inactive_container = get_bool(params.get('only'),'inactive')
    current_control =xbmc.getInfoLabel('System.CurrentControlID')

    for item in containers:

        try:
            if current_control == item and only_inactive_container:
                raise Exception

            current_item = int(xbmc.getInfoLabel('Container(%s).CurrentItem' % item))
            if current_item > 1:
                current_item -= 1
                execute('Control.Move(%s,-%s)' % (item,str(current_item)))

        except Exception:
            pass


def details_by_season(params):
    season_query = json_call('VideoLibrary.GetSeasonDetails',
                             properties=JSON_MAP['season_properties'],
                             params={'seasonid': int(params.get('dbid'))}
                             )

    try:
        tvshow_id = str(season_query['result']['seasondetails']['tvshowid'])
    except Exception:
        log('Show details by season: Could not get TV show ID')
        return

    tvshow_query = json_call('VideoLibrary.GetTVShowDetails',
                             properties=JSON_MAP['tvshow_properties'],
                             params={'tvshowid': int(tvshow_id)}
                             )

    try:
        details = tvshow_query['result']['tvshowdetails']
    except Exception:
        log('Show details by season: Could not get TV show details')
        return

    episode = details['episode']
    watchedepisodes = details['watchedepisodes']
    unwatchedepisodes = get_unwatched(episode,watchedepisodes)

    winprop('tvshow.dbid', str(details['tvshowid']))
    winprop('tvshow.rating', str(round(details['rating'],1)))
    winprop('tvshow.seasons', str(details['season']))
    winprop('tvshow.episodes', str(episode))
    winprop('tvshow.watchedepisodes', str(watchedepisodes))
    winprop('tvshow.unwatchedepisodes', str(unwatchedepisodes))


def txtfile(params):
    prop = params.get('prop')
    path = xbmcvfs.translatePath(remove_quotes(params.get('path')))

    if os.path.isfile(path):
        log('Reading file %s' % path)
        with open(path) as f:
            text = f.read()

        if prop:
            winprop(prop,text)
        else:
            DIALOG.textviewer(remove_quotes(params.get('header')), text)

    else:
        log(f'Cannot find {path}')
        winprop(prop, clear=True)


def fontchange(params):
    font = params.get('font')
    fallback_locales = params.get('locales').split('+')

    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].lower()

        for value in fallback_locales:
            if value == shortlocale:
                setkodisetting({'setting': 'lookandfeel.font', 'value': params.get('font')})
                DIALOG.notification('%s %s' % (value.upper(),ADDON.getLocalizedString(32004)), '%s %s' % (ADDON.getLocalizedString(32005),font))
                log('Locale %s is not supported by default font. Change to %s.' % (value.upper(),font))
                break

    except Exception:
        log('Auto font change: No system locale found')


def setinfo(params):
    dbid = params.get('dbid')
    dbtype = params.get('type')
    value = remove_quotes(params.get('value'))

    try:
        value = int(value)
    except Exception:
        value = eval(value)
        pass

    if dbtype == 'movie':
        method = 'VideoLibrary.SetMovieDetails'
        key = 'movieid'

    elif dbtype == 'episode':
        method = 'VideoLibrary.SetEpisodeDetails'
        key = 'episodeid'

    elif dbtype == 'tvshow':
        method = 'VideoLibrary.SetTVShowDetails'
        key = 'tvshowid'

    json_call(method,
              params={key: int(dbid), params.get('field'): value}
              )


def split(params):
    value =  remove_quotes(params.get('value'))
    prop = params.get('prop')
    separator = remove_quotes(params.get('separator'))

    if value:
        if separator:
            value = value.split(separator)
        else:
            value = value.splitlines()

        i = 0
        for item in value:
            winprop('%s.%s' % (prop,i), item)
            i += 1

        for item in range(i,30):
            winprop('%s.%s' % (prop,i), clear=True)
            i += 1


def lookforfile(params):
    file = remove_quotes(params.get('file'))
    prop = params.get('prop', 'FileExists')

    if xbmcvfs.exists(file):
        winprop('%s.bool' % prop, True)
        log('File exists: %s' % file)

    else:
        winprop(prop, clear=True)
        log('File does not exist: %s' % file)


def getlocale(params):
    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].upper()
        winprop('SystemLocale', shortlocale)

    except Exception:
        winprop('SystemLocale', clear=True)


def deleteimgcache(params,path=ADDON_DATA_IMG_PATH,delete=False):
    if not delete:
        if DIALOG.yesno(ADDON.getLocalizedString(32003), ADDON.getLocalizedString(32019)):
            delete = True

    if delete:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                os.remove(full_path)
            else:
                deleteimgcache(params,full_path,True)


def selecttags(params):
    tags = get_library_tags()

    if tags:
        sync_library_tags(tags)

        try:
            whitelist = addon_data('tags_whitelist.' + xbmc.getSkinDir() +'.data')
        except Exception:
            whitelist = []

        indexlist = {}
        selectlist = []
        preselectlist = []

        index = 0
        for item in sorted(tags):
            selectlist.append(item)
            indexlist[index] = item
            if item in whitelist:
                preselectlist.append(index)
            index += 1

        selectdialog = DIALOG.multiselect(ADDON.getLocalizedString(32026), selectlist, preselect=preselectlist)

        if selectdialog is not None and not selectdialog:
            set_library_tags(tags, [], clear=True)

        elif selectdialog is not None:
            whitelist_new = []
            for item in selectdialog:
                whitelist_new.append(indexlist[item])

            if whitelist != whitelist_new:
                set_library_tags(tags, whitelist_new)

    elif params.get('silent') != 'true':
        DIALOG.ok(ADDON.getLocalizedString(32000), ADDON.getLocalizedString(32024))


def whitelisttags(params):
    sync_library_tags(recreate=True)


def oscarviewer(params):
    oscar_text = ''
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    imdbid = remove_quotes(params.get('imdbid', ''))
    oscar_item = OSCAR_DATA.get(imdbid, {})
    oscars = oscar_item.get('awards', [])
    annual = oscar_item.get('annual')
    heading = annual + ' ' + headertxt
    for i in oscars:
        item_text = ''
        category = i['category']
        won = i['won']
        nominee = i['nominee']
        if won is True:
            category = '[COLOR gold]' + category + '[/COLOR]'
        if nominee != 'None':
            item_text += '[B]' + category + '[/B][CR][I]' + nominee + '[/I]'
        else:
            item_text += '[B]' + category + '[/B]'
        oscar_text += '[CR]' + item_text + '[CR]'

    DIALOG.textviewer(heading, str(oscar_text))



def emmyviewer(params):
    emmy_text = ''
    # heading = 'Primetime Emmy Awards'
    headertxt = remove_quotes(params.get('header', ''))
    bodytxt = remove_quotes(params.get('message', ''))
    tvdb_id = remove_quotes(params.get('tvdbid', ''))
    emmy_type = remove_quotes(params.get('type', ''))
    heading = headertxt
    if emmy_type == 'tvshow':
        emmy_item = EMMY_DATA['series'].get(tvdb_id, {})
        emmys = emmy_item.get('emmys', [])
        for e in emmys:
            category = e['category']
            nominees = e['nominees']
            cat_wins = e['cat_wins']
            total_wins = 0
            total_noms = 0
            if cat_wins > 0:
                emmy_text += f'[CR][COLOR gold][B]{category}[/B][/COLOR][CR]'
            else:
                emmy_text += f'[CR][B]{category}[/B][CR]'
            for n in nominees:
                nominee = n['nominee']
                nom_years = str(n['awards']['nom_years']).replace('[', '(').replace(']', ')')
                noms = n['awards']['noms']
                wins = n['awards']['wins']
                win_years = str(n['awards']['win_years']).replace('[', '(').replace(']', ')')
                if wins > 0:
                    total_wins += 1
                    total_noms += 1
                else:
                    total_noms += 1

                if nominee is None:
                    text = ''
                else:
                    text = f'{nominee} - '

                if wins == 1 and noms > 1 :
                    text += f'{wins} win {win_years} and {noms} other nominations {nom_years}[CR]'
                elif wins > 1 and noms > 1 :
                    text += f'{wins} wins {win_years} and {noms} other nominations {nom_years}[CR]'
                elif wins == 1 and noms == 1:
                    text += f'{wins} win {win_years} and {noms} other nomination {nom_years}[CR]'
                elif wins > 1 and noms == 1 :
                    text += f'{wins} wins {win_years} and {noms} other nomination {nom_years}[CR]'
                elif wins > 1 and noms == 0:
                    text += f'{wins} wins {win_years}[CR]'
                elif wins == 1 and noms == 0:
                    text += f'{wins} win {win_years}[CR]'
                elif wins == 0 and noms > 1:
                    text += f'{noms} nominations {nom_years}[CR]'
                elif wins == 0 and noms == 1:
                    text += f'{noms} nomination {nom_years}[CR]'

                else:
                    text = ''

                emmy_text += f'[I]{text}[/I]'
    elif emmy_type == 'movie':
        emmy_item = EMMY_DATA['movies'].get(tvdb_id, {})
        emmys = emmy_item.get('awards', [])
        annual = emmy_item.get('annual')
        heading = annual + ' ' + headertxt
        for i in emmys:
            item_text = ''
            category = i['category']
            won = i['won']
            nominee = i['nominee']
            if won is True:
                category = '[COLOR gold]' + category + '[/COLOR]'
            if nominee != 'None':
                item_text += '[B]' + category + '[/B][CR][I]' + nominee + '[/I]'
            else:
                item_text += '[B]' + category + '[/B]'
            emmy_text += '[CR]' + item_text + '[CR]'


    DIALOG.textviewer(heading, str(emmy_text))


def save_pickle(file_name, data):
    try:
        if not os.path.exists(OSCARS_PATH):
            os.makedirs(OSCARS_PATH)

    except (OSError,TypeError) as e:
        # fix for race condition
        if e.errno != os.errno.EEXIST:
            raise
        DIALOG.notification('GRR', f'error saving pickle file{file_name} with error:{e}')
        log(f'error saving pickle file{file_name} with error:{e}', INFO)

    file_path = os.path.join(OSCARS_PATH,file_name)
    with open(file_path, 'wb+') as f:
        pickle.dump(data, f)
    log(f'pickle file saved: {file_name}', INFO)
    DIALOG.notification('GRR', f'pickle file saved: {file_name}')


def get_pickle(file_name):
    try:
        if not os.path.exists(OSCARS_PATH):
            os.makedirs(OSCARS_PATH)

    except OSError as e:
        # fix for race condition
        if e.errno != os.errno.EEXIST:
            raise
        pass

    file_path = os.path.join(OSCARS_PATH, file_name)
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
    except (OSError,TypeError, EOFError):
        # log(f'Could not load pickle for {file_name}', INFO)
        # DIALOG.notification('GRR', f'Could not load pickle for {file_name}')
        return None
    except pickle.UnpicklingError:
        log(f'Unpickling error for {file_name}', INFO)
        DIALOG.notification('GRR', f'Unpickling error for {file_name}')
        return None
    else:
        return data


def downloadmovie(params):
    movie_id = remove_quotes(params.get('movieid', ''))

    # if user cancels, return
    if not movie_id:
        return
    rdr = RadarrAPI()
    movies = rdr.get_movies()
    if movies is None:
        DIALOG.notification('Radarr', 'Problem getting movies', RADARR_ICON, 5000)
        return
    tmdb_ids = [movie.get('tmdbId') for movie in movies]
    data = rdr.lookup_movie(movie_id)

    # open dialog for choosing preferred quality if not specified
    default_quality = get_default_quality('radarr')
    if default_quality is None:
        return

    # open dialog for choosing default folder if not specified
    default_folder = get_default_folder('radarr')
    if default_folder is None:
        return

    # open dialog for choosing default search if not specified
    default_search = get_default_search('radarr')
    if default_search is None:
        return

    # Set Add Movie Data
    tmdb_id = data['tmdbId']
    title = data['title']
    new_data = {
        'title': str(title),
        'year': int(data['year']),
        'qualityProfileId': int(default_quality),
        'titleSlug': str(data['titleSlug']),
        'tmdbId': int(tmdb_id),
        'images': data['images'],
        'rootFolderPath': default_folder,
        'monitored': True,
        'addOptions': {
             'searchForMovie': default_search
        }
    }
    if tmdb_id in tmdb_ids:
        DIALOG.notification('Radarr', f'Already added movie: {title}', RADARR_ICON, 5000)
        return
    else:
        res = rdr.add_movie(new_data)
        if res is None:
            DIALOG.notification('Radarr', f'Could not add movie: {title}', RADARR_ICON, 5000)
        else:
            DIALOG.notification('Radarr', f'Added movie: {title}', RADARR_ICON, 5000)
        return

def downloadshow(params):
    snr = SonarrAPI()
    series_id = remove_quotes(params.get('seriesid', ''))

    # if user cancels, return
    if not series_id:
        return

    shows = snr.get_shows()
    if shows is None:
        DIALOG.notification('Sonarr', 'Problem getting shows from Sonarr', SONARR_ICON, 5000)
        return
    tvdb_ids = [show.get('tvdbId') for show in shows]
    data = snr.lookup_show(series_id)

    # open dialog for choosing preferred quality if not specified
    default_quality = get_default_quality('sonarr')
    if default_quality is None:
        return

    # open dialog for choosing default folder if not specified
    default_folder = get_default_folder('sonarr')
    if default_folder is None:
        return

    # Get default search if not specified
    default_search = get_default_search('sonarr')
    # DIALOG.notification('Sonarr', f'Default Search: {default_search}', SONARR_ICON, 5000)
    # if default_search is None:
    #     return

    # Set Add Show Data
    tvdb_id = data['tvdbId']
    title = data['title']
    new_data = {
        'title': str(title),
        'profileId': int(default_quality),
        'titleSlug': str(data['titleSlug']),
        'tvdbId': int(tvdb_id),
        'images': data['images'],
        'seasons': data['seasons'],
        'rootFolderPath': default_folder,
        'monitored': True,
        'addOptions': {
             'searchForMissingEpisodes': default_search
        }
    }
    if tvdb_id in tvdb_ids:
        DIALOG.notification('Sonarr', f'Already added show: {title}', SONARR_ICON, 5000)
        return
    else:
        res = snr.add_show(new_data)
        if res is None:
            DIALOG.notification('Sonarr', f'Could not add show: {title}', SONARR_ICON, 5000)
        else:
            DIALOG.notification('Sonarr', f'Added show: {title}', SONARR_ICON, 5000)
        return
