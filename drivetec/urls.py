from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from core import views as v
urlpatterns=[path('admin/',admin.site.urls),path('',v.index),path('config.js',v.config),path('api/state',v.state),
 path('api/geocode',v.geocode),path('api/rank',v.rank),path('api/audit/verify',v.verify),
 path('api/transcribe',v.transcribe),path('api/translate',v.translate),path('healthz',lambda r:HttpResponse('ok')),path('health',lambda r:HttpResponse('ok'))]
