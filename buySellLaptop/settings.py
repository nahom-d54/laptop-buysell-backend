from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-8p6te)s!5%98r)jtlct08os3%lbh(c$ab+g*)w!s-z40bv@!d6"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

PRODUCTION = os.getenv("ENV") == "production"


ALLOWED_HOSTS = ["127.0.0.1"]

ALLOWED_HOSTS += os.getenv("ALLOWED_HOSTS", "").split(",")


# Application definition

if PRODUCTION:
    DEBUG = False

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            }
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
            "laptops": {  # Replace 'my_app' with your app name
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname}: {asctime} {module} {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file": {
                "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": os.path.join(BASE_DIR, "logs/django.log"),
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": True,
            },
            "laptops": {  # Replace 'my_app' with your app name
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "phonenumber_field",
    "laptops",
    "users",
    "storages",
]

AUTH_USER_MODEL = "users.CustomUser"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

# Optional: Simple JWT settings (customize as needed)


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Lifetime of access tokens
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),  # Lifetime of refresh tokens
    "ROTATE_REFRESH_TOKENS": True,  # Rotates refresh tokens
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklists old refresh tokens
    "ALGORITHM": "HS256",  # Algorithm for token encoding
    "SIGNING_KEY": SECRET_KEY,  # Secret key for signing tokens
    "AUTH_HEADER_TYPES": ("Bearer",),  # Authorization header prefix
}


TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_SESSIONS = os.getenv("TELEGRAM_SESSIONS")
TELEGRAM_CHANNELS = os.getenv("TELEGRAM_CHANNELS", "").split(",")
SCHEDULE_INTERVAL = os.getenv("SCHEDULE_INTERVAL", 20)

GEMENI_API_KEY = os.getenv("GEMENI_API_KEY", "").split(",")


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "buySellLaptop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "buySellLaptop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# custom fields

STATIC_URL = "/static/"
MEDIA_URL = "/media/"


if PRODUCTION:
    print("Running in production")
    FTP_HOST = os.getenv("FTP_SERVER")
    FTP_USERNAME = os.getenv("FTP_USERNAME")
    FTP_PASSWORD = os.getenv("FTP_PASSWORD")

    ASSETS_URL = os.getenv("ASSETS_URL")
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.ftp.FTPStorage",
            "OPTIONS": {
                "location": f"ftp://{FTP_USERNAME}:{FTP_PASSWORD}@{FTP_HOST}:21/",
                "base_url": ASSETS_URL,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.ftp.FTPStorage",
            "OPTIONS": {
                "location": f"ftp://{FTP_USERNAME}:{FTP_PASSWORD}@{FTP_HOST}:21/",
                "base_url": ASSETS_URL,
            },
        },
    }

    db_from_env = dj_database_url.config(conn_max_age=600)
    DATABASES["default"].update(db_from_env)

    #
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    MIDDLEWARE = ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE
