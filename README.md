Requestlog
==========

[![pipeline status](https://gitlab.com/mpom/requestlog/badges/master/pipeline.svg)](https://gitlab.com/mpom/requestlog/commits/master) [![coverage report](https://gitlab.com/mpom/requestlog/badges/master/coverage.svg)](https://gitlab.com/mpom/requestlog/commits/master)


Middleware who logs each request with their headers and the body into the database. 


Why Logging to the database?
----------------------------
Logging to the database instead of to a logfile has the advantage that it can be 
searched by people not having  access to the server logs. Of course this only works 
for low traffic sites. 

The log is written to the table `requestlog_requestlog`.

The body field is truncated at 1024 bytes.

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

In `myapp/tasks.py`

    from celery import shared_task
    
    @shared_task
    def delete_old_requestlog_entries():
        from requestlog.utils import delete_old_entries
        delete_old_entries(older_than_days=14)
    
In your settings: 

    CELERY_BEAT_SCHEDULE = {
        ...    
        'myapp.tasks.delete_old_requestlog_entries': {
            'task': 'myapp.tasks.delete_old_requestlog_entries',
            'schedule': crontab(hour='0', minute='0'),        
        }
    }
    
