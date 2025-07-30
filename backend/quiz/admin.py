from django.contrib import admin

from .models import User,Form,Categorie,Question,Choices,Terminal

admin.site.register(User)
admin.site.register(Form)
admin.site.register(Choices),
admin.site.register(Question)
admin.site.register(Categorie)
admin.site.register(Terminal)


