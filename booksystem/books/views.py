# books/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BorrowRecord
from .forms import BookForm
from django.utils import timezone
from django.db.models import Q  # For complex queries
from django.contrib.auth.decorators import login_required  # To ensure only logged-in users can access


def home(request):
    return HttpResponse("Welcome to the Book System!")

# List all books
from django.db.models import Q

def book_list(request):
    query = request.GET.get('q')  # Get the search term from the query parameters
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            available=True  # Ensure only available books are shown
        ).order_by('-registered_date')
    else:
        books = Book.objects.filter(available=True).order_by('-registered_date')  # Only available books, no search term

    return render(request, 'books/book_list.html', {'books': books, 'query': query})

def book_list_user(request):
    query = request.GET.get('q')  # Get the search term from the query parameters
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            available=True  # Ensure only available books are shown
        ).order_by('-registered_date')
    else:
        books = Book.objects.filter(available=True).order_by('-registered_date')  # Only available books, no search term

    return render(request, 'books/book_list_user.html', {'books': books, 'query': query})


# Register a new book
def register_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

# Update book details
def update_book(request, pk):
    book = Book.objects.get(pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

# Delete a book
def delete_book(request, pk):
    book = Book.objects.get(pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# List available books
def available_books(request):
    books = Book.objects.filter(available=True).order_by('-registered_date')
    return render(request, 'books/available_books.html', {'books': books})

# Borrow a book
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        if book.available:
            # Automatically use the logged-in user's name
            BorrowRecord.objects.create(book=book, borrower_name=request.user.username)
            book.available = False
            book.save()
            return redirect('book_list_user')
    return render(request, 'books/borrow_book.html', {'book': book})


# Return a book
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrow_record = BorrowRecord.objects.filter(book=book, return_date__isnull=True).first()
    if request.method == 'POST':
        if borrow_record:
            borrow_record.return_date = timezone.now()
            borrow_record.save()
            book.available = True
            book.save()
            return redirect('borrowed_books_user')
    return render(request, 'books/return_book.html', {'book': book, 'borrow_record': borrow_record})

def borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True)  # Books currently borrowed
    return render(request, 'books/borrowed_books.html', {'borrowed_books': borrowed_books})

# Borrowed books user
def borrowed_books_users(request):
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True)  # Books currently borrowed
    return render(request, 'books/borrowed_books_user.html', {'borrowed_books': borrowed_books})
