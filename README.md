# A Data Application Project

## Introduction

### This is a part of take home project from xVectorLabs. The project is to create a data application that can be used to store, compute and plot graphs. The data is provided in the form of a csv file.

## NOTE: A Proper internet connection is required to run the project.

# DEMO
https://github.com/Suman2023/xvectorlabs/assets/66205793/d88515a0-df43-4b59-89fe-08e9f9c504b3

## Requirements

### The project is written in python 3.11. The following packages are required to run the project:

- Django
- pandas
- pycopg2

### The Frontend is written in Django Template and JavaScript. The following packages are provided through CDN:

- Tailwind CSS
- plotly.js

### The Database used is PostgreSQL. This can be easily done using Docker. The following steps can be used to setup the basic postgres database in Docker:

- Install Docker
- Run the following command in the terminal:

```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### However Django comes with a default database SQLite3. This can be used by changing the DATABASES variable in settings.py file.

```
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

## Installation

### The project can be installed by cloning the repository and running the following command in the terminal:

```bash
    pip install -r requirements.txt
```

### Though a better way is to use a virtual environment. The following steps can be used to create a virtual environment:

```bash
    python -m venv env
```

### To activate the virtual environment:

```bash
    source env/bin/activate
```

### Then install the requirements:

```bash
    pip install -r requirements.txt
```

### Then make a migrations file:

```bash
    python manage.py makemigrations
```

### Then migrate the database:

```bash
    python manage.py migrate
```

### Then run the server:

```bash
    python manage.py runserver
```

### Then open the browser and go to the following url:

```
    http://localhost:8000/
```

### The project has a csv file name Airline_Delay_Cause.csv. To test out the complete functionality of the project.
