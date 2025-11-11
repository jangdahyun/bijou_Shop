from pathlib import Path
import environ
from datetime import timedelta
import os
from django.urls import reverse_lazy
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR.parent / ".env")


SECRET_KEY = env("DJANGO_SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])


# Application definition

INSTALLED_APPS = [
    # 프로젝트 전용 AdminSite 사용 설정
    'config.apps.ConfigAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'accounts',
    'catalog',
    'product',
    'cart',
    'notifications',
    'order',
    'social',
    'common',
    'delivery',
    #봇 차단 캡챠
    'django_recaptcha',
    #로그인 시도 제한
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #로그인 시도 제한
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates",],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"] 
# STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.Account" # 커스텀 유저 모델 설정

# 구글 reCAPTCHA 설정
ENABLE_RECAPTCHA = env.bool("ENABLE_RECAPTCHA", default=False)
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default="")

#로그인 시도 제한 설정
AXES_FAILURE_LIMIT = 5  # 허용할 최대 로그인 실패 횟수
AXES_COOLOFF_TIME = timedelta(minutes=5)  # 로그인 제한 시간 (시간 단위)
# AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'  # 잠금 화면



#------------------- 보안 설정 -------------------#
if not DEBUG:
    # HTTPS 설정 HTTPS로 강제해 중간자 공격 방지
    SECURE_SSL_REDIRECT = True
    # 트래픽에서는 세션 쿠키가 전송되지 않도록 설정
    SESSION_COOKIE_SECURE = True
    # CORS 쿠키가 트래픽에서는 전송되지 않도록 설정
    CSRF_COOKIE_SECURE = True
    # 브라우저가 사이트를 HTTPS로만 접근하도록 지시
    SECURE_HSTS_SECONDS = 31536000  # 1년
    # 하위 도메인에도 HSTS 정책 적용
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # HSTS 정책을 브라우저에 미리 로드하도록 지시
    SECURE_HSTS_PRELOAD = True
    # 브라우저의 XSS 필터 활성화
    SECURE_BROWSER_XSS_FILTER = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0


#----------------------log설정-------------------------#
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "daily_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "when": "midnight",          # 자정마다 새 파일
            "interval": 1,
            "backupCount": 7,            # 7일치만 보관 (필요에 맞게 조절)
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["daily_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["daily_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "root": {
            "handlers": ["daily_file", "console"],
            "level": "INFO",
        },
    },
}

#------------------- 인증 백엔드 설정 -------------------#
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
#------------------- 로그인 리다이렉트 설정 -------------------#
LOGIN_REDIRECT_URL = reverse_lazy("home")

#------------------- 이메일 설정 -------------------#
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Bijou <noreply@bijou.local>")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
