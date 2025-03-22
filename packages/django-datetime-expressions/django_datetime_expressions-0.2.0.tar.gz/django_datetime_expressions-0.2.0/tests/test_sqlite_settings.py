SECRET_KEY = "test-secret"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    },
}

INSTALLED_APPS = [
    "tests",
]

MIGRATION_MODULES = {
    "tests": None,
}

USE_TZ = False
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
