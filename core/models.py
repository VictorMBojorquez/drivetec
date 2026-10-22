from django.db import models
class Unit(models.Model):
    code=models.CharField(max_length=10,primary_key=True); kind=models.CharField(max_length=20)
    lat=models.FloatField(); lng=models.FloatField(); busy=models.BooleanField(default=False)
class Report(models.Model):
    folio=models.CharField(max_length=20,primary_key=True); data=models.JSONField(); updated=models.DateTimeField(auto_now=True)
class AuditEvent(models.Model):  # cadena SHA-256 verificable en servidor
    t=models.CharField(max_length=40); st=models.CharField(max_length=40); d=models.TextField()
    p=models.CharField(max_length=64); h=models.CharField(max_length=64); sha=models.CharField(max_length=64)
