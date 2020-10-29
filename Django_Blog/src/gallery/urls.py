from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views


from gallery.views import (
    IndexView,
    PictureListView,
    PictureDetailView,
    PictureCreateView,
    PictureUpdateView,
    PictureDeleteView,
)

urlpatterns = [
    path('', IndexView.as_view(), name='gallery-index'),
    path('list/', PictureListView.as_view(), name='picture-list'),
    path('create/', PictureCreateView.as_view(), name='picture-create'),
    path('<slug:slug>/', PictureDetailView.as_view(), name='picture-detail'),
    path('<slug:slug>/update/', PictureUpdateView.as_view(), name='picture-update'),
    path('<slug:slug>/delete/', PictureDeleteView.as_view(), name='picture-delete'),
]
