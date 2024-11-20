import argparse
import os
import sys
import sqlite3
import boto3
from config import object_storage_config

bucket_name = 'braedonmcdonaldphotoalbums'
albums_dir = 'photo-albums'

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring photo albums from digital ocean spaces',
    )
    parser.add_argument(
        '-u', '--upload', action='store_true',
        help='Upload photo albums to cloud bucket, skipping ones that have already been uploaded'
    )
    parser.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore photo albums stored in the cloud to local dir'
    )
    return parser

def make_client():
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name='tor1',
        endpoint_url='https://tor1.digitaloceanspaces.com',
        aws_access_key_id=object_storage_config['api_access_key'],
        aws_secret_access_key=object_storage_config['api_secret_key']
    )

def make_db_con():
    con = sqlite3.connect("photo-albums.db")
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS album(
            name, 
            date_str,
            UNIQUE(name, date_str))
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS photo(
            filename, 
            position, 
            album_id,
            FOREIGN KEY(album_id) REFERENCES album(id),
            UNIQUE(filename, position, album_id))
    """)
    return con

def upload_all_albums():
    client = make_client()
    response = client.list_buckets()
    existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
    if bucket_name not in existing_buckets:
        client.create_bucket(Bucket=bucket_name)

    total_uploaded = 0
    total_skipped = 0

    album_dirs = os.listdir(albums_dir)
    for album_dirname in album_dirs:
        result = upload_album(album_dirname)
        total_uploaded += result['uploaded']
        total_skipped += result['skipped']

    print(f'Total uploaded: {total_uploaded}')
    print(f'Total skipped: {total_skipped}')

def upload_album(album_dirname):
    print(f'uploading {album_dirname}...')
    client = make_client()
    con = make_db_con()
    path = os.path.join(albums_dir, album_dirname)
    
    album_name, date_str = album_dirname.split('_')
    filenames = os.listdir(path)
    filenames.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)))

    cur = con.cursor()
    cur.execute(f'INSERT OR IGNORE INTO album VALUES (?, ?)', (album_name, date_str))
    con.commit()
    album_id = cur.execute(
        f'SELECT rowid FROM album WHERE name = ? and date_str = ?', 
        (album_name, date_str)).fetchone()[0]

    pos = 0
    uploaded = 0
    skipped = 0
    for filename in filenames:
        cur = con.cursor()
        cur.execute(f'INSERT OR IGNORE INTO photo VALUES(?, ?, ?)', (filename, pos, album_id))
        con.commit()
        filepath = os.path.join(albums_dir, album_dirname, filename)
        if cur.lastrowid:
            print(f'    Uploading {filename}...')
            client.upload_file(
                filepath, 
                bucket_name, 
                f'{album_dirname}/{filename}', 
                ExtraArgs={'ACL': 'public-read'})
            uploaded += 1
        else:
            skipped += 1
        pos += 1
    
    print(f'    Uploaded {uploaded}')
    print(f'    Skipped {skipped}')
    con.close()
    return {'uploaded': uploaded, 'skipped': skipped}

def restore_albums():
    pass

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    if args.upload and args.restore:
        print('Must supply either "upload" or "restore" as argument, not both')
        exit()
    if args.upload:
        print(f"Uploading photo albums...")
        upload_all_albums()
    if args.restore:
        print("Restoring photo albums...")
        restore_albums()
