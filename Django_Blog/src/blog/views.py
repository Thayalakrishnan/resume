from django.views import generic
from django.shortcuts import render
from django.contrib import messages
from .models import Post


class BlogPostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blogindex.html'

class BlogPostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'

