from django.urls import path

from django_time_logs.views import time_logs

# app_name = 'time_logger'

urlpatterns = (
    path('time-logs', time_logs, name='time_logs'),
)