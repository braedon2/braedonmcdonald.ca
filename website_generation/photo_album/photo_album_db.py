from __future__ import annotations

from datetime import datetime
import sqlite3

class IncompatiblePhotoListException(Exception):
    pass

class Album:
    def __init__(
            self, 
            name: str, 
            start_date_str: str, 
            end_date_str: str, 
            dirname, 
            rowid: int|None = None):
        self.rowid = rowid
        self.name = name
        self.dirname = dirname
        self.start_date_dtr = start_date_str
        self.end_date_str = end_date_str
        self.start_date = self.parse_date(start_date_str)

    def __lt__(self, album: Album) -> bool:
        return self.start_date < album.start_date

    @staticmethod
    def parse_date(date_str: str):
        try:
            return datetime.strptime(date_str, '%b %Y')
        except ValueError:
            return datetime.strptime(date_str, '%Y')
        
    @staticmethod
    def from_dirname(dirname: str) -> Album:
        name, *date_strs = dirname.split('_')
        name = name.replace('-', ' ')
        start_date_str = date_strs[0].replace('-', ' ')
        end_date_str = date_strs[1].replace('-', ' ') if len(date_strs) == 2 else ''
        return Album(name, start_date_str, end_date_str, dirname)
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> Album:
        return Album(
            row['name'], 
            row['start_date_str'], 
            row['end_date_str'], 
            row['dirname'], 
            row['rowid'])
    
class Photo:
    def __init__(self, filename: str, position: int, album_id: int, rowid: int|None):
        self.rowid = rowid
        self.filename = filename
        self.position = position
        self.album_id = album_id

    def __lt__(self, photo: Photo) -> bool:
        return self.position < photo.position
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> Photo:
        return Photo(
            row['filename'],
            row['position'],
            row['album_id'],
            row['rowid']
        )

class PhotoAlbumDb:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 

    def close(self):
        self.conn.close()

    def get_albums(self) -> list[Album]:
        res = self.conn.execute('SELECT rowid, * FROM album')
        rows = res.fetchall()
        return [Album.from_db_row(row) for row in rows]
    
    def get_resized_album_photos(self, album_id: int) -> list[Photo]:
        res = self.conn.execute(
            '''
            SELECT rowid, * 
            FROM photo 
            WHERE album_id = ? AND filename LIKE "%%_resized%%"
            ''', 
            (album_id,))
        rows = res.fetchall()
        return [Photo.from_db_row(row) for row in rows]
    
    def get_nonresized_album_photos(self, album_id: int) -> list[Photo]:
        res = self.conn.execute(
            '''
            SELECT rowid, * 
            FROM photo 
            WHERE album_id = ? AND filename NOT LIKE "%%_resized%%"
            ''', 
            (album_id,))
        rows = res.fetchall()
        return [Photo.from_db_row(row) for row in rows]

    def update_photos_with_new_order(self, photos: list[Photo]) -> None:
        """
        Updates each photos position to match its index in the input list.
        Updates both the photo and its non-resized counterpart.
        Input list must be resized photos only
        Input list's positions are mutated in place before being saved to db.
        """
        if not all('_resized' in photo.filename for photo in photos):
            raise IncompatiblePhotoListException('All photos must be resized')
        if not all(photo.rowid for photo in photos):
            raise IncompatiblePhotoListException('All photos must have rowids')
        
        for i, photo in enumerate(photos):
            photo.position = i
            self.conn.execute("""
                UPDATE photo
                SET position = ?
                WHERE rowid = ?""",
                (i, photo.rowid))
            self.conn.execute("""
                UPDATE photo
                SET position = ?
                WHERE filename = ?""",
                (i, photo.filename.replace('_resized', '')))
            