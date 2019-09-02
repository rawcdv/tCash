## Setup

### Locations (lat/long)
Locations require a spatial database and some geospatial libraries
Note: SpatiaLite extension for SQLite is recommended for local development

See the [docs](https://docs.djangoproject.com/en/2.1/ref/contrib/gis/install/)

### GeoLocation 
This is used for automatically detecting the user's location based on their ip address

See the [docs](https://docs.djangoproject.com/en/dev/ref/contrib/gis/geoip2/)

It recommends installing [libmaxminddb C library](https://github.com/maxmind/libmaxminddb) for faster speed

### Create virtualenv and install dependencies
```bash
python3 -m venv env
source env/bin/activate

pip3 install -r requirements.txt
```

### Run servers
```bash
docker run -p 6379:6379 -d redis:2.8
python3 manage.py runserver 0:8000
```

## Dev process

A project includes many apps.
Our website is a project with apps running in it.

Create new app
```bash
python3 manage.py startapp APP_NAME
```

View database
```
python3 manage.py makemigrations webapp
python3 manage.py sqlmigrate webapp 0001
```

Migrate new tables
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py migrate --run-syncdb
```

Populate db with initial data
```bash
python3 manage.py loaddata webapp/fixtures/currency-fixture.json
```