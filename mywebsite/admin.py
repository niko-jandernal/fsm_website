# Register your models here.
from django.contrib import admin
from .models import Image
from .models import Album
from .models import DiscussionTopic


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('title', 'owner__username')


@admin.register(DiscussionTopic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)


admin.site.register(Image)
