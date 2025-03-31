import sqlite3
from website_generation.photo_album.config import Config

def initialize_version_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY
    )
    """)
    conn.commit()

def get_current_version(conn):
    cursor = conn.execute("SELECT MAX(version) FROM schema_version")
    result = cursor.fetchone()
    return result[0] if result[0] else 0

def migration_001(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS album(
        name, 
        start_date_str,
        end_date_str,
        dirname,
        UNIQUE(dirname))
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS photo(
        filename, 
        position, 
        album_id,
        FOREIGN KEY(album_id) REFERENCES album(id),
        UNIQUE(filename, album_id))
    """)
    conn.commit()

def apply_migrations(conn, migrations):
    current_version = get_current_version(conn)
    for version, migration in enumerate(migrations, start=1):
        if version > current_version:
            print(f"Applying migration {version}")
            migration(conn)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
            conn.commit()

migrations = [
    migration_001
]

def run_migrations(db_path):
    conn = sqlite3.connect(db_path)
    initialize_version_table(conn)
    apply_migrations(conn, migrations)
    conn.close()

if __name__ == '__main__':
    config = Config()
    conn = sqlite3.connect(config.photo_albums_db_path)
    initialize_version_table(conn)
    apply_migrations(conn, migrations)
    conn.close()
