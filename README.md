Django-Requestlog
=================

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=muehlemann-popp_requestlog&metric=alert_status)](https://sonarcloud.io/dashboard?id=muehlemann-popp_requestlog) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=muehlemann-popp_requestlog&metric=coverage)](https://sonarcloud.io/dashboard?id=muehlemann-popp_requestlog) ![PyPi](https://img.shields.io/pypi/v/django-requestlog.svg) 

Middleware who logs each request with their headers and the body into to PostgreSQL for diagnostic purposes. 


Why Logging to the database?
----------------------------
Logging to the database instead of to a logfile has the advantage that it can be 
searched by people not having access to the server logs. Of course this only works 
for low traffic sites. And I recommend to purge those logs regularly with the provided 
manage command or celery task.

What is logged?
---------------

The log is written to the table `requestlog_requestlog`.

* timestamp
* client IP address
* django user-id
* method
* URL
* header fields
* cookies
* query parameter
* POST body
* HTTP status code
* the first 1024 of the response

Credits
-------
Based on https://github.com/ASKBOT/django-request-logging


Settings
--------

Request logging has to be explicitely enabled (for performance reasons):

    REQUEST_LOGGING_ENABLED = True
    
You can ask the service to ignore certain fields from the querystring and the header. You do this by setting
the name of the fields in the Django settings variable `REQUEST_LOGGING_HIDE_PARAMETERS`. For example like this:

    REQUEST_LOGGING_HIDE_PARAMETERS = [ 'HTTP_AUTHORIZATION', 'password' ]

Filter certain IPs (e.g. internal Kubernetes health check requests)

    REQUEST_LOGGING_IGNORE_IPS = [ '10.2.3.4' ]

Filter certain paths by Regex (including query string):

    REQUEST_LOGGING_IGNORE_PATHS = [ '/admin/login' ]

Purge old entries
-----------------

You can use the following management command which deletes entries older than 3 days:

    ./manage.py requestlog_purge

Or you trigger the task with Celery beat by adding a shared task to your projects task list:

    
In your settings: 

    CELERY_BEAT_SCHEDULE = {
        ...    
        'requestlog.tasks.delete_old_requestlog_entries': {
            'task': 'requestlog.tasks.delete_old_requestlog_entries',
            'schedule': crontab(hour=2, minute=0)
            'args': (30,) # This is the number of days to keep the entries 
        },
    }
    
