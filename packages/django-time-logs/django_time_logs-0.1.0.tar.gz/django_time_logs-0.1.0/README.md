==========================
Django-Time-Logs
==========================

A Django middleware-based application that logs the path, creation date, and duration of each request.

Features
========
- Logs the request path (URL).
- Logs the creation date and time of the request.
- Logs the duration (time taken) for the request to complete.
- Easy to integrate into any Django project.

Installation
============

1. Clone the repository or download the app::

    git clone https://github.com/Fattyk/django-time-logs.git or pip install django-time-logs

2. Add the app to your Django project's `INSTALLED_APPS` in `settings.py`::

    INSTALLED_APPS = [
        ...
        'django_time_logs',
        ...
    ]

3. Add the middleware to your `MIDDLEWARE` list in `settings.py`::

    MIDDLEWARE = [
        ...
        'django_time_logs.middleware.TimeLoggerMiddleware',
        ...
    ]

4. Include the django-time-logs URLconf in your project urls.py like this::

    path('', include('django_time_logs.urls')),


5. Start the development server and visit ``/time-logs`` for the logs.


Usage
=====

Once installed, the app will automatically log the following details for every request:

- **Path**: The URL path of the request.
- **Created Date**: The timestamp when the request was made.
- **Duration**: The time taken (in seconds) for the request to complete.

Example Log Entry
-----------------

::

    Path: /api/data/
    Created Date: 2023-10-01 12:34:56
    Duration: 0.12 seconds

Configuration
=============

You can customize the behavior of the logger by adding the following settings to your `settings.py`:
- **TIME_LOGGER_INDEX**: Define the elastic search index for the loggins if you're logging to elastic search
- **WHERE_TO_LOG_REQUEST**: Set to `ELASTIC` to log requests to a elastic search (default: `ELASTIC`). You can log to `ELASTIC` or `FILE`. Kindly note that `FILE` option is still in progress
- **TIME_LOG_TEMPLATE**: (optional). You can customize this template in `settings.py` to use your custom template.

Example::

    # settings.py
    TIME_LOGGER_INDEX = 'elastic_time_logger'
    WHERE_TO_LOG_REQUEST = ELASTIC
    TIME_LOG_TEMPLATE = 'path-to-your-template.html'

Contributing
============

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.

License
=======

This project is licensed under the MIT License. See the `LICENSE` file for details.

Author
======

Fatai Kayode Ogundele – [ogundele.fatai.k@gmail.com]

Project Link: https://github.com/Fattyk/django-time-logs