from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from tinymce import HTMLField
from django.utils.text import slugify

User = get_user_model()

def get_categories_list():
    queryset = Category.objects.all()
    return queryset

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField()
    
    def __str__(self):
        return self.user.username

class Category(models.Model):
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title

class MembershipThrough(models.Model):
    category = models.ForeignKey(Category, related_name='membership',on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='membership',on_delete=models.CASCADE)


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = HTMLField()
    view_count = models.IntegerField(default = 0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    categories = models.ManyToManyField(Category, related_name='posts',through=MembershipThrough)
    featured = models.BooleanField()
    previous_post = models.ForeignKey('self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey('self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'slug': self.slug
        })
    
    def get_create_url(self):
        return reverse('post-create', kwargs={
            'slug': self.slug
        })
    
    def get_update_url(self):
        return reverse('post-update', kwargs={
            'slug': self.slug
        })
        
    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'slug': self.slug
        })
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args,**kwargs)


