import argparse
import os
import boto3
from website_generation.photo_album.config import Config
from website_generation.photo_album.photo_album_filesystem import resize_image

bucketname = 'braedonmcdonaldblogpostassets'
assets_root = 'images/posts'
posts_root = 'html/posts'

def make_parser():
    parser = argparse.ArgumentParser(
        description='Tool for uploading and restoring blog post assets from digital ocean spaces',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--upload', action='store_true',
        help='Upload blog post assets to cloud bucket, skipping ones that have already been uploaded'
    )
    group.add_argument(
        '-r', '--restore', action='store_true',
        help='Restore blog post assets stored in the cloud to local dir'
    )
    return parser

def make_client():
    config = Config()
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name='tor1',
        endpoint_url='https://tor1.digitaloceanspaces.com',
        aws_access_key_id=config.api_access_key,
        aws_secret_access_key=config.api_secret_key
    )

def upload():
    client = make_client()
    post_names = [post.replace('.html', '') for post in os.listdir(posts_root)]

    for post_name in post_names:
        print(f'Uploading assets for {post_name}')
        assets_path = os.path.join(assets_root, post_name)
        non_resized_assets = [asset for asset in os.listdir(assets_path) if '_resized' not in asset]

        for asset in non_resized_assets:
            root, ext = os.path.splitext(asset)
            resized_asset_name = root + '_resized' + ext
            if not os.path.exists(os.path.join(assets_root, post_name, resized_asset_name)):
                print(f'    Resizing {asset}')
                resize_image(os.path.join(assets_root, post_name), asset)

        cloud_assets = client.list_objects_v2(Bucket=bucketname, Prefix=post_name)
        local_assets = os.listdir(assets_path)

        if set(local_assets) == set(cloud_assets):
            print('    Nothing to upload')
        else:
            for asset in local_assets:
                asset_path = os.path.join(assets_path, asset)
                if asset not in cloud_assets:
                    print(f'    Uploading {asset}')
                    client.upload_file(asset_path, bucketname, f'{post_name}/{asset}', ExtraArgs={'ACL': 'public-read'})
    print('Done')

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if args.upload:
        print('Uploading blog assets...')
        upload()