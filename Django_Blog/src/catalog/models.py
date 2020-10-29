from django.db import models
from django.urls import reverse 
import uuid

# genre model
# will store information about the book caregory
# non-fiction, ficion etc 
class Genre(models.Model):
    name=models.CharField(max_length=200, help_text='Enter a book genre:')
    
    def __str__(self):
        return self.name

# book model
# this model represents a book , however it does not represent a specific copy
# of a book (like a physical book), just the book itself
class Book(models.Model):
    title=models.CharField(max_length=200)
    author=models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary=models.TextField(max_length=1000, help_text='Enter a brief description of the Book')
    isbn=models.CharField(
        'ISBN',
        max_length=13,
        help_text='13 Chacter <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre=models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language=models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        # generate a string for genre
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = 'Genre'

# book instance model
# represenets a specific copy of a book that can be borrewed out
# inlucdes information abouty the book, including when it will be avaiable and
# its current borrwed status 
class BookInstance(models.Model):
    id=models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text='Unique ID for this particular book in the library')
    book=models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint=models.CharField(max_length=200)
    due_back=models.DateField(null=True, blank=True)
    
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    
    status=models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book Availibility'
        )
    
    class Meta:
        ordering = ['due_back']
        
    def __str__(self):
        return f'{self.id} ({self.book.title})'

# author model
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class Language(models.Model):
    name=models.CharField(
        max_length=200,
        unique=True,
        help_text='Enter the Language'
        )
    
    def __str__(self):
        return self.name

