# books/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BorrowRecord
from .forms import BookForm
from django.utils import timezone
from django.db.models import Q  # For complex queries
from django.contrib.auth.decorators import login_required  # To ensure only logged-in users can access
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserEditForm
from django.contrib.auth import update_session_auth_hash


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

    # Pass the user to the template
    return render(request, 'books/book_list_user.html', {'books': books, 'query': query, 'user': request.user})



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
    return render(request, 'books/borrow_book.html', {'book': book,'user': request.user})


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
    return render(request, 'books/return_book.html', {'book': book, 'borrow_record': borrow_record,'user': request.user})

def borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True)  # Books currently borrowed
    return render(request, 'books/borrowed_books.html', {'borrowed_books': borrowed_books})

# Borrowed books user
def borrowed_books_users(request):
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True)  # Books currently borrowed
    return render(request, 'books/borrowed_books_user.html', {'borrowed_books': borrowed_books,'user': request.user})

# View Profile
# View Profile (Role-based Routing)
@login_required
def view_profile(request):
    if request.user.is_staff:
        return render(request, 'books/profile_view.html', {'user': request.user})  # Admin profile view
    else:
        return render(request, 'books/profile_view_user.html', {'user': request.user})  # Normal user profile view


# Edit Profile (Role-based Routing)
@login_required
def edit_profile(request):
    if request.user.is_staff:
        return handle_profile_edit(request, 'books/profile_edit.html', 'view_profile')  # Admin profile edit
    else:
        return handle_profile_edit(request, 'books/profile_edit_user.html', 'profile_view_user')  # Normal user profile edit


# Helper function for handling profile editing
def handle_profile_edit(request, template_name, redirect_view_name):
    user = request.user

    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()

            # Handle password change
            password = form.cleaned_data.get("password")
            confirm_password = form.cleaned_data.get("confirm_password")

            if password:
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    update_session_auth_hash(request, user)  # Keep user logged in
                else:
                    form.add_error('confirm_password', 'The two passwords do not match.')

            return redirect(redirect_view_name)
    else:
        form = CustomUserEditForm(instance=user)

    return render(request, template_name, {'form': form})
