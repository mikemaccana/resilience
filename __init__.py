import sys
import traceback
import logging
import time
import inspect

def run_resilient(function, function_args=[], function_kwargs={}, tolerated_errors=(Exception,), log_prefix='Something failed, tolerating error and retrying: ', retries=5, delay=True, critical=False, initial_delay_time=0.1, delay_multiplier = 2.0):
    """Run the function with function_args and function_kwargs. Warn if it excepts, and retry. If retries are exhausted, 
    log that, and if it's critical, properly throw the exception """
    
    def show_exception_info(log_prefix):
        """Warn about an exception with a lower priority message, with a text prefix and the error type"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        traceback_text = lines[2]
        logging.info(log_prefix + traceback_text)
        return
    
    delay_time = initial_delay_time
    while retries:
        retries -= 1
        try:
            return function(*function_args, **function_kwargs)
        except tolerated_errors, error: #IGNORE:W0703
            # One of our anticipated errors happened.
            if retries:
                # We've got more retries left. Log the error, and continue.
                show_exception_info(log_prefix)
                if delay:
                    time.sleep(delay_time)
                    delay_time = delay_time * delay_multiplier
                else:
                    delay_time = 0

                logging.info('We have %d tries left. Delaying for %.2f seconds and trying again.', retries, delay_time)    
            else:
                logging.warn('Could not complete action after %d retries.', retries)   
                if critical:
                    logging.error('Critical action failed.')
                    raise error 
        except Exception:
            # We've recieved an error we didn't anticipate. This is bad. 
            # Depending on the error we the developers should either fix something, or, if we want to tolerate it, 
            # add it to our tolerated_errors.
            # Those things require human judgement, so we'll raise the exception.                       
            logging.exception('Unanticipated error recieved!') #Log the exception
            raise #Re-raise
        except:
            typ, value, unused = sys.exc_info()
        
            # We've received an exception that isn't even an Exception subclass! 
            # This is bad manners - see http://docs.python.org/tutorial/errors.html: 
            # "Exceptions should typically be derived from the Exception class, either directly or indirectly."
            logging.exception("Bad mannered exception. Class was: %s Value was: %s Source file: %s", typ.__name__, str(value), inspect.getsourcefile(typ))
            raise
            
