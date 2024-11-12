# will create braedonmcdonald.ca on remote if it doesn't exist
# -a for archive (preserve permissions and copy recursively) -P to show progress 
# use --dry-run to test things

rsync -aP --delete *.html style.css images posts braedonmcdonald.ca:/var/www/braedonmcdonald.ca
