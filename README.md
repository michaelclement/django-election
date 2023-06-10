# Django Election
A little Django web app based on the stock Django polls example. It's meant to 
facilitate small group elections or other polling scenarios. 
Security isn't really a concern.

Voting is enabled through the use of one-time tokens. Admins create tokens in the backend
and then distribute them to voters. Each voter can vote one time using a unique token.

## Structure
- `election/`: the main Django application
- `polls/`: the polls application

## Creating Voter Tokens

1. Navigate to `http://localhost:8000/admin/` and log in
2. Under the section labeled **POLLS > Tokens**, click on **Add**
3. On the **Add token** form insert a new token value and optionally
a memo. Then click **SAVE**

The new token may be distributed and used to vote a single time.

## Creating Poll/Election Questions

1. Navigate to `http://localhost:8000/admin/` and log in
2. Under the section labeled **POLLS > Questions**, click on **Add**
3. On the **Add question** form fill out the required fields and 
click **SAVE**

The new question will automatically display along with its choices 
when the user navigates to the vote screen. 

After users have voted, results can be viewed at 
`http://localhost:8000/polls/results/`

## Running the Application Locally

### 0. Set Up a Virtual Environment (Recommended)

It is recommended that you create a virtual environment before installing
the python dependencies. To do so, run:

```bash
python -m venv django_venv
```

After creating the virtual environment, activate it:

```bash
source django_venv/bin/activate
```

### 1. Install Dependencies

Install the dependencies listed in the requirements.txt file at the root of
the project by running:

```bash
pip install -r requirements.txt
```

### 2. Initialize the Database

Set up the database to support poll/election questions and the token system:

```bash
python manage.py migrate
```

Then, add an admin user:

```bash
python manage.py createsuperuser
```

### 3. Start the Django Server

Begin running the Django development server and access it from your browser:

```bash
python manage.py runserver
```

Then navigate to `http://localhost:8000/polls/`

### 4. Access the Admin Interface

The admin interface lets you create voting tokens and survey questions as well
as view data about responses. 

To access it, navigate to `http://localhost:8000/admin/` and then log in with username and password created in step 2.
