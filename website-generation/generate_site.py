import os
import datetime
import shutil
import sqlite3

import jinja2

def copy_files():
    shutil.copytree('html', 'generated', dirs_exist_ok=True)
    shutil.copytree('images', 'generated/images')
    shutil.copytree('resources', 'generated/resources')

def generate_photo_albums():
    con = sqlite3.connect('photo-albums.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    db_albums = cur.execute('SELECT rowid, name, start_date_str, end_date_str FROM album').fetchall()
    albums = []
    for dba in db_albums:
        album = {}
        album['name'] = dba['name']
        try:
            album['start_date'] = datetime.strptime(dba['start_date'], '%b-%d-%Y')
            album['start_date_format'] = '%b-%d-%Y'
        except ValueError:
            album['start_date'] = datetime(dba['start_date'], '%Y')
            album['start_date_format'] = '%Y'


    albums.sort(key=lambda x: x['start_date'])

    con.close()

if __name__ =="__main__":
    shutil.rmtree('generated/', ignore_errors=True)
    os.makedirs('generated')
    copy_files()
    generate_photo_albums()