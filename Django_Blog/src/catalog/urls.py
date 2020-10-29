from django.urls import path
from . import views

urlpatterns=[
    path('', views.catalogindex, name='catalogindex'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('authors/<pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]

#response = MyView.as_view()(request)

