import argparse
import os
from datetime import datetime
import shutil
import sqlite3

from jinja2 import Environment, FileSystemLoader

from photo_album.photo_album_db import Album, Photo, PhotoAlbumDb
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
    db = PhotoAlbumDb(config)

    albums = db.get_albums()
    albums.sort(reverse=True)

    template = template_env.get_template('photo_album_list.html')
    with open(f'{config.generated_site_root}/photo_album_list.html', mode='w') as f:
        f.write(template.render(albums=[vars(album) for album in albums]))

    os.mkdir(f'{config.generated_site_root}/photo-albums')
    template = template_env.get_template('photo_album.html')

    for album in albums:
        photos = db.get_resized_album_photos(album.rowid)
        photos.sort(key=lambda x: x.position)
        filenames = [p.filename for p in photos]

        with open(f'{config.generated_site_root}/photo-albums/{album.dirname}.html', mode='w') as f:
            f.write(template.render(
                bucket=config.photo_albums_bucket,
                dirname=album.dirname,
                album_name=album.name, 
                start_date_str=album.start_date_str,
                end_date_str=album.end_date_str,
                filenames=filenames))

    db.close()

if __name__ =="__main__":
    parser = make_parser()
    args = parser.parse_args()
    config = Config() if not args.test else TestConfig()

    shutil.rmtree(config.generated_site_root, ignore_errors=True)
    os.makedirs(config.generated_site_root)
    copy_files(config)
    generate_photo_albums(config)