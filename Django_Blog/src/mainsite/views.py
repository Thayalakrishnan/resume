from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.views.generic import View
from itertools import chain
import blog.models
import posts.models
import catalog.models
from posts.models import Post
from gallery.models import Picture
from django.db.models import Count, Q


class IndexView(View):
    def get(self,request, *args, **kwargs):
        starred = Picture.objects.filter(starred=True).order_by('-timestamp')[0:3]
        featured = Post.objects.filter(featured=True).order_by('-timestamp')[0:3]
        latest = Post.objects.order_by('-timestamp')[0:3]
        context = {
            'object_list': featured,
            'starred': starred
        }
        return render(request, 'index.html', context)

def base(request):
    return render(request, 'base.html')

class SearchView(View):
    def get(self, request, *args, **kwargs):
        blog_queryset = blog.models.Post.objects.all()
        posts_queryset = posts.models.Post.objects.all()
        catalog_queryset = catalog.models.Book.objects.all()
        query = request.GET.get('q')
        blog_filter = Q(title__icontains=query) | Q(slug__icontains=query)
        post_filter = Q(title__icontains=query) | Q(slug__icontains=query)
        catalog_filter = Q(title__icontains=query) | Q(summary__icontains=query)
        if query:
            blog_queryset = blog_queryset.filter(blog_filter).distinct()
            posts_queryset = posts_queryset.filter(post_filter).distinct()
            catalog_queryset = catalog_queryset.filter(catalog_filter).distinct()
            queryset = [blog_queryset,posts_queryset,catalog_queryset]
        
        context = {
            'queryset':queryset,
            'blog_queryset':blog_queryset,
            'catalog_queryset':catalog_queryset,
            'posts_queryset':posts_queryset
        }
        return render(request, 'search_results.html', context)

class JumboView(View):
    def get(self,request, *args, **kwargs):
        featured = Post.objects.filter(featured=True).order_by('-timestamp')[0:3]
        context = {
            'object_list': featured,
        }
        return render(request, 'index.html', context) 


'''
class PostListView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'queryset'
    paginate_by = 1
    
    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] =category_count
        return context
'''