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
