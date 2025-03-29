import argparse
import os
import boto3
from config import Config

bucket_name = 'braedonmcdonaldguitarvideos'
video_dir = 'guitar-videos'

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring guitar videos from digital ocean spaces',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--upload', action='store_true',
        help='Upload guitar videos to cloud bucket, skipping ones that have already been uploaded'
    )
    group.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore guitar videos stored in the cloud to local dir'
    )
    return parser

def make_client():
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name='tor1',
        endpoint_url='https://tor1.digitaloceanspaces.com',
        aws_access_key_id=Config.api_access_key,
        aws_secret_access_key=Config.api_secret_key
    )

def get_video_keys(client):
    response = client.list_objects_v2(Bucket=bucket_name)
    video_keys = []
    if response['KeyCount']:
        video_keys = [video['Key'] for video in response['Contents']]
    return video_keys

def upload():
    client = make_client()
    response = client.list_buckets()

    response = client.list_objects_v2(Bucket=bucket_name)
    cloud_videos = []
    if response['KeyCount']:
        cloud_videos = [video['Key'] for video in response['Contents']]
        
    local_videos = os.listdir(video_dir)
    if set(local_videos) == set(cloud_videos):
        print('Nothing to upload')
    for video in local_videos:
        if video not in cloud_videos:
            print(f'Uploading {video}...')
            client.upload_file(f'{video_dir}/{video}', bucket_name, video, ExtraArgs={'ACL': 'public-read'})
    print('Done')

def restore():
    client = make_client()
    local_videos = []
    if not os.path.isdir(video_dir):
        os.mkdir(video_dir)
    else:
        local_videos = os.listdir(video_dir)

    video_keys = get_video_keys(client)
    if set(local_videos) == set(video_keys):
        print('Nothing to restore')
    for key in video_keys:
        if key not in local_videos:
            print(f'Downloading {key}...')
            client.download_file(bucket_name, key, f'{video_dir}/{key}')
    print('Done')

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if args.upload:
        print("Uploading new guitar videos...")
        upload()
    if args.restore:
        print("Restoring guitar videos...")
        restore()
