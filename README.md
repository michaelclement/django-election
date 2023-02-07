# django-election
A little Django web app meant to facilitate elections for ACM and other small groups. Security isn't really a concern.

## Structure
- `election/`: the main Django application
- `polls/`: the polls application
- `django_venv/`: virtual environment for development

## Development
- Start the virtual environment: `source django_venv/bin/activate`
- Start Django server: `python manage.py runserver`
- Navigate to: `http://localhost:8000/polls/` in your web browser
