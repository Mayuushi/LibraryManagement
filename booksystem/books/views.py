# books/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BorrowRecord
from .forms import BookForm
from django.utils import timezone

def home(request):
    return HttpResponse("Welcome to the Book System!")

# List all books
def book_list(request):
    books = Book.objects.all().order_by('-registered_date')
    return render(request, 'books/book_list.html', {'books': books})

# Register a new book
def register_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
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
        form = BookForm(request.POST, instance=book)
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
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        borrower_name = request.POST.get('borrower_name')
        if book.available:
            BorrowRecord.objects.create(book=book, borrower_name=borrower_name)
            book.available = False
            book.save()
            return redirect('available_books')
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
            return redirect('available_books')
    return render(request, 'books/return_book.html', {'book': book, 'borrow_record': borrow_record})
