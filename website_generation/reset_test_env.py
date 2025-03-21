import os
import shutil
from config import TestConfig
from photo_album_migrations import run_migrations
from photo_album.photo_album_cloud import PhotoAlbumCloud

config = TestConfig()

print("Copying files")
shutil.rmtree(config.photo_albums_root, ignore_errors=True)
shutil.copytree(config.test_data_source, config.photo_albums_root)

print("Reseting database")
os.remove(config.photo_albums_db_path)
run_migrations(config.photo_albums_db_path)

print("Deleting cloud objects")
cloud = PhotoAlbumCloud(config)
cloud.bucket.objects.delete()