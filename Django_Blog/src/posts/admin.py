from django.contrib import admin
from .models import Author, Category, Post


admin.site.register(Author)
admin.site.register(Category)


class PostInLine(admin.TabularInline):
    model = Post
    fields = ('title', 'slug', 'featured', 'thumbnail',)
    fk_name = 'previous_post'
    fk_name = 'next_post'
    extra=0

#@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp', 'slug', 'featured', 'thumbnail')
    list_filter = ('featured', 'timestamp')
    inlines = [PostInLine]

admin.site.register(Post, PostAdmin)
