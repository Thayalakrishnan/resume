from .import views
from django.urls import path
from .models import Post

urlpatterns = [
    path('', views.BlogPostList.as_view(), name='blogindex'),
    path('<slug:slug>/', views.BlogPostDetail.as_view(), name='post_detail'),
]