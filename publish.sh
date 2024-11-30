# will create braedonmcdonald.ca on remote if it doesn't exist
# -a for archive (preserve permissions and copy recursively) -P to show progress 
# use --dry-run to test things

chmod -R 555 generated
rsync -aP --delete generated/ braedonmcdonald.ca:/var/www/braedonmcdonald.ca
