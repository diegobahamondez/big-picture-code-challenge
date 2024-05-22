# How to run this code:

## install python

www.python.org

## create virtual environment

- python3 -m venv venv
- source venv/bin/activate # On Windows use `venv\Scripts\activate`

## install Django and dependencies

pip install -r requirements.txt

## change to project directory

cd big_picture_library

## setup database migrations (using sqlite for simplicity)

python manage.py makemigrations

## implement the migrations

python manage.py migrate

## run the server

python manage.py runserver
