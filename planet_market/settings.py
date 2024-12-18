"""Django settings for planet_market project."""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from env.py
env_file = os.path.join(BASE_DIR, "env.py")
env_path = Path(env_file)
# read the env.py file if it exists, windsurf helped with this
if env_path.exists():
    with env_path.open("r", encoding="utf-8") as file:
        exec(file.read())

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
# FIX DEBUG IS FALSE
DEBUG = False

if DEBUG:
    # Always include local development hosts
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
else:
    # Allowed hosts did not like using environment variables
    # Error 400 Bad Request so used plain values
    ALLOWED_HOSTS = [
        "8000-dutchmims-planetmarket-bpjhkysy2er"
        + ".ws.codeinstitute-ide.net",
        "planet-market-ef36a376b17d.herokuapp.com",
    ]

# Add production hosts if they exist
PRODUCTION_HOST_CI = os.getenv(
    "PRODUCTION_HOSTS_CI",
    "8000-dutchmims-planetmarket-bpjhkysy2er"
    + ".ws.codeinstitute-ide.net")
PRODUCTION_HOSTS_HEROKU = os.getenv(
    "PRODUCTION_HOSTS_HEROKU",
    "planet-market-ef36a376b17d.herokuapp.com")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # added
    "django.contrib.sitemaps",  # added
    "django_extensions",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "home",
    "products",
    "bag",
    "checkout",
    "profiles",
    "newsletter",  # new
    "crispy_forms",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "planet_market.urls"

# Crispy Forms Settings
CRISPY_TEMPLATE_PACK = "bootstrap4"  # version 4 not 5.

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates", "allauth"),
            os.path.join(BASE_DIR, "newsletters", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "bag.contexts.bag_contents",
                # to handle sitename in meta tags
                "home.context_processors.site_name",
            ],
            "builtins": [
                "crispy_forms.templatetags.crispy_forms_tags",
                "crispy_forms.templatetags.crispy_forms_field",
            ],
        },
    }
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Allauth settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Additional Allauth Settings
ACCOUNT_LOGIN_BY_CODE_REQUIRED = False  # stops email on login
ACCOUNT_LOGOUT_ON_GET = False  # Requires POST request to logout
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True

WSGI_APPLICATION = "planet_market.wsgi.application"

# CSRF Settings
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    PRODUCTION_HOST_CI,
    PRODUCTION_HOSTS_HEROKU
]

# Session Settings
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Test Runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Test Password Hasher (Faster)
PASSWORD_HASHERS = [
    # Fast password hashing for tests
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Once this tip was mentioned, it made sense to add this
# Local development settings
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Heroku
    DATABASES = {
        "default":
        dj_database_url.parse(os.getenv("DATABASE_URL"))
    }

# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# AWS settings
if not DEBUG and "USE_AWS" in os.environ:
    # Cache control
    AWS_S3_OBJECT_PARAMETERS = {
        "Expires": os.getenv("AWS_S3_EXPIRES"),
        "CacheControl": os.getenv(
            "AWS_CACHE_CONTROL",
            "max-age=94608000"),
    }

    # Bucket Config
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_TLD_DOMAIN = os.getenv("AWS_S3_TLD_DOMAIN")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_TLD_DOMAIN}"

    # Static and media files
    STATICFILES_STORAGE = "custom_storages.StaticStorage"
    STATICFILES_LOCATION = "static"
    DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"
    MEDIAFILES_LOCATION = "media"

    # Override static and media URLs in production
    STATIC_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/"
    )
    MEDIA_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"
    )
else:
    # Local development settings
    STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    DEFAULT_FILE_STORAGE = (
        "django.core.files.storage.FileSystemStorage"
    )

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Stripe
FREE_DELIVERY_THRESHOLD = 85
STANDARD_DELIVERY_PERCENTAGE = 10
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WH_SECRET = os.getenv("STRIPE_WH_SECRET", "")

# Email settings
# With some tips, managed to understand how django sends emails
EMAILSERVICE = 3

if EMAILSERVICE == 1:
    # Zero configuration needed
    # Emails print directly to EMAILSERVICE
    # Perfect for local development
    # Built into Django

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif EMAILSERVICE == 2:
    # Simple setup
    # Saves emails as files
    # Good for debugging
    # No external services needed
    # Built into Django

    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.getenv(
        "EMAIL_FILE_PATH",
        "tmp/email-messages/")

elif EMAILSERVICE == 3:
    # I used Gmail SMTP and an app password
    # Windsurf helped with backend configuration
    EMAIL_BACKEND = "planet_market.email_backend.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Mailchimp Settings
# Works locally, but not on heroku
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
MAILCHIMP_REGION = os.environ.get('MAILCHIMP_REGION')
MAILCHIMP_LIST_ID = os.environ.get('MAILCHIMP_LIST_ID')
