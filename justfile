alias g := generate

generate:
    sudo rm -rf generated
    venv/bin/python scripts/generate_site.py

serve:
    #!/usr/bin/env bash
    cd generated
    ../venv/bin/python -m http.server

edit:
    venv/bin/python scripts/photo_albums_gui.py 

upload:
    venv/bin/python scripts/manage_photo_albums.py --upload

backup:
    venv/bin/python scripts/manage_photo_albums_db.py --backup

