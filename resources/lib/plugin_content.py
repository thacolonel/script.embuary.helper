#!/usr/bin/python
# coding: utf-8

########################

import random
import xbmcvfs

from resources.lib.helper import *
from resources.lib.library import *

########################

class PluginContent(object):

    def __init__(self,params,li):
        self.params = params
        self.dbtitle = remove_quotes(params.get('title'))
        self.dblabel = remove_quotes(params.get('label'))
        self.dbtype = remove_quotes(params.get('type'))
        self.dbid = remove_quotes(params.get('dbid'))
        self.season = remove_quotes(params.get('season'))
        self.tag = remove_quotes(params.get('tag'))
        self.unwatched = remove_quotes(params.get('unwatched'))
        self.limit = remove_quotes(params.get('limit'))
        self.retry_count = 1
        self.li = li

        if self.dbtype == 'movie':
            self.method_details = 'VideoLibrary.GetMovieDetails'
            self.method_item = 'VideoLibrary.GetMovies'
            self.param = 'movieid'
            self.key_details = 'moviedetails'
            self.key_items = 'movies'
            self.properties = movie_properties
        elif self.dbtype == 'tvshow':
            self.method_details = 'VideoLibrary.GetTVShowDetails'
            self.method_item = 'VideoLibrary.GetTVShows'
            self.param = 'tvshowid'
            self.key_details = 'tvshowdetails'
            self.key_items = 'tvshows'
            self.properties = tvshow_properties
        elif self.dbtype == 'episode':
            self.method_details = 'VideoLibrary.GetEpisodeDetails'
            self.method_item = 'VideoLibrary.GetEpisodes'
            self.param = 'episodeid'
            self.key_details = 'episodedetails'
            self.key_items = 'episodes'
            self.properties = episode_properties

        self.sort_lastplayed = {'order': 'descending', 'method': 'lastplayed'}
        self.sort_recent = {'order': 'descending', 'method': 'dateadded'}
        self.sort_random = {'method': 'random'}
        self.unplayed_filter = {'field': 'playcount', 'operator': 'lessthan', 'value': '1'}
        self.played_filter = {'field': 'playcount', 'operator': 'greaterthan', 'value': '0'}
        self.unplayedepisodes_filter = {'field':'numwatched','operator':'lessthan','value':['1']}
        self.playedepisodes_filter = {'field':'numwatched','operator':'greaterthan','value':['0']}
        self.specials_filter = {'field': 'season', 'operator': 'greaterthan', 'value': '0'}
        self.inprogress_filter = {'field': 'inprogress', 'operator': 'true', 'value': ''}
        self.notinprogress_filter = {'field': 'inprogress', 'operator': 'false', 'value': ''}
        self.tag_filter = {'operator': 'is', 'field': 'tag', 'value': self.tag}
        self.title_filter = {'operator': 'is', 'field': 'title', 'value': self.dbtitle}


    ''' by dbid to get all available listitems
    '''
    def getbydbid(self):
        try:
            json_query = json_call(self.method_details,
                                properties=self.properties,
                                params={self.param: int(self.dbid)}
                                )

            result = json_query['result'][self.key_details]

        except Exception as error:
            log('Get by DBID: No result found: %s' % error)
            return

        append_items(self.li,[result],type=self.dbtype)


    ''' by custom args to parse own json
    '''
    def getbyargs(self):
        limit = self.limit or None
        filter_args = remove_quotes(self.params.get('filter_args')) or None
        sort_args = remove_quotes(self.params.get('sort_args')) or None

        filters = []
        if filter_args is not None:
            filters.append(eval(filter_args))
        if self.tag:
            filters.append(self.tag_filter)
        if filters:
            filter = {'and': filters}
        else:
            filter = None

        if sort_args is not None:
            sort_args = eval(sort_args)

        try:
            json_query = json_call(self.method_item,
                                    properties=self.properties,
                                    sort=sort_args, limit=limit,
                                    query_filter=filter
                                    )

            result = json_query['result'][self.key_items]

        except Exception as error:
            log('Get by args: No result found: %s' % error)
            return

        append_items(self.li,result,type=self.dbtype)


    ''' resource helper to create a list will all existing and matching resource images
    '''
    def getresourceimages(self):
        resource_addon = self.params.get('addon')
        resource_dir = xbmc.translatePath('resource://%s/' % resource_addon)

        string = remove_quotes(self.params.get('string'))
        separator = remove_quotes(self.params.get('separator'))

        if separator:
            values = string.split(separator)
        else:
            values = string.splitlines()

        for item in values:
            for filename in ['%s.jpg' % item, '%s.png' % item]:
                filepath = resource_dir + filename
                if xbmcvfs.exists(filepath):
                    list_item = xbmcgui.ListItem(label=item)
                    list_item.setArt({'icon': filepath})
                    self.li.append(('', list_item, False))
                    break


    ''' season widgets to display library content that fit a special seasson or date
    '''
    def getseasonal(self):
        xmas = ['xmas', 'christmas', 'x-mas', 'mistletow', 'claus', 'snowman', 'happy holidays', 'st. nick', 'Weihnacht', 'weihnachten', 'fest der liebe', 'trannenbaum', 'schneemann', 'heilige nacht',
                'heiliger abend', 'heiligabend', 'nikolaus', 'christkind', 'mistelzweig', 'Noël', 'Meilleurs vœux', 'feliz navidad', 'joyeux noel', 'Natale', 'szczęśliwe święta', 'Veselé Vánoce',
                'Vrolijk kerstfeest', 'Kerstmis', 'Boże Narodzenie', 'Kalėdos', 'Crăciun']

        horror = ['ужас', 'užas', 'rædsel', 'horror', 'φρίκη', 'õudus', 'kauhu', 'horreur', 'užas', 'borzalom', 'hryllingi', 'ホラー', 'siaubas', 'verschrikking', 'skrekk', 'przerażenie', 'groază',
                'фильм ужасов', 'hrôza', 'grozo', 'Skräck', 'korku', 'жах']

        starwars = ['Star Wars', 'Krieg der Sterne', 'Luke Skywalker', 'Darth Vader', 'Jedi ', 'Ewoks', 'Starwars', 'Kylo Ren', 'Yoda ', 'Chewbacca', 'Anakin Skywalker', 'Han Solo', 'r2-d2', 'bb-8',
                    'Millennium Falcon', 'Millenium Falke', 'Stormtrooper', 'Sturmtruppler']

        startrek = ['Star Trek', 'Captain Kirk', 'Cpt. Kirk', 'James Kirk', 'James T. Kirk', 'James Tiberius Kirk', 'Jean-Luc Picard', 'Commander Spock', 'Deep Space Nine', 'Deep Space 9',
                    'Raumschiff Enterprise', 'Raumschiff Voyager', 'Klingonen', 'Klingons', 'Commander Data', 'Commander Geordi La Forge', 'Counselor Deanna Troi', 'William Thomas Riker',
                    'Captain Benjamin Sisko', 'Cpt. Benjamin Sisko', 'Captain Kathryn Janeway', 'Cpt. Kathryn Janeway']

        filters = []
        list_type = self.params.get('list')

        if list_type == 'xmas':
            use_episodes = True
            for keyword in xmas:
                filters.append({'operator': 'contains', 'field': 'title', 'value': keyword})
                filters.append({'operator': 'contains', 'field': 'plot', 'value': keyword})

        elif list_type == 'horror':
            use_episodes = False
            for keyword in horror:
                filters.append({'operator': 'contains', 'field': 'genre', 'value': keyword})

        elif list_type == 'starwars':
            use_episodes = False
            for keyword in starwars:
                filters.append({'operator': 'contains', 'field': 'title', 'value': keyword})
                filters.append({'operator': 'contains', 'field': 'originaltitle', 'value': keyword})
                filters.append({'operator': 'contains', 'field': 'plot', 'value': keyword})

        elif list_type == 'startrek':
            use_episodes = False
            for keyword in startrek:
                filters.append({'operator': 'contains', 'field': 'title', 'value': keyword})
                filters.append({'operator': 'contains', 'field': 'originaltitle', 'value': keyword})
                filters.append({'operator': 'contains', 'field': 'plot', 'value': keyword})

        else:
            return

        filter = {'or': filters}

        limit = self.limit or 25

        if self.dbtype != 'tvshow':
            json_query = json_call('VideoLibrary.GetMovies',
                                properties=movie_properties,
                                sort=self.sort_random, limit=limit,
                                query_filter=filter
                                )
            try:
                json_query = json_query['result']['movies']
            except Exception:
                log('Movies by seasonal keyword: No movies found.')
            else:
                append_items(self.li,json_query,type='movie')

        if self.dbtype != 'movie':
            if use_episodes:
                json_query = json_call('VideoLibrary.GetEpisodes',
                                    properties=episode_properties,
                                    sort=self.sort_random, limit=limit,
                                    query_filter=filter
                                    )
                try:
                    json_query = json_query['result']['episodes']
                except Exception:
                    log('Episodes by seasonal keyword: No episodes found.')
                else:
                    append_items(self.li,json_query,type='episode')

            else:
                json_query = json_call('VideoLibrary.GetTVShows',
                                    properties=tvshow_properties,
                                    sort=self.sort_random, limit=limit,
                                    query_filter=filter
                                    )
                try:
                    json_query = json_query['result']['tvshows']
                except Exception:
                    log('TV shows by seasonal keyword: No shows found.')
                else:
                    append_items(self.li,json_query,type='tvshow')

        random.shuffle(self.li)


    ''' get seasons of a show
    '''
    def getseasons(self):
        if not self.dbid:
            get_dbid = json_call('VideoLibrary.GetTVShows',
                            properties=['title'], limit=1,
                            query_filter=self.title_filter
                            )

            try:
                tvshow_dbid = get_dbid['result']['tvshows'][0]['tvshowid']
            except Exception:
                log('Get seasons by TV show: Show not found')
                return

        else:
            tvshow_dbid = self.dbid

        season_query = json_call('VideoLibrary.GetSeasons',
                            properties=season_properties,
                            sort={'order': 'ascending', 'method': 'season'},
                            params={'tvshowid': int(tvshow_dbid)}
                            )

        try:
            season_query = season_query['result']['seasons']
            if not len(season_query) > 1 and self.params.get('allseasons') == 'false':
                return

        except Exception:
            log('Get seasons by TV show: No seasons found')
        else:
            append_items(self.li,season_query,type='season')


    ''' get more episodes from the same season
    '''
    def getseasonepisodes(self):
        if not self.dbid:
            get_dbid = json_call('VideoLibrary.GetTVShows',
                            properties=['title'], limit=1,
                            query_filter=self.title_filter
                            )

            try:
                tvshow_dbid = get_dbid['result']['tvshows'][0]['tvshowid']
            except Exception:
                log('Get more episodes by season: Show not found')
                return

        else:
            tvshow_dbid = self.dbid

        episode_query = json_call('VideoLibrary.GetEpisodes',
                            properties=episode_properties,
                            sort={'order': 'ascending', 'method': 'episode'},
                            query_filter={'operator': 'is', 'field': 'season', 'value': self.season},
                            params={'tvshowid': int(tvshow_dbid)}
                            )

        try:
            episode_query = episode_query['result']['episodes']
        except Exception:
            log('Get more episodes by season: No episodes found')
        else:
            append_items(self.li,episode_query,type='episode')


    ''' get nextup of inprogress TV shows
    '''
    def getnextup(self):
        filters = [self.inprogress_filter]
        if self.tag:
            filters.append(self.tag_filter)
        filter = {'and': filters}

        json_query = json_call('VideoLibrary.GetTVShows',
                        properties=tvshow_properties,
                        sort=self.sort_lastplayed, limit=25,
                        query_filter=filter
                        )

        try:
            json_query = json_query['result']['tvshows']
        except Exception:
            log('Get next up episodes: No TV shows found')
            return

        for episode in json_query:

                episode_query = json_call('VideoLibrary.GetEpisodes',
                            properties=episode_properties,
                            sort={'order': 'ascending', 'method': 'episode'},limit=1,
                            query_filter={'and': [self.unplayed_filter,{'field': 'season', 'operator': 'greaterthan', 'value': '0'}]},
                            params={'tvshowid': int(episode['tvshowid'])}
                            )

                try:
                    episode_details = episode_query['result']['episodes']
                except Exception:
                    log('Get next up episodes: No next episodes found for %s' % episode['title'])
                else:
                    append_items(self.li,episode_details,type='episode')


    ''' get recently added episodes of unwatched shows
    '''
    def getnewshows(self):
        show_all = get_bool(self.params.get('showall'))

        if show_all:
            filter = self.tag_filter if self.tag else None

        else:
            filters = [self.unplayed_filter]
            if self.tag:
                filters.append(self.tag_filter)
            filter = {'and': filters}

        json_query = json_call('VideoLibrary.GetTVShows',
                        properties=tvshow_properties,
                        sort=self.sort_recent, limit=25,
                        query_filter=filter
                        )

        try:
            json_query = json_query['result']['tvshows']
        except Exception:
            log('Get new media: No TV shows found')
            return

        for tvshow in json_query:
            try:
                unwatchedepisodes = get_unwatched(tvshow['episode'],tvshow['watchedepisodes'])
                append_tvshow = False

                if show_all:
                    ''' All recently added episodes. Watched state is ignored and only items added of the same date
                        will be grouped.
                    '''
                    episode_query = json_call('VideoLibrary.GetEpisodes',
                                            properties=episode_properties,
                                            sort=self.sort_recent, limit=2,
                                            params={'tvshowid': int(tvshow['tvshowid'])}
                                            )

                    episode_query = episode_query['result']['episodes']

                    try:
                        if not get_date(episode_query[0]['dateadded']) == get_date(episode_query[1]['dateadded']):
                            raise Exception
                        append_tvshow = True

                    except Exception:
                        append_items(self.li,[episode_query[0]],type='episode')

                elif unwatchedepisodes == 1:
                    ''' Recently added episodes based on unwatched or in progress TV shows. Episodes will be grouped
                        if more than one unwatched episode is available.
                    '''
                    episode_query = json_call('VideoLibrary.GetEpisodes',
                                            properties=episode_properties,
                                            sort=self.sort_recent,limit=1,
                                            query_filter=self.unplayed_filter,
                                            params={'tvshowid': int(tvshow['tvshowid'])}
                                            )

                    episode_query = episode_query['result']['episodes']
                    append_items(self.li,episode_query,type='episode')

                else:
                    append_tvshow = True

                ''' Group episodes to show if more than one valid episode is available
                '''
                if append_tvshow:
                    tvshow_query = json_call('VideoLibrary.GetTVShowDetails',
                                            properties=tvshow_properties,
                                            params={'tvshowid': int(tvshow['tvshowid'])}
                                            )

                    tvshow_query = tvshow_query['result']['tvshowdetails']
                    append_items(self.li,[tvshow_query],type='tvshow')

            except Exception as error:
                log('Get new media: Not able to parse data for show %s - %s' % (tvshow,error))
                pass


    ''' get custom media by genre
    '''
    def getbygenre(self):
        genre = remove_quotes(self.params.get('genre'))

        if not genre:
            genres = []

            if self.dbtype != 'tvshow':
                movies_genres_query = json_call('VideoLibrary.GetGenres',
                                    sort={'method': 'label'},
                                    params={'type': 'movie'}
                                    )
                try:
                    for item in movies_genres_query['result']['genres']:
                        genres.append(item.get('label'))
                except Exception:
                    log('Get movies by genre: no genres found')

            if self.dbtype != 'movie':
                tvshow_genres_query = json_call('VideoLibrary.GetGenres',
                                    sort={'method': 'label'},
                                    params={'type': 'tvshow'}
                                    )
                try:
                    for item in tvshow_genres_query['result']['genres']:
                        genres.append(item.get('label'))
                except Exception:
                    log('Get TV shows by genre: no genres found')

            if genres:
                genre = random.choice(genres)

        if genre:
            filters = [{'operator': 'contains', 'field': 'genre', 'value': genre}]
            if self.unwatched == 'True':
                filters.append(self.unplayed_filter)
            if self.tag:
                filters.append(self.tag_filter)
            filter = {'and': filters}

            if self.dbtype != 'tvshow':
                json_query = json_call('VideoLibrary.GetMovies',
                                    properties=movie_properties,
                                    sort=self.sort_random, limit=10,
                                    query_filter=filter
                                    )
                try:
                    json_query = json_query['result']['movies']
                except Exception:
                    log('Movies by genre %s: No movies found.' % genre)
                else:
                    append_items(self.li,json_query,type='movie',searchstring=genre)

            if self.dbtype != 'movie':
                json_query = json_call('VideoLibrary.GetTVShows',
                                    properties=tvshow_properties,
                                    sort=self.sort_random, limit=10,
                                    query_filter=filter
                                    )
                try:
                    json_query = json_query['result']['tvshows']
                except Exception:
                    log('TV shows by genre %s: No shows found.' % genre)
                else:
                    append_items(self.li,json_query,type='tvshow',searchstring=genre)

            if not self.li:
                self._retry('getbygenre')

            random.shuffle(self.li)


    ''' get inprogress media
    '''
    def getinprogress(self):
        filters = [self.inprogress_filter]
        if self.tag:
            filters.append(self.tag_filter)
        filter = {'and': filters}

        if self.dbtype != 'tvshow':
            json_query = json_call('VideoLibrary.GetMovies',
                                properties=movie_properties,
                                sort=self.sort_lastplayed,
                                query_filter=filter
                                )
            try:
                json_query = json_query['result']['movies']
            except Exception:
                log('In progress media: No movies found.')
            else:
                append_items(self.li,json_query,type='movie')

        if self.dbtype != 'movie':
            json_query = json_call('VideoLibrary.GetEpisodes',
                                properties=episode_properties,
                                sort=self.sort_lastplayed,
                                query_filter=filter
                                )
            try:
                json_query = json_query['result']['episodes']
            except Exception:
                log('In progress media: No episodes found.')
            else:
                append_items(self.li,json_query,type='episode')


    ''' genres listing with 4 posters of each available genre content
    '''
    def getgenre(self):
        json_query = json_call('VideoLibrary.GetGenres',
                            sort={'method': 'label'},
                            params={'type': self.dbtype}
                            )
        try:
            json_query = json_query['result']['genres']
        except KeyError:
            log('Get genres: No genres found')
            return

        for genre in json_query:

            genre_items = json_call(self.method_item,
                            properties=['art'],
                            sort=self.sort_random, limit=4,
                            query_filter={'operator': 'is', 'field': 'genre', 'value': genre['label']}
                            )
            posters = {}
            index=0
            try:
                for art in genre_items['result'][self.key_items]:
                    poster = 'poster.%s' % index
                    posters[poster] = art['art'].get('poster', '')
                    index+=1
            except Exception:
                pass

            genre['art'] = posters

            try:
                genre['file'] = 'videodb://%ss/genres/%s/' % (self.dbtype, genre['genreid'])
            except Exception:
                log('Get genres: No genre ID found')
                return

        append_items(self.li,json_query,type='genre')


    ''' get movies by director
    '''
    def getdirectedby(self):
        if self.dbid:
            json_query = json_call('VideoLibrary.GetMovieDetails',
                                properties=['title', 'director'],
                                params={'movieid': int(self.dbid)}
                                )

        try:
            directors = json_query['result']['moviedetails']['director']
            title = json_query['result']['moviedetails']['title']
            joineddirectors = ' / '.join(directors)
        except Exception:
            log('Movies by director: No director found')
            return

        filters=[]
        for director in directors:
            filters.append({'operator': 'is', 'field': 'director', 'value': director})
        filter = {'and': [{'or': filters}, {'operator': 'isnot', 'field': 'title', 'value': title}]}

        json_query = json_call('VideoLibrary.GetMovies',
                                    properties=movie_properties,
                                    sort=self.sort_random,
                                    query_filter=filter
                                    )
        try:
            json_query = json_query['result']['movies']
        except Exception:
            log('Movies by director %s: No additional movies found' % joineddirectors)
            self._retry('getdirectedby')
            return

        append_items(self.li,json_query,type='movie',searchstring=joineddirectors)


    ''' get items by actor
    '''
    def getitemsbyactor(self):
        ''' Pick random actor of provided DBID item
        '''
        if self.dbid:
            json_query = json_call(self.method_details,
                                    properties=['title', 'cast'],
                                    params={self.param: int(self.dbid)}
                                    )

            try:
                cast = json_query['result'][self.key_details]['cast']
                title = json_query['result'][self.key_details]['label']

                if not cast:
                    raise Exception

            except Exception:
                log('Items by actor: No cast found')
                return

            cast_range=[]
            i = 0
            for actor in cast:
                if i < 4:
                    cast_range.append(actor['name'])
                    i += 1
                else:
                    break

            actor = ''.join(random.choice(cast_range))

        else:
            ''' Pick actor by label
            '''
            actor = self.dblabel
            title = self.dbtitle

        if actor and title:
            filter = {'and': [{'operator': 'is', 'field': 'actor', 'value': actor}, {'operator': 'isnot', 'field': 'title', 'value': title}]}

            if not self.dbtype == 'tvshow':
                movie_query = json_call('VideoLibrary.GetMovies',
                                        properties=movie_properties,
                                        sort=self.sort_random,
                                        query_filter=filter
                                        )

                try:
                    movie_query = movie_query['result']['movies']
                except Exception:
                    log('Items by actor %s: No movies found' % actor)
                else:
                    append_items(self.li,movie_query,type='movie',searchstring=actor)

            if not self.dbtype == 'movie':
                tvshow_query = json_call('VideoLibrary.GetTVShows',
                                        properties=tvshow_properties,
                                        sort=self.sort_random,
                                        query_filter=filter
                                        )

                try:
                    tvshow_query = tvshow_query['result']['tvshows']
                except Exception:
                    log('Items by actor %s: No shows found' % actor)
                else:
                    append_items(self.li,tvshow_query,type='tvshow',searchstring=actor)

            ''' Retry if query is based on dbid and a random actor
            '''
            if self.dbid and not self.li:
                self._retry('getitemsbyactor')

            random.shuffle(self.li)


    ''' because you watched xyz
    '''
    def getsimilar(self):
        ''' Based on show or movie of the database
        '''
        if self.dbid:
            json_query = json_call(self.method_details,
                                properties=['title', 'genre'],
                                params={self.param: int(self.dbid)}
                                )

        ''' Based on a random one of the last 10 watched items
        '''
        if not self.dbid:
            if self.dbtype == 'tvshow':
                query_filter={'or': [self.played_filter,self.playedepisodes_filter]}
            else:
                query_filter=self.played_filter

            json_query = json_call(self.method_item,
                                properties=['title', 'genre'],
                                sort={'method': 'lastplayed','order': 'descending'}, limit=10,
                                query_filter=query_filter
                                )

        ''' Get the genres of the selected item
        '''
        try:
            if self.dbid:
                title = json_query['result'][self.key_details]['title']
                genres = json_query['result'][self.key_details]['genre']
            else:
                similar_list = []
                for x in json_query['result'][self.key_items]:
                    if x['genre']:
                        similar_list.append(x)

                item_pos = self.params.get('pos')
                if not item_pos:
                    random.shuffle(similar_list)
                    i = 0
                else:
                    i = int(item_pos)

                title = similar_list[i]['title']
                genres = similar_list[i]['genre']

            if not genres:
                raise Exception

        except Exception:
            log ('Get similar: Not able to get genres')
            return

        random.shuffle(genres)

        ''' Get movies or shows based on one or two genres of selected watched item
        '''
        filters = [{'operator': 'isnot', 'field': 'title', 'value': title},{'operator': 'is', 'field': 'genre', 'value': genres[0]}]
        if len(genres) > 1:
            filters.append({'operator': 'is', 'field': 'genre', 'value': genres[1]})
        if self.tag:
            filters.append(self.tag_filter)
        filter = {'and': filters}

        json_query = json_call(self.method_item,
                            properties=self.properties,
                            sort=self.sort_random, limit=15,
                            query_filter=filter
                            )

        try:
            json_query = json_query['result'][self.key_items]
        except KeyError:
            log('Get similar: No matching items found')
            self._retry('getsimilar')
            return

        if self.dbtype == 'movie':
            append_items(self.li,json_query,type='movie',searchstring=title)
        elif self.dbtype == 'tvshow':
            append_items(self.li,json_query,type='tvshow',searchstring=title)


    ''' get cast of item
    '''
    def getcast(self):
        if self.dbtitle:
            json_query = json_call(self.method_item,
                                properties=['cast'],
                                limit=1,
                                query_filter=self.title_filter
                                )
        elif self.dbid:
            json_query = json_call(self.method_details,
                                properties=['cast'],
                                params={self.param: int(self.dbid)}
                                )

        try:
            if self.key_details in json_query['result']:
                cast = json_query['result'][self.key_details]['cast']
            else:
                cast = json_query['result'][self.key_items][0]['cast']

            if not cast:
                raise Exception

        except Exception:
            log('Get cast: No cast found.')
            return

        append_items(self.li,cast,type='cast')


    ''' jump to letter for smsjump navigation
    '''
    def jumptoletter(self):
        if xbmc.getInfoLabel('Container.NumItems'):

            all_letters = []
            for i in range(int(xbmc.getInfoLabel('Container.NumItems'))):
                all_letters.append(xbmc.getInfoLabel('Listitem(%s).SortLetter' % i).upper())

            if len(all_letters) > 1:

                numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                alphabet = ['#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
                letter_count = 0
                first_number = False

                for item in numbers:
                    if item in all_letters:
                        letter_count += 1
                        first_number = item
                        break

                for item in alphabet:
                    if item in all_letters:
                        letter_count += 1

                if letter_count < 2:
                    return

                for letter in alphabet:

                    li_item = xbmcgui.ListItem(label=letter)

                    if letter == '#' and first_number:
                        li_path = 'plugin://script.embuary.helper/?action=smsjump&letter=0'
                        li_item.setProperty('IsNumber', first_number)
                        append = True

                    elif letter in all_letters:
                        li_path = 'plugin://script.embuary.helper/?action=smsjump&letter=%s' % letter
                        append = True

                    elif get_bool(self.params.get('showall','true')):
                        li_path = ''
                        li_item.setProperty('NotAvailable', 'true')
                        append = True

                    else:
                        append = False

                    if append:
                        self.li.append((li_path, li_item, False))


    def getpathstats(self):
        path = remove_quotes(self.params.get('path'))
        prop_prefix = self.params.get('prefix','Stats')

        played = 0
        numitems = 0
        inprogress = 0
        episodes = 0
        watchedepisodes = 0
        tvshowscount = 0
        tvshows = []

        if 'activatewindow' in path.lower() and '://' in path and ',' in path:
            path = path.split(',')[1]
            path = remove_quotes("'" + path + "'") #be sure to remove unwanted quotes from the path

            json_query = json_call('Files.GetDirectory',
                                    properties=['playcount','resume','episode','watchedepisodes','tvshowid'],
                                    params={'directory': path, 'media': 'video'}
                                    )

            try:
                for item in json_query['result']['files']:
                    if 'type' not in item:
                        continue

                    if item['type'] == 'episode':
                        episodes += 1
                        if item['playcount'] > 0:
                            watchedepisodes += 1
                        if item['tvshowid'] not in tvshows:
                            tvshows.append(item['tvshowid'])
                            tvshowscount += 1

                    elif item['type'] == 'tvshow':
                        episodes += item['episode']
                        watchedepisodes += item['watchedepisodes']
                        tvshowscount += 1

                    else:
                        numitems += 1
                        if 'playcount' in item.keys():
                            if item['playcount'] > 0:
                                played += 1
                            if item['resume']['position'] > 0:
                                inprogress += 1

            except Exception:
                pass

            winprop('%s_Watched' % prop_prefix, str(played))
            winprop('%s_Count' % prop_prefix, str(numitems))
            winprop('%s_TVShowCount' % prop_prefix, str(tvshowscount))
            winprop('%s_InProgress' % prop_prefix, str(inprogress))
            winprop('%s_Unwatched' % prop_prefix, str(numitems - played))
            winprop('%s_Episodes' % prop_prefix, str(episodes))
            winprop('%s_WatchedEpisodes' % prop_prefix, str(watchedepisodes))
            winprop('%s_UnwatchedEpisodes' % prop_prefix, str(episodes - watchedepisodes))


    ''' retry loop for random based widgets if previous run has not returned any single item
    '''
    def _retry(self,type):
        log('Retry to get content (%s)' % str(self.retry_count))

        if self.retry_count < 5:
            self.retry_count += 1
            getattr(self, type)()

        else:
            log('No content found. Stop retrying.')
            self.retry_count = 1

