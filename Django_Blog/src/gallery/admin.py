from django.contrib import admin
from .models import Picture, Album, Tag, EditingTool, Equipment


admin.site.register(Album)
admin.site.register(Tag)
admin.site.register(EditingTool)
admin.site.register(Equipment)
admin.site.register(Picture)
