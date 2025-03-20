from django.contrib import admin

from dbsettings.models import Setting

class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'value')
    search_fields = ('key', 'description', 'value')
    ordering = ('key',)

admin.site.register(Setting, SettingAdmin)
