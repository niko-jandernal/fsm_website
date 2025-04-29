# Register your models here.
from django.contrib import admin
from .models import Image
from .models import Album

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    list_filter  = ('owner',)
    search_fields = ('title', 'owner__username')


admin.site.register(Image)