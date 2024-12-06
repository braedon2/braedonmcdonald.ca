import argparse
from datetime import datetime
import sys

import boto3

from config import object_storage_config

bucket_name = 'braedonmcdonaldphotoalbumsdbbackup'
db_name = 'photo-albums.db'

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring the photo albums database from digital ocean spaces',
    )
    parser.add_argument(
        '-u', '--backup', action='store_true',
        help='Upload photo albums database to cloud bucket, using current date and time as key name'
    )
    parser.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore photo albums databse stored, uses that last uploaded backup'
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

def get_bucket_resource():
    session = boto3.session.Session(
        region_name='tor1',
        aws_access_key_id=object_storage_config['api_access_key'],
        aws_secret_access_key=object_storage_config['api_secret_key']
    )
    resource = session.resource(
        's3', 
        endpoint_url='https://tor1.digitaloceanspaces.com'
    )
    return resource.Bucket(bucket_name)

def backup_db():
    client = make_client()
    key_name = datetime.today().strftime('%Y-%m-%d %H:%M')
    print(f'Uploading with key {key_name}...')
    client.upload_file(
        db_name, 
        bucket_name, 
        key_name, 
        ExtraArgs={'ACL': 'public-read'})

def restore_db():
    client = make_client()
    bucket = get_bucket_resource()

    backups = list(bucket.objects.all())
    backups.sort(key=lambda x: x.last_modified)

    print(f'restoring {backups[-1].key}...')
    response = input('Are you sure you want to restore? (y/n): ')
    if response == 'y':
        client.download_file(bucket_name, backups[-1].key, db_name)

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    if args.backup and args.restore:
        print('Must supply either "upload" or "restore" as argument, not both')
        exit()
    if args.backup:
        print(f"Backing up db...")
        backup_db()
    if args.restore:
        print("Restoring photo db...")
        restore_db()