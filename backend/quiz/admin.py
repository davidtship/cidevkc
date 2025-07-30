from django.contrib import admin

from .models import User,Form,Categorie,Question,Choices,Terminal,AuthorizedDevice

admin.site.register(User)
admin.site.register(Form)
admin.site.register(Choices),
admin.site.register(Question)
admin.site.register(Categorie)
admin.site.register(Terminal)


@admin.register(AuthorizedDevice)
class AuthorizedDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'device_uuid', 'label', 'created_at']
    search_fields = ['device_id', 'label']