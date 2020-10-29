from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic

# cataglog view searches the databse for all book instances and returns a the
# instances of the books. 
def catalogindex(request):
    # get counts of our object instances
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # get counts of the books that are available
    # remember that we set the book status to 'a' if its available   
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # count all the authors 
    num_authors = Author.objects.count()
    num_genre = Genre.objects.count()
    
    # session stuff
    # number of visists to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context={
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre':num_genre,
        'num_visits': num_visits,
    }
    
    return render(request, 'catalogindex.html', context=context)


# class-based view for our book list
class BookListView(generic.ListView):
    model=Book
    paginate_by = 3

class BookDetailView(generic.DetailView):
    model=Book

class AuthorListView(generic.ListView):
    model=Author
    paginate_by=3

class AuthorDetailView(generic.DetailView):
    model = Author
