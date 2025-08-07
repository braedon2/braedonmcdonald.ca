alias g := generate

generate:
    sudo rm -rf generated
    venv/bin/python scripts/generate_site.py