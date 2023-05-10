# django-election
A little Django web app meant to facilitate elections for ACM and other small groups. Security isn't really a concern.

## Structure
- `election/`: the main Django application
- `polls/`: the polls application

## Development

**0. Set Up a Virtual Environment (Recommended)**

It is recommended that you create a virtual environment before installing
the python dependencies. To do so, run:

`python -m venv django_venv`

After creating the virtual environment, activate it:

`source django_venv/bin/activate`

**1. Install Dependencies**

Install the dependencies listed in the requirements.txt file at the root of
the project by running:

`pip install -r requirements.txt`

**2. Initialize the Database**

Set up the database to support poll/election questions and the token system:

`python manage.py migrate`

Then, add an admin user:

`python manage.py createsuperuser`

**3. Start the Django Server**

Begin running the Django development server and access it from your browser:

Run:

`python manage.py runserver`

Then navigate to `http://localhost:8000/polls/`

**4. Access the Admin Interface**

The admin interface lets you create voting tokens and survey questions as well
as view data about responses. 

To access it, navigate to `http://localhost:8000/admin/` and then log in with username and password created in step 2.
