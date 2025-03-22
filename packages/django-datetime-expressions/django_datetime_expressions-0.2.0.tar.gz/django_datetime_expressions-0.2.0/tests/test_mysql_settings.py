SECRET_KEY = "test-secret"

DATABASES = {
    "default": {
        "NAME": "django_datetime_expressions",
        "ENGINE": "django.db.backends.mysql",
        "HOST": "127.0.0.1",
        "USER": "root",
        "PASSWORD": "mysql",
        "PORT": "3306",
    }
}

INSTALLED_APPS = [
    "tests",
]

MIGRATION_MODULES = {
    "tests": None,
}

USE_TZ = False
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
