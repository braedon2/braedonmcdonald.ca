import os
import boto3
from photo_album.photo_album_db import Album, Photo
from config import AbstractConfig

class PhotoAlbumCloud:
    def __init__(self, config: AbstractConfig):
        self.config = config
        self.bucket = boto3.Session(
            region_name='tor1',
            aws_access_key_id=config.api_access_key,
            aws_secret_access_key=config.api_secret_key
        ).resource(
            's3',
            endpoint_url='https://tor1.digitaloceanspaces.com'
        ).Bucket(config.photo_albums_bucket)
        self.uploaded = 0

    def download(self, album: Album, photo: Photo) -> None:
        object_key = f'{album.dirname}/{photo.filename}'
        download_dir = os.path.join(self.config.photo_albums_root, album.dirname)
        filepath = os.path.join(download_dir, photo.filename)
        
        if not (os.path.exists(download_dir)):
            os.makedirs(download_dir)
        self.bucket.download_file(object_key, filepath)
        
    def upload(self, album: Album, photo: Photo) -> None:
        object_key = f'{album.dirname}/{photo.filename}'
        filepath = f'{self.config.photo_albums_root}/{album.dirname}/{photo.filename}'
        self.bucket.upload_file(
            filepath, object_key, 
            ExtraArgs={'ACL': 'public-read'})
        self.uploaded += 1

    def delete(self, album: Album, photo: Photo) -> None:
        """photo must have _resized suffix"""
        resized_key = f'{album.dirname}/{photo.filename}'
        original_key = f'{album.dirname}/{photo.filename.replace('_resized', '')}'
        self.bucket.Object(resized_key).delete()
        self.bucket.Object(original_key).delete()