# Resilience

Resilience is a wrapper around functions that may fail. It's designed for **cloud platforms where 'transient' errors may occur** - ie, errors where the only way to is to simply re-try the failed function.

It was developed for Google App Engine, where the urlfetch service, data store, and blob store may all occasionally fail with a varety of exceptions which, according to their Python docstrings, are simple failures where the operation should be retried.

Resilience adds:

- A **specific set of exceptions** to catch  
- An **amount of retries** considered acceptable
- **Whether the operation is critical** - ie, the app should raise the exceptions if the retries are exhaused, or simply log that exceptions were exhausted and continue on. 
- **Delay time** between retries
- **Delay multiplier** after each retry
- **What to log** during each failure

If you have a lot of work to do, and aren't particularly interested if one fails due to a transient 'docstring says try again' type errors with the data store, blob store, or whatever else. 

**Unexpected Exceptions - ie those not explicitly mentioned - will be raised normally**. If something unanticipated is happening with your app, you should know about it.

## Who uses Resilience?

Resilience is currently used in [Google Engage](http://google.com/engage), [YouTube WorldView](http://youtube.com/worldview) and [Android Ambassador](http://android-ambassador.appspot.com/).

## I'm an AppEngine user. What kind of exceptions can I use resilience for?

The following exceptions are common use cases for resilience:

### Adding something to a queue:

    import taskqueue.TransientError

### Writing to the datastore:
    
DataStoreError

    from google.appengine.api.datastore_errors import Error as DataStoreError

APIError

    from google.appengine.runtime.apiproxy_errors import Error as APIError

For Django Non-rel users: DatabaseError

    from django.db import DatabaseError

### Using the urlfetch service

    from google.appengine.api import urlfetch
    urlfetch.DeadlineExceededError
    urlfetch.DownloadError

## Examples

#### Adding something to a queue
###### Before

    my_task = taskqueue.Task(url=some_url, method='GET')
    my_queue.add(my_task)

###### With Resilience

    my_task = taskqueue.Task(url=some_url, method='GET')
    try_something_unreliable(
        my_queue.add,
        function_args = [ my_task ],
        tolerated_errors = (taskqueue.TransientError, ),
        log_prefix = "Couldn't give coupons to agent, retrying:"
    )

#### Doing some data store work

###### Before

    my_datastore_function()

###### With Resilience
    try_something_unreliable(
        my_datastore_function,
        tolerated_errors = (APIError, DataStoreError, DatabaseError),
        log_prefix = '''Error when doing my datastore work. Will retry. Error was:''',
        retries = 5, 
        delay = True,
        critical = False,
    )


##### Using the URLFetch service

###### Before

    urlfetch.fetch(urlfetch_kwargs)

###### With Resilience

    try_something_unreliable(
        urlfetch.fetch,
        function_kwargs = urlfetch_kwargs,
        tolerated_errors = (urlfetch.DeadlineExceededError, urlfetch.DownloadError ),
        log_prefix = """URLFetch exceeded deadline, but I won't let it bother me. Error was:""", 
        retries = 3, 
        delay = True,
        critical = True,
    )

## Using resilience via a decorator

Resilience lets developers use their own judgement about what errors are acceptable for individual functions, what timeouts should be, delays, etc.

Once you know exactly how you want to handle those errors, we encourage you to wrap resilience in your own decorator. For example:


