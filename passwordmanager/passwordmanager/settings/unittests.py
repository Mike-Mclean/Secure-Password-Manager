from .default import *

DEBUG=True
CACHE_BACKEND = "locmem://"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "unittests.db",
    },
}