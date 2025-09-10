# Backend (Flask)

## Setup
1. Create virtualenv and install requirements:
   ```
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Run:
   ```
   export FLASK_APP=app.py
   flask run
   ```
   Or: `python app.py` for a demo run (it will create sqlite db `app.db`).

## Tests
```
pytest
```