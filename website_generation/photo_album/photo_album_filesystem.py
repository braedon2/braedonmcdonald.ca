import os
import shutil
from PIL import Image, ImageOps
from config import AbstractConfig
from photo_album.photo_album_db import Album, Photo

class AlbumNotSet(Exception):
    pass

def resize_image(path: str, filename: str) -> str:
    root, ext = os.path.splitext(filename)
    image_format = ext.replace('.', '')
    if image_format == 'jpg':
        image_format = 'JPEG'
    resized_filename = root + "_resized" + ext
    max_width = 680

    with Image.open(os.path.join(path, filename)) as image:
        image = ImageOps.exif_transpose(image)
        aspect_ratio = image.height / image.width
        if image.width > max_width:
            new_height = int(max_width * aspect_ratio)
            image = image.resize((max_width, new_height))
            image.format = image_format
        image.save(
            os.path.join(path, resized_filename), 
            format=image_format, 
            quality='keep')
    return resized_filename

class PhotoAlbumFileSystem:
    def __init__(self, config: AbstractConfig):
        self.root_dir = config.photo_albums_root
        self.album = None
        self.filenames_to_upload = []
        self.filename_pairs_to_upload = [] # tuples of uncompressed files with compressed counterpart

    def set_album(self, album: Album, db_photos: list[Photo]) -> None:
        self.album = album
        album_path = f'{self.root_dir}/{album.dirname}'
        filenames = os.listdir(album_path)
        filenames.sort(key=lambda x: os.path.getctime(f'{album_path}/{x}'))
        db_filenames = [p.filename for p in db_photos]
        self.filenames_to_upload = [f for f in filenames if f not in db_filenames]

    def resize_files(self) -> None:
        if not self.album:
            raise AlbumNotSet('Attempt to resize files before setting album on PhotoAlbumFileSystem instance')
        album_path = f'{self.root_dir}/{self.album.dirname}'
        for f in self.filenames_to_upload:
            if '_resized' not in f:
                resized_filename = resize_image(album_path, f)
                self.filename_pairs_to_upload.append((f, resized_filename))
            else:
                non_resized_filename = f.replace('_resized', '')
                self.filename_pairs_to_upload.append((non_resized_filename, f))

    def clean_dir(self, album: Album, db_photos: list[Photo]) -> int:
        """Remove local photos not present in the database"""
        dir_path = os.path.join(self.root_dir, album.dirname)
        local_photos = os.listdir(dir_path)
        to_remove = set(local_photos) - set([p.filename for p in db_photos])
        for fname in to_remove:
            os.remove(os.path.join(self.root_dir, fname))
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
        return len(to_remove)
    
    def remove_dangling_albums(self, db_albums: list[Album]) -> list[str]:
        """Remove local albums not present in the database"""
        local_albums = os.listdir(self.root_dir)
        to_remove = set(local_albums) - set([a.dirname for a in db_albums])
        for dir_name in to_remove:
            shutil.rmtree(os.path.join(self.root_dir, dir_name))
        return list(to_remove)