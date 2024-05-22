## How to run this code:

# install python

www.python.org

# install Django and dependencies

pip install django
pip install isbnlib
pip install requests
pip install python-dotenv
pip install bs4

# setup database (just using sqlite for simplicity)

python manage.py makemigrations
python manage.py migrate

# run the server
python manage.py runserver
