alias g := generate

generate:
    sudo rm -rf generated
    venv/bin/python scripts/generate_site.py

serve:
    #!/usr/bin/env bash
    cd generated
    ../venv/bin/python -m http.server