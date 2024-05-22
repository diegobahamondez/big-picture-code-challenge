# FIXME
FROM python:3.9-slim

ENV DEBUG=0
ENV SECRET_KEY="c@+y14)i9f+h%tk!zuyql_h*y*=@efc=*3-apz2fc_=pffe0xo"
ENV DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver"]
