from django.urls import path, include
from .views import PostView, PostCreateView, PostListCreateView, PostListView, PostDetailView

''' 
core app is able to render post list and post create views using the rest framework and fetch urls properly
this is not yet possible in our nba app
'''

app_name = 'core'

urlpatterns = [
    path('', PostView.as_view(), name='test'),
    path('create/', PostCreateView.as_view(), name='create'),
    path('list-create/', PostListCreateView.as_view(), name='list-create'),
    path('post-detail/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post-list/', PostListView.as_view(), name='post-list'),
]