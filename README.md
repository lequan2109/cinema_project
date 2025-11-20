# Django Cinema Management (UI Only)

## Quickstart
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Notes
- Business logic is all on UI routes under `/manage/*` for staff.
- Set a user as staff either via Django admin or DB, or create Profile with role `STAFF`.
