import os
from datetime import datetime
import shutil
import sqlite3

from jinja2 import Environment, FileSystemLoader

def copy_files():
    shutil.copytree('html', 'generated', dirs_exist_ok=True)
    shutil.copytree('images', 'generated/images')
    shutil.copytree('resources', 'generated/resources')

def generate_photo_albums():
    template_env = Environment(loader=FileSystemLoader("website-generation/templates/"))
    con = sqlite3.connect('photo-albums.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    db_albums = cur.execute('SELECT rowid, name, start_date_str, end_date_str, dirname FROM album').fetchall()
    albums = []
    for dba in db_albums: 
        album = {}
        album['name'] = dba['name']
        album['dirname'] = dba['dirname']

        try:
            album['start_date'] = datetime.strptime(dba['start_date_str'], '%b %Y')
            album['start_date_str'] = dba['start_date_str']
        except ValueError:
            album['start_date'] = datetime.strptime(dba['start_date_str'], '%Y')
            album['start_date_str'] = dba['start_date_str']
        if dba['end_date_str']:
            try:
                album['end_date'] = datetime.strptime(dba['end_date_str'], '%b %Y')
                album['end_date_str'] = dba['end_date_str']
            except ValueError:
                album['end_date'] = datetime.strptime(dba['end_date_str'], '%Y')
                album['end_date_str'] = dba['end_date_str']
        else:
            album['end_date'] = ''
        albums.append(album)
    albums.sort(key=lambda x: x['start_date'], reverse=True)

    template = template_env.get_template('photo_album_list.html')
    with open('generated/photo_album_list.html', mode='w') as f:
        f.write(template.render({'albums': albums}))

    os.mkdir('generated/photo-albums')
    template = template_env.get_template('photo_album.html')

    for dba in db_albums:
        res = cur.execute(
            "SELECT filename, position FROM photo WHERE album_id = ?", 
            (dba['rowid'],)).fetchall()
        res.sort(key=lambda x: x['position'])
        filenames = [x['filename'] for x in res]

        with open(f'generated/photo-albums/{dba['dirname']}.html', mode='w') as f:
            f.write(template.render(
                dirname=dba['dirname'],
                album_name=dba['name'], 
                start_date_str=dba['start_date_str'],
                end_date_str=dba['end_date_str'],
                filenames=filenames))

    con.close()

if __name__ =="__main__":
    shutil.rmtree('generated/', ignore_errors=True)
    os.makedirs('generated')
    copy_files()
    generate_photo_albums()