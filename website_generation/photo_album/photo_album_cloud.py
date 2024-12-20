import os
import boto3
from photo_album.photo_album_db import Album, Photo

class PhotoAlbumCloud:
    def __init__(
            self, access_key: str, 
            secret_key: str, 
            bucket_name: str,
            downlowd_root: str):
        self.bucket_name = bucket_name
        self.download_root = downlowd_root
        self.client = boto3.Session().client(
            's3',
            region_name='tor1',
            endpoint_url='https://tor1.digitaloceanspaces.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    def download(self, album: Album, photo: Photo):
        object_name = os.path.join(album.dirname, photo.filename)
        download_dir = os.path.join(self.download_root, album.dirname)
        filepath = os.path.join(download_dir, photo.filename)
        
        if not (os.path.exists(download_dir)):
            os.makedirs(download_dir)
        self.client.download_file(self.bucket_name, object_name, filepath)