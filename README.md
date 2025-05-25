# braedonmdonald.ca

This repository contains the source code used to generate my personal website.
It does not use an off the shelf static site generator. Instead it has custom
Python scripts used for backing up photo albums to the cloud and then using
those cloud links to generate webpages for each album. The rest of the pages
are mostly hand coded html except for the header and navigation links which
are inserted using a template library.

Right now I'm using Web Hosting Canada for the domain name, and Digital Ocean
for the virtual private server and object storage. 

The rest of the readme is mostly notes for myself.

# Project setup

Read the entire section before starting! These are the steps for setting up the project on a new machine or after a fresh git clone.

* requires Python 3.12
* Install Live Server VS Code extension
* run `python -m venv venv` to make a new virtual environment then run `source venv/bin/activate`
* run `pyton -m pip install -r requirements.txt` in the root of the project
* run `python -m pip install -e .` in the root of the project to install local website generation library such that the source can be edited
* In the `src/website_generation` directory make a copy of `config.template.py` in
  same directory and call it `config.py`
  * Change the `project_root` string in `AbstractConfig` to the absolute path
    of where the project was cloned
  * Set the access key and secret key for the obect storage API. You'll have to make a new access key in the Spaces and Object Storage tab in Digital Ocean.
* run `python scrips/manage_photo_albums_db.py --restore`
* run `python scripts/manage_photo_albums.py --restore`
* run `python scrips/manage_guitar_videos.py --restore`
* Bring up build tasks again and run `restore guitar videos`

VERY IMPORTANT: add an ssh config for braedonmcdonald.ca so that `publish.sh` doesn't try to connect the cloudflare proxy
```
Host braedonmcdonald.ca
    HostName <find ip on Digital Ocean account>
		User root
		IdentityFile ~/.ssh/<identity file>
```

# Server setup

install nginx and vim 
```
sudo apt-get install nginx
sudo apt-get install vim
```

start nginx
```
sudo systemctl start nginx
```

start nginx on boot
```
sudo systemctl enable nginx
```

copy the configuration into `/etx/nginx/sites-available/braedoncmdonald.conf`
```
server {
	listen 80;
	listen [::]:80;

	root /home/braedonmcdonald/braedonmcdonald.ca;
	index index.html;

	location / {
		try_files $uri $uri/ =404;
	}
}
```

link the configuration to `sites-enabled`
```
sudo ln -s /etc/nginx/sites-available/braedonmcdonald.conf /etc/nginx/sites-enabled/
```

remove the default configuration from `sites-enabled`

reload nginx
```
sudo systemctl reload nginx
```

# Running Unit Tests

Run `pytest` from project root.

# Using The Scripts

The `website_generation` folder contains scripts for backing up photo albums,
backing up guitar videos, and generating the website's html files. The scripts 
are based around three things: The local filesystem, a local SQLite database,
and a few cloud based object storage buckets. Photo albums backed up to the 
cloud must be present in the local filesystem (in the directory set in the 
config) for certain script operations to work. The database is used by 
`generate_site.py` to construct photo cloud links and put them in the right 
order.

## manage_photo_albums.py

This script is used to restore and upload photo albums to and from the root 
directory set in `Config`. Albums are uploaded with 
`manage_photo_albums.py --upload` and restored with 
`manage_photo_albums.py --restore`.

### Uploading an album

When making a new photo album, the directory must 
have to following format: the name of the album with dashes instead of spaces
followed by an underscore with a start date of the form `%b-%Y` or `Y` and an
optional following of an end date of the same form. 

When `manage_photo_albums.py --upload` is run, the script loops through each 
subfolder of `Config.photo_albums_root`. Photos in an album are resized as 
copies before all the photos (resized and non resized) are uploaded to the 
object storage bucket of `Config.photo_albums_bucket`. Photos that are already
present in the local database will not be re-uploaded. Album information (if 
it is new) and photo information will be added to the local database.

Don't forget to backup the database using the `manage_photo_albums_db.py`

### Restoring albums

Restoring albums is less intelligent than uploading in that it won't try to 
skip restoring photos that are already present in the database. Instead it 
restores everything, overwriting files that are already present. Photos in any 
of the albums that are not present in the local database are removed. Any 
albums that are not present in the local database will also be removed.

Before restoring albums it's important to always restore the local database 
first.

## manage_photo_albums_db.py 

This script is used to restore and backup the local SQLite database set in 
`Config.photo_albums_db_path` to and from the bucket set in 
`AbstractConfig.db_backup_bucket`. The database is backed up with
`manage_photo_albums_db.py --upload` where the file is uploaded with a 
timestamp instead of its original filename for its key. The database is 
restored with `manage_photo_albums_db.py --restore` where it uses the 
timestamps to restore the most recently backed up file. 

## generate_site.py

This script the Jinja templates to generate the website. It uses the local 
database to populate the `photo_albums_list.html` page with links and generates
a page for each photo album. The photo albums are simple top down lists of the 
images.

## photo_albums_gui.py 

Running this will open a graphical window. On the left is a list of photo album
titles. Selecting from the list will show the albums photos. From there the 
photos can be rearranged and the save button will become active. Clicking the
save button will save the new order in the local database so that the next 
call the `generate_site.py` will reflect the new order.

## publish.sh

This script simply copies the generated html files to the server.

## Manual testing

First make a directory called `test-data-source` in the root of the project
then run the `reset_test_env.py` script to set up an environment that allows
for manual testing. From there, some scripts support the `--test` flag for 
manual testing.

Scripts that support the flag:
* `manage_photo_albums.py`
* `photo_albums_gui.py`
* `generate_site.py`
