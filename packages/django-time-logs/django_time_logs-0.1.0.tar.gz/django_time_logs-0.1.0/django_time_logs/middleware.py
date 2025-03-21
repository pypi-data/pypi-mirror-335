import time

from django_time_logs.utils import time_logger

class TimeLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = time.perf_counter()

        http_method = request.method
        path_info = request.path_info
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        end_time = time.perf_counter()
        duration = round((end_time - start_time), 2)
        time_logger(title=f"{path_info} ({http_method})", duration=duration)
        return response