# gapminder dashboard

Dashboard for comparing countries over time.

## run

```bash
cd dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

open `http://127.0.0.1:8050/` in a browser.

## nixos

if the local venv fails with missing shared libraries, use:

```bash
cd dashboard
./run_dashboard.sh
```

## files

- `app.py`
- `data/gapminder.csv`
- `requirements.txt`
- `run_dashboard.sh`
