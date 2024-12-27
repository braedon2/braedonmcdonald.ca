import argparse
import os
import sqlite3
import sys

import boto3
from PIL import Image, ImageOps

from config import Config, TestConfig
from photo_album.photo_album_db import Album, Photo, PhotoAlbumDb
from photo_album.photo_album_cloud import PhotoAlbumCloud
from photo_album.photo_album_filesystem import PhotoAlbumFileSystem

bucket_name = 'braedonmcdonaldphotoalbums'
albums_dir = 'photo-albums'

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring photo albums from digital ocean spaces',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--upload', action='store_true',
        help='Upload photo albums to cloud bucket, skipping ones that have already been uploaded'
    )
    group.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore photo albums stored in the cloud to local dir'
    )
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='restore or upload to the configured test bucket and database'
    )
    return parser

def make_client():
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name='tor1',
        endpoint_url='https://tor1.digitaloceanspaces.com',
        aws_access_key_id=Config.api_access_key,
        aws_secret_access_key=Config.api_secret_key
    )

def resize_image(path: str, filename: str) -> str:
    resized_filename = os.path.splitext(filename)[0] + "_resized.JPEG" 
    max_width = 680

    with Image.open(os.path.join(path, filename)) as image:
        image = ImageOps.exif_transpose(image)
        aspect_ratio = image.height / image.width
        if image.width > max_width:
            new_height = int(max_width * aspect_ratio)
            image = image.resize((max_width, new_height))
            image.format = 'JPEG'
        image.save(
            os.path.join(path, resized_filename), 
            format='JPEG', 
            quality='keep')

    return resized_filename

def upload_all_albums(conn):
    client = make_client()
    response = client.list_buckets()
    existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
    if bucket_name not in existing_buckets:
        client.create_bucket(Bucket=bucket_name)

    total_uploaded = 0
    total_skipped = 0

    album_dirs = os.listdir(albums_dir)
    for album_dirname in album_dirs:
        result = upload_album(conn, album_dirname)
        total_uploaded += result['uploaded']
        total_skipped += result['skipped']

    print(f'Total uploaded: {total_uploaded}')
    print(f'Total skipped: {total_skipped}')
    conn.close()

def upload_album(conn, album_dirname):
    print(f'uploading {album_dirname}...')
    client = make_client()
    path = os.path.join(albums_dir, album_dirname)
    
    album_name, *date_strs = album_dirname.split('_')
    album_name = album_name.replace('-', ' ')
    filenames = os.listdir(path)
    filenames.sort(key=lambda x: os.path.getctime(os.path.join(path, x)))

    start_date_str = date_strs[0].replace('-', ' ')
    end_date_str = date_strs[1].replace('-', ' ') if len(date_strs) == 2 else ''

    cur = conn.cursor()
    cur.execute(
        f'INSERT OR IGNORE INTO album VALUES (?, ?, ?, ?)', 
        (album_name, start_date_str, end_date_str, album_dirname))
    conn.commit()
    album_id = cur.execute(
        f'SELECT rowid FROM album WHERE dirname = ?', 
        (album_dirname,)).fetchone()[0]

    pos = 0
    uploaded = 0
    skipped = 0

    res = cur.execute(
        f'SELECT position FROM photo WHERE album_id = ?', 
        (album_id,)).fetchall()
    if res:
        pos = max([x[0] for x in res]) + 1

    for filename in filenames:
        cur = conn.cursor()
        cur.execute(
            f'INSERT OR IGNORE INTO photo VALUES(?, ?, ?)', 
            (filename, pos, album_id))
        conn.commit()
        filepath = os.path.join(albums_dir, album_dirname, filename)
        if cur.lastrowid:
            print(f'    Uploading {filename}...')
            client.upload_file(
                filepath, 
                bucket_name, 
                f'{album_dirname}/{filename}', 
                ExtraArgs={'ACL': 'public-read'})
            uploaded += 1
            if "_resized" not in filename:
                resized_filename = resize_image(path, filename)
                filepath = os.path.join(albums_dir, album_dirname, resized_filename)
                cur.execute(
                    f'INSERT OR IGNORE INTO photo VALUES(?, ?, ?)', 
                    (resized_filename, pos, album_id))
                conn.commit()
                print(f'    Uploading {resized_filename}...')
                client.upload_file(
                    filepath, 
                    bucket_name, 
                    f'{album_dirname}/{resized_filename}', 
                    ExtraArgs={'ACL': 'public-read'})
                uploaded += 1
            pos += 1
        else:
            skipped += 1
    
    print(f'    Uploaded {uploaded}')
    print(f'    Skipped {skipped}')
    return {'uploaded': uploaded, 'skipped': skipped}

def restore_albums():
    config = Config()
    db = PhotoAlbumDb(config)
    cloud = PhotoAlbumCloud(config)
    fs = PhotoAlbumFileSystem(config)

    for album in db.get_albums():
        print(f'Restoring {album.dirname}')
        db_photos = db.get_album_photos(album.rowid)
        for photo in db_photos:
            print(f'    Restoring {photo.filename}')
            cloud.download(album, photo)
        print(f'Syncing {album.dirname} with database')
        cleaned = fs.clean_dir(album, db_photos)
        print(f'    Removed {cleaned} photos')

    print('Removing dangling albums')
    removed = fs.remove_dangling_albums(db.get_albums())
    print(f'    Removed {' '.join(removed)}')

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if args.upload:
        print(f"Uploading photo albums...")
        conn = sqlite3.connect('photo-albums.db')
        upload_all_albums(conn)
    if args.restore:
        print("Restoring photo albums...")
        restore_albums()
