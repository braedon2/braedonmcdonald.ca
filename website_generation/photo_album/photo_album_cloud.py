import os
import boto3
from photo_album.photo_album_db import Album, Photo
from config import AbstractConfig

class PhotoAlbumCloud:
    def __init__(self, config: AbstractConfig):
        self.config = config
        self.client = boto3.Session().client(
            's3',
            region_name='tor1',
            endpoint_url='https://tor1.digitaloceanspaces.com',
            aws_secret_access_key=self.config.api_secret_key,
            aws_access_key_id=self.config.api_access_key
        )
        self.bucket = boto3.Session(
            region_name='tor1',
            aws_access_key_id=config.api_access_key,
            aws_secret_access_key=config.api_secret_key
        ).resource(
            's3',
            endpoint_url='https://tor1.digitaloceanspaces.com'
        ).Bucket(config.photo_albums_bucket)

    def download(self, album: Album, photo: Photo):
        object_key = f'{album.dirname}/{photo.filename}'
        download_dir = os.path.join(self.config.photo_albums_root, album.dirname)
        filepath = os.path.join(download_dir, photo.filename)
        
        if not (os.path.exists(download_dir)):
            os.makedirs(download_dir)
        self.client.download_file(
            self.config.photo_albums_bucket, 
            object_key, filepath)