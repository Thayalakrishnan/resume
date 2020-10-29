from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

STATUS = (
    (0, 'DRAFT'),
    (1, 'PUBLISH')
)

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    cover = models.ImageField(upload_to='images/', default='blog\static\img\default.jpg')
    status = models.IntegerField(choices=STATUS, default = 0)
    
    class Meta:
        ordering = ['-created_on']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={
            'slug': self.slug
        })
    

def get_image_filename(instance, filename):
    id = instance.post.id
    return "images/%s" % (id)


class Images(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=get_image_filename, verbose_name='Image')