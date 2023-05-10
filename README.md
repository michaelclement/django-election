# django-election
A little Django web app meant to facilitate elections for ACM and other small groups. Security isn't really a concern.

## Structure
- `election/`: the main Django application
- `polls/`: the polls application
- `django_venv/`: virtual environment for development

## Development

**0. Set Up a Virtual Environment (Recommended)**

It is recommended that you create a virtual environment before installing
the python dependencies. To do so, run:

- `python -m venv django_venv`

After creating the virtual environment, activate it:

- `source django_venv/bin/activate`

**1. Install Dependencies**

Install the dependencies listed in the requirements.txt file at the root of
the project by running:

- `pip install -r requirements.txt`

**2. Start the Django Server**

Begin running the Django development server and access it from your browser:

- `python manage.py runserver`
- Navigate to: `http://localhost:8000/polls/`

**3. Access the Admin Interface**

The admin interface lets you create voting tokens and survey questions as well
as view data about responses. To access it:

- Navigate to: `http://localhost:8000/admin/`
- Log in with username `admin` and password `password`
