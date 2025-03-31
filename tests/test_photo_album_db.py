import os
import sqlite3
from typing import Generator
import pytest

from website_generation.photo_album.config import TestConfig
from website_generation.photo_album.photo_album_db import PhotoAlbumDb
from website_generation.migrations.photo_album_migrations import run_migrations

config = TestConfig()
config.photo_albums_db_path = 'unit-test.db'

@pytest.fixture
def empty_db_path() -> Generator[str, None, None]:
    db_path = config.photo_albums_db_path
    run_migrations(db_path)
    yield db_path
    os.remove(config.photo_albums_db_path)

@pytest.fixture
def populated_db_path(empty_db_path) -> str:
    conn = sqlite3.connect(empty_db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Gaspe", "Aug 2023", "", "Gaspe_Aug-2023"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 1, cur.lastrowid),
            ("123_resized.jpg", 1, cur.lastrowid),
            ("345.jpg", 0, cur.lastrowid),
            ("345_resized.jpg", 0, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid),
            ("678_resized.jpg", 2, cur.lastrowid),
        ])
    conn.commit()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Test1", "Sep 2019", "Oct 2020", "Test1_Sep-2019_Oct-2020"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 0, cur.lastrowid),
            ("123_resized.jpg", 0, cur.lastrowid),
            ("345.jpg", 1, cur.lastrowid),
            ("345_resized.jpg", 1, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid),
            ("678_resized.jpg", 2, cur.lastrowid),
        ])
    conn.commit()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Test two", "2020", "", "Test-two_2020"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 0, cur.lastrowid),
            ("123_resized.jpg", 0, cur.lastrowid),
            ("345.jpg", 1, cur.lastrowid),
            ("345_resized.jpg", 1, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid),
            ("678_resized.jpg", 2, cur.lastrowid),
        ])
    conn.commit()
    conn.close()
    return empty_db_path

@pytest.fixture
def populated_db_object(populated_db_path):
    db = PhotoAlbumDb(config)
    yield db 
    db.close()

def test_get_albums_sortable(populated_db_object):
    # act
    albums = populated_db_object.get_albums()
    albums.sort()

    assert albums[0].name == "Test1"

def test_get_resized_album_photos_sortable(populated_db_object):
    #act
    photos = populated_db_object.get_resized_album_photos(1)
    photos.sort()

    assert all("_resized" in photo.filename for photo in photos)
    assert all(photo.position == i for i, photo in enumerate(photos))

def test_update_photos_with_new_order(populated_db_object):
    # arrange
    photos = populated_db_object.get_resized_album_photos(2)
    photos.sort(reverse=True)

    # act 
    populated_db_object.update_photos_with_new_order(photos)
    
    updated_db_resized_photos = populated_db_object.get_resized_album_photos(2)
    updated_db_resized_photos.sort()
    updated_nonresized_photos = populated_db_object.get_nonresized_album_photos(2)
    updated_nonresized_photos.sort()
    
    assert all(photo.position == i for i, photo in enumerate(photos))
    assert updated_db_resized_photos[0].filename == '678_resized.jpg'
    assert updated_db_resized_photos[1].filename == '345_resized.jpg'
    assert updated_db_resized_photos[2].filename == '123_resized.jpg'
    assert updated_nonresized_photos[0].filename == '678.jpg'
    assert updated_nonresized_photos[1].filename == '345.jpg'
    assert updated_nonresized_photos[2].filename == '123.jpg'

def test_delete_photo(populated_db_object):
    # arrange
    photos = populated_db_object.get_resized_album_photos(2)
    album = sorted(populated_db_object.get_albums())[0]
    
    # act
    populated_db_object.delete_photo(album, photos[1])
    updated_photos = populated_db_object.get_resized_album_photos(2)
    updated_photos.sort()

    assert len(updated_photos) == 2
    assert updated_photos[0].filename == '123_resized.jpg'
    assert updated_photos[0].position == 0
    assert updated_photos[1].filename == '678_resized.jpg'
    assert updated_photos[1].position == 2

    updated_photos = populated_db_object.get_nonresized_album_photos(2)
    updated_photos.sort()

    assert len(updated_photos) == 2
    assert updated_photos[0].filename == '123.jpg'
    assert updated_photos[0].position == 0
    assert updated_photos[1].filename == '678.jpg'
    assert updated_photos[1].position == 2
    