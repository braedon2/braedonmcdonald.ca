import argparse
import os
from datetime import datetime
import shutil
import sqlite3

from jinja2 import Environment, FileSystemLoader

from config import Config, TestConfig, AbstractConfig

def make_parser():
    parser = argparse.ArgumentParser(
        description='Script for generating the site',
    )
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='Use the test database and cloud links to generate the photo albums')
    return parser

def copy_files(config: AbstractConfig):
    shutil.copytree('html', config.generated_site_root, dirs_exist_ok=True)
    shutil.copytree('images', f'{config.generated_site_root}/images')
    shutil.copytree('resources', f'{config.generated_site_root}/resources')

def generate_photo_albums(config: AbstractConfig):
    template_env = Environment(loader=FileSystemLoader(config.templates_path))
    con = sqlite3.connect(config.photo_albums_db_path)
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
    with open(f'{config.generated_site_root}/photo_album_list.html', mode='w') as f:
        f.write(template.render({'albums': albums}))

    os.mkdir(f'{config.generated_site_root}/photo-albums')
    template = template_env.get_template('photo_album.html')

    for dba in db_albums:
        res = cur.execute(
            'SELECT filename, position FROM photo WHERE album_id = ? AND filename LIKE "%%_resized%%"', 
            (dba['rowid'],)).fetchall()
        res.sort(key=lambda x: x['position'])
        filenames = [x['filename'] for x in res]

        with open(f'{config.generated_site_root}/photo-albums/{dba['dirname']}.html', mode='w') as f:
            f.write(template.render(
                bucket=config.photo_albums_bucket,
                dirname=dba['dirname'],
                album_name=dba['name'], 
                start_date_str=dba['start_date_str'],
                end_date_str=dba['end_date_str'],
                filenames=filenames))

    con.close()

if __name__ =="__main__":
    parser = make_parser()
    args = parser.parse_args()
    config = Config() if not args.test else TestConfig()

    shutil.rmtree(config.generated_site_root, ignore_errors=True)
    os.makedirs(config.generated_site_root)
    copy_files(config)
    generate_photo_albums(config)