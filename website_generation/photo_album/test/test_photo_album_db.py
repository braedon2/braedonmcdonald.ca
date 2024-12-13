import os
import sqlite3
from typing import Generator

from website_generation.photo_album.photo_album_db import PhotoAlbumDb
from website_generation.photo_album_migrations import run_migrations
import pytest

@pytest.fixture
def empty_db_path() -> Generator[str, None, None]:
    db_path = 'test-photo-albums.db'
    run_migrations(db_path)
    yield db_path
    os.remove('test-photo-albums.db')

@pytest.fixture
def populated_db_path(empty_db_path) -> str:
    conn = sqlite3.connect(empty_db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Gaspe", "Aug 2023", "", "Gaspe_Aug-2023"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 0, cur.lastrowid),
            ("345.jpg", 1, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid)
        ])
    conn.commit()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Test1", "Sep 2019", "Oct 2020", "Test1_Sep-2019_Oct-2020"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 0, cur.lastrowid),
            ("345.jpg", 1, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid)
        ])
    conn.commit()
    cur.execute('INSERT INTO album VALUES (?, ?, ?, ?)',
        ("Test two", "2020", "", "Test-two_2020"))
    cur.executemany('INSERT INTO photo VALUES (?, ?, ?)',
        [
            ("123.jpg", 0, cur.lastrowid),
            ("345.jpg", 1, cur.lastrowid),
            ("678.jpg", 2, cur.lastrowid)
        ])
    conn.commit()
    conn.close()
    return empty_db_path

@pytest.fixture
def populated_db_object(populated_db_path):
    db = PhotoAlbumDb(populated_db_path)
    yield db 
    db.close()

def test_get_albums_sortable(populated_db_object):
    albums = populated_db_object.get_albums()
    albums.sort()

    assert albums[0].name == "Test1"