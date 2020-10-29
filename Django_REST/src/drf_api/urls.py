from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from core.views import PostView, PostCreateView, PostListCreateView
from nba import views
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from rest_framework import routers

from django.conf.urls.static import static




router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewSet)


urlpatterns = [
    path('grappelli/', include('grappelli.urls')), # grappelli URLS
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('create/', PostCreateView.as_view(), name='create'),
    path('list-create/', PostListCreateView.as_view(), name='list-create'),
    path('api/token/', obtain_auth_token, name='obtain-token'),
    path('nba/',include('nba.urls')),
    url('^api/', include(router.urls)),
    url('', views.index, name='players'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)