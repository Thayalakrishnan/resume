from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Picture, Tag
from .forms import PictureForm
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model

class IndexView(View):
    template_name = 'gallery_index.html'
    def get(self,request, *args, **kwargs):
        starred_pictures = Picture.objects.filter(starred=True).order_by('-timestamp')[0:3]
        latest_pictures = Picture.objects.order_by('-timestamp')[0:3]
        context = {
            'starred_pictures': starred_pictures,
            'latest_pictures': latest_pictures
        }
        return render(request, 'gallery_index.html', context)


class PictureListView(ListView):
    model = Picture
    template_name = 'picture_list.html'
    context_object_name = 'queryset'
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        all_pictures = Picture.objects.order_by('-timestamp')
        all_tags = Tag.objects.all()
        context = super().get_context_data(**kwargs)
        context['most_recent'] = all_pictures
        context['page_request_var'] = "page"
        return context

class PictureDetailView(DetailView):
    model = Picture
    template_name = 'picture_detail.html'
    context_object_name = 'pic'
    
    def get_object(self):
        obj = super().get_object()
        return obj
    
    def get_context_data(self, **kwargs):
        most_recent = Picture.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        return context

class PictureCreateView(CreateView):
    model = Picture
    template_name = 'picture_create.html'
    form_class = PictureForm
    User = get_user_model()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context
    
    def form_valid(self,form):
        form.instance.author = self.request.user
        form.save()
        return redirect(reverse('picture-detail', kwargs={'slug': form.instance.slug}))

class PictureUpdateView(UpdateView):
    model = Picture
    template_name = 'picture_create.html'
    form_class = PictureForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context
    
    def form_valid(self,form):
        form.instance.author = self.request.user
        form.save()
        return redirect(reverse('picture-detail', kwargs={'slug': form.instance.slug,}))

class PictureDeleteView(DeleteView):
    model = Picture
    success_url = '/gallery'
    template_name = 'picture_confirm_delete.html'
