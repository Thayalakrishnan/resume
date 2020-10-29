from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model

class Tag(models.Model):
    name = models.CharField(max_length=30,unique=True)
    description = models.TextField(default="")
    '''
    tag_graphic = models.ImageField()
    '''
    
    def __str__(self):
        return self.name


class EditingTool(models.Model):
    name = models.CharField(max_length=30,unique=True)
    description = models.TextField(default="")
    '''
    editingtool_graphic = models.ImageField()
    '''
    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=30,unique=True)
    description = models.TextField(default="")
    '''
    equipment_graphic = models.ImageField()
    '''
    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(max_length=100)
    overview = models.TextField(default='')
    description = models.TextField(default='')
    slug = models.SlugField(unique=True)
    starred = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        return reverse('', kwargs={'slug': self.slug})
    
    def get_create_url(self):
        return reverse('album-create', kwargs={'slug': self.slug})
    
    def get_update_url(self):
        return reverse('album-update', kwargs={'slug': self.slug})
    
    def get_delete_url(self):
        return reverse('album-delete', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Album, self).save(*args,**kwargs)


class Picture(models.Model):
    title = models.CharField(max_length=200)
    picture = models.ImageField(unique=True)
    slug = models.SlugField(unique=True)
    date = models.DateField(
        default=timezone.now,
        verbose_name="Date of Picture"
        )
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(default='')
    description = models.TextField(default='')
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, blank=True, null=True)
    starred = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag,default='', blank=True)
    equipment_used = models.ForeignKey(Equipment,default='', on_delete=models.SET_NULL, blank=True, null=True)
    editing = models.ForeignKey(EditingTool,default='', on_delete=models.SET_NULL, blank=True, null=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('picture-detail', kwargs={'slug': self.slug})
        
    def get_create_url(self):
        return reverse('picture-create', kwargs={'slug': self.slug})
        
    def get_update_url(self):
        return reverse('picture-update', kwargs={'slug': self.slug})
        
    def get_delete_url(self):
        return reverse('picture-delete', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Picture, self).save(*args,**kwargs)