import os, dj_database_url
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
B=Path(__file__).resolve().parent.parent
env=os.environ.get
SECRET_KEY=env('SECRET_KEY','dev-insecure-change-me')
DEBUG=env('DEBUG','0')=='1'
if not DEBUG and SECRET_KEY=='dev-insecure-change-me':
    raise ImproperlyConfigured('Define SECRET_KEY en el entorno antes de desplegar sin DEBUG.')
ALLOWED_HOSTS=env('ALLOWED_HOSTS','localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS=[o for o in env('CSRF_TRUSTED_ORIGINS','').split(',') if o]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF='drivetec.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='drivetec.wsgi.application'
DATABASES={'default':dj_database_url.config(default='sqlite:///'+str(B/'db.sqlite3'))}
LANGUAGE_CODE='es-mx'; TIME_ZONE='America/Tijuana'; USE_TZ=True
STATIC_URL='/static/'; STATIC_ROOT=B/'staticfiles'
STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/admin/login/'
if env('HTTPS')=='1':
    SESSION_COOKIE_SECURE=CSRF_COOKIE_SECURE=SECURE_SSL_REDIRECT=True
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https'); SECURE_HSTS_SECONDS=31536000
GOOGLE_MAPS_KEY=env('GOOGLE_MAPS_KEY','')      # clave de navegador (restringir por referrer)
GOOGLE_SERVER_KEY=env('GOOGLE_SERVER_KEY','')  # clave de servidor (nunca se envía al cliente)
WHISPER_MODEL=env('WHISPER_MODEL','')          # transcripción en servidor con faster-whisper ('base','small'...; vacío = solo navegador)
WHISPER_DEVICE=env('WHISPER_DEVICE','cpu')     # 'cpu' o 'cuda'
WHISPER_COMPUTE=env('WHISPER_COMPUTE','int8')  # 'int8','int8_float16','float16'
