from django.apps import AppConfig


class TimeLoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_time_logs'
    label = 'time_logger'
