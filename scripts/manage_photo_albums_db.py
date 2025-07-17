import argparse
from datetime import datetime
import boto3
from website_generation.photo_album.config import Config

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring the photo albums database from digital ocean spaces',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-b', '--backup', action='store_true',
        help='Backup photo albums database to cloud bucket, using current date and time as key name'
    )
    group.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore photo albums databse stored, uses that last uploaded backup'
    )
    return parser

def get_bucket_resource(config: Config):
    return boto3.session.Session(
        region_name='tor1',
        aws_access_key_id=config.api_access_key,
        aws_secret_access_key=config.api_secret_key
    ).resource(
        's3', 
        endpoint_url='https://tor1.digitaloceanspaces.com'
    ).Bucket(config.db_backup_bucket)

def backup_db(config: Config):
    bucket = get_bucket_resource(config)
    key_name = datetime.today().strftime('%Y-%m-%d %H:%M')
    print(f'Uploading with key {key_name}...')
    bucket.upload_file(
        config.photo_albums_db_path, 
        key_name, 
        ExtraArgs={'ACL': 'public-read'})

def restore_db(config: Config):
    bucket = get_bucket_resource(config)
    backups = list(bucket.objects.all())
    backups.sort(key=lambda x: datetime.strptime(x.key, '%Y-%m-%d %H:%M'))

    print(f'Restoring {backups[-1].key}...')
    response = input('Are you sure you want to restore? (y/n): ')
    if response == 'y':
        print('Restoring...')
        bucket.download_file(
            backups[-1].key, 
            config.photo_albums_db_path)
    else:
        print('Aborting...')

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    config = Config()
    if args.backup:
        print(f"Backing up db...")
        backup_db(config)
    if args.restore:
        print("Restoring photo db...")
        restore_db(config)
