# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 2
worker_class = "sync"
worker_connections = 1000
timeout = 50
keepalive = 5

# Graceful shutdown
max_requests = 1000
max_requests_jitter = 50
preload_app = False

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "do-utg-app"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in the future)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Django settings
raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings",
]

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
