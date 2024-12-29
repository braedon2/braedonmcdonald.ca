import argparse
import os

from config import AbstractConfig, Config, TestConfig
from photo_album.photo_album_db import Album, Photo, PhotoAlbumDb
from photo_album.photo_album_cloud import PhotoAlbumCloud
from photo_album.photo_album_filesystem import PhotoAlbumFileSystem

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


def upload_all_albums(config: AbstractConfig):
    db = PhotoAlbumDb(config)
    cloud = PhotoAlbumCloud(config)

    album_dirs = os.listdir(config.photo_albums_root)
    for album_dirname in album_dirs:
        upload_album(album_dirname, db, cloud, config)

    db.close()
    print(f'Total uploaded: {cloud.uploaded}')


def upload_album(
        album_dirname: str, 
        db: PhotoAlbumDb, 
        cloud: PhotoAlbumCloud,
        config: AbstractConfig):
    print(f'uploading {album_dirname}...')
    fs = PhotoAlbumFileSystem(config)
    album = Album.from_dirname(album_dirname)
    pos = db.add_album(album)

    fs.set_album(album, db.get_album_photos(album.rowid))
    fs.resize_files()

    for pair in fs.filename_pairs_to_upload:
        for filename in pair:
            print(f'    Uploading {filename}...')
            photo = Photo(filename, pos, album.rowid)
            cloud.upload(album, photo)
            db.add_photo(photo)
        pos += 1


def restore_albums(config: AbstractConfig):
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
    if removed:
        print(f'    Removed {' '.join(removed)}')
    else:
        print('    Nothing to remove')

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    config = Config() if not args.test else TestConfig()
    if args.upload:
        print(f"Uploading photo albums...")
        upload_all_albums(config)
    if args.restore:
        print("Restoring photo albums...")
        restore_albums(config)
