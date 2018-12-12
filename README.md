Requestlog
==========

Middleware who logs each request with their headers and the body into the database. 


Why Logging to the database?
----------------------------
Logging to the database instead of to a logfile has the advantage that it can be 
searched by people not having  access to the server logs. Of course this only works 
for low traffic sites. 

The log is written to the table `requestlog_requestlog`.

The body field is truncated at 1024 bytes.


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
