import sqlite3
import xbmcvfs
from resources.lib.helper import log, INFO



def update_user_rating(movie_id, user_rating):
    directory = xbmcvfs.translatePath('special://database/MyVideos119.db')
    conn = sqlite3.connect(directory)
    cur = conn.cursor()
    rq = """UPDATE movie SET userrating = ? WHERE idMovie = ?"""
    cur.execute(rq, (user_rating, movie_id))
    conn.commit()
    conn.close()



def get_director_art(movie_id):
    directory = xbmcvfs.translatePath('special://database/MyVideos119.db')
    conn = sqlite3.connect(directory)
    cur = conn.cursor()
    rq_d = """SELECT actor_id FROM director_link  WHERE media_type= 'movie' AND media_id=?"""
    cur.execute(rq_d, (movie_id,))
    data_d = cur.fetchone()
    if data_d is None:
        return None
    director_id = data_d[0]
    rq_a = """SELECT url FROM art  WHERE  media_type= 'director' AND media_id=?"""
    cur.execute(rq_a, (director_id,))
    data_a = cur.fetchone()
    conn.commit()
    conn.close()
    if data_a is None:
        return None
    else:
        thumb = data_a[0]
        return thumb

