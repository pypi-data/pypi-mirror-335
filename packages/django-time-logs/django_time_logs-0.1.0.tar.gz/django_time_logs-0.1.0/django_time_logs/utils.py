import time
from django.utils import timezone
from django.conf import settings
from elasticsearch_dsl.connections import connections

try:
    index_name = settings.TIME_LOGGER_INDEX
except:
    index_name = None


def get_elastic_client():
    """Returns an Elasticsearch client instance"""
    try:
        es_settings = settings.ELASTICSEARCH_DSL['default']
        connections.configure(
            default=es_settings,
        )
        return connections.get_connection()
    except Exception as e:
        print(f'Failed to generate elastic client: {e}')


# Option 1: For functions
def time_taken(function):
    """Track how long a function take to execute"""
    def track(*args, **kwargs):
        start_time = time.perf_counter()
        f = function(*args, **kwargs)
        end_time = time.perf_counter()
        duration = round((end_time - start_time), 2)
        time_logger(title=function.__name__, duration=duration)
        return f
    return track


# Option 2: For class views
def time_taken_class_view(cls):
    """Track how long a class view takes to execute"""
    original_dispatch = cls.dispatch
    
    def new_dispatch(self, *args, **kwargs):
        start_time = time.perf_counter()
        result = original_dispatch(self, *args, **kwargs)
        end_time = time.perf_counter()
        duration = round((end_time - start_time), 2)
        time_logger(title=f"{cls.__name__}/{original_dispatch.__name__}", duration=duration)
        return result
    
    cls.dispatch = new_dispatch
    return cls


# Option 3: For MiddleWare
# Check middleware.py



def time_logger(title, duration):
    """Log the function name and the duration to elastic search

    Args:
        title (str): Function name
        duration (float): duration in seconds describing how log the function takes to run
    """
    try:
        data = {
            "title": title,
            "duration": duration,
            "created": timezone.now().isoformat()
        }

        es_client = get_elastic_client()
        if not index_name:
            return
        response = es_client.index(
                    index=index_name,
                    body=data
                )
    except Exception as e:
        print(f'Failed to generate time_logger: {e}')