import os
import shutil

from config import AbstractConfig
from photo_album.photo_album_db import Album, Photo

class PhotoAlbumFileSystem:
    def __init__(self, config: AbstractConfig):
        self.root_dir = config.photo_albums_root

    def clean_dir(self, album: Album, db_photos: list[Photo]) -> int:
        dir_path = os.path.join(self.root_dir, album.dirname)
        local_photos = os.listdir(dir_path)
        to_remove = set(local_photos) - set([p.filename for p in db_photos])
        for fname in to_remove:
            os.remove(os.path.join(self.root_dir, fname))
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
        return len(to_remove)
    
    def remove_dangling_albums(self, db_albums: list[Album]) -> list[str]:
        local_albums = os.listdir(self.root_dir)
        to_remove = set(local_albums) - set([a.dirname for a in db_albums])
        for dir_name in to_remove:
            shutil.rmtree(os.path.join(self.root_dir, dir_name))
        return list(to_remove)