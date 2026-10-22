from django.contrib import admin
from .models import Unit, Report, AuditEvent

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display=('code','kind','lat','lng','busy')
    list_editable=('lat','lng','busy')
    list_filter=('kind',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('folio','updated')
    search_fields=('folio',)
    readonly_fields=('updated',)

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display=('id','t','st','d','sha')
    readonly_fields=('t','st','d','p','h','sha')
    def has_add_permission(self,request): return False  # solo la API crea eventos (cadena verificable)
    def has_change_permission(self,request,obj=None): return False
