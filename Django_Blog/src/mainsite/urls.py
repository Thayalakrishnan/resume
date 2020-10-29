from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import IndexView, base, SearchView

urlpatterns = [path('', IndexView.as_view(), name="index"),]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [path('admin/', admin.site.urls),]

urlpatterns += [path('catalog/', include('catalog.urls')),]

urlpatterns += [path('blog/', include('blog.urls')),]

urlpatterns += [path('posts/', include('posts.urls')),]

urlpatterns += [path('gallery/', include('gallery.urls')),]

urlpatterns +=[path('search/', SearchView.as_view(), name='search'),]



admin.site.site_header = "Main Site"
admin.site.site_title = "Main Site Admin Portal"
admin.site.index_title = "Main Site: Admin  "

