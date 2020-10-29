from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Author,MembershipThrough, Category
from .forms import PostForm, CategoryFormSet,CategoryForm
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query)
            ).distinct()

        context = {
            'queryset':queryset 
        }
        return render(request, 'search_results.html', context)


def get_category_count():
    queryset= Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

def get_categories():
    queryset = Category.objects.all()
    return queryset

class IndexView(View):
    def get(self,request, *args, **kwargs):
        featured = Post.objects.filter(featured=True).order_by('-timestamp')[0:3]
        latest = Post.objects.order_by('-timestamp')[0:3]
        context = {
            'object_list': featured,
            'latest': latest
        }
        return render(request, 'post_index.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'queryset'
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] =category_count
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    
    def get_object(self):
        obj = super().get_object()
        return obj
    
    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] =category_count
        return context
    '''
    def post(self,request,*args,**kwargs):
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = self.get_object()
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'slug': post.slug
            }))
    '''

class PostCreateView(CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm
    
    def get_context_data(self, **kwargs):
        category_list = get_categories()
        data = super(PostCreateView,self).get_context_data(**kwargs)
        data['categories_list'] = category_list
        data['title'] = 'Create'
        if self.request.POST:
            data['categories']=CategoryFormSet(self.request.POST)
        else:
            data['categories']=CategoryFormSet()
        return data
    
    def form_valid(self,form):
        context = self.get_context_data()
        categories = context['categories']
        form.instance.author = get_author(self.request.user)
        self.object = form.save()
        if categories.is_valid():
            categories.instance = self.object
            categories.save()
        form.save()
        return redirect(reverse('post-detail', kwargs={
            'slug': form.instance.slug
        }))
        

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm
    
    def get_context_data(self, **kwargs):
        category_list = get_categories()
        data = super().get_context_data(**kwargs)
        data['categories_list'] = category_list
        if self.request.POST:
            data['title'] = 'Update'
            data['categories'] = CategoryFormSet(self.request.POST, instance=self.object)
        else:
            data['title'] = 'Update'
            data['categories'] = CategoryFormSet(instance=self.object)
        return data
    
    def form_valid(self,form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse('post-detail', kwargs={
            'slug': form.instance.slug,
        }))
        

class PostDeleteView(DeleteView):
    model = Post
    success_url = '/list'
    template_name = 'post_confirm_delete.html'


