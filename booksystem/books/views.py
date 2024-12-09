from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BorrowRecord
from .forms import BookForm, CustomUserEditForm
from django.utils import timezone
from django.db.models import Q  # For complex queries
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model


# Check if user is an admin
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def all_users(request):
    User = get_user_model()  # Retrieve the custom user model
    users = User.objects.all().order_by('username')  # Fetch all users

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')

        if user_id and user_type:
            try:
                user = User.objects.get(id=user_id)
                if user_type == 'admin':
                    user.is_superuser = True
                    user.is_staff = True
                else:
                    user.is_superuser = False
                    user.is_staff = False
                user.save()
            except User.DoesNotExist:
                pass  # Handle user not found

    return render(request, 'books/all_users.html', {'users': users})



def home(request):
    return HttpResponse("Welcome to the Book System!")


# List all books
def book_list(request):
    query = request.GET.get('q')  # Get the search term from the query parameters
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            available=True
        ).order_by('-registered_date')
    else:
        books = Book.objects.filter(available=True).order_by('-registered_date')

    return render(request, 'books/book_list.html', {'books': books, 'query': query})


# List books for user with personalization
def book_list_user(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            available=True
        ).order_by('-registered_date')
    else:
        books = Book.objects.filter(available=True).order_by('-registered_date')

    return render(request, 'books/book_list_user.html', {'books': books, 'query': query, 'user': request.user})

# List available books
def available_books(request):
    books = Book.objects.filter(available=True).order_by('-registered_date')
    return render(request, 'books/available_books.html', {'books': books})

# Register a new book
@login_required
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
@login_required
def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})


# Delete a book
@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# Borrow a book
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        if book.available:
            BorrowRecord.objects.create(book=book, borrower_name=request.user.username)
            book.available = False
            book.save()
            return redirect('book_list_user')
    return render(request, 'books/borrow_book.html', {'book': book, 'user': request.user})


# Return a book
@login_required
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

    return render(request, 'books/return_book.html', {'book': book, 'borrow_record': borrow_record, 'user': request.user})


# List borrowed books (admin and users)
def borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True)
    return render(request, 'books/borrowed_books.html', {'borrowed_books': borrowed_books})


@user_passes_test(is_admin)
def borrowed_books_admin(request):
    borrowed_books = BorrowRecord.objects.select_related('book').all()

    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        status = request.POST.get('status')

        if record_id and status:
            record = get_object_or_404(BorrowRecord, id=record_id)

            if status == 'returned':
                # Call the mark_as_returned method
                record.mark_as_returned()
            elif status == 'borrowed':
                # Reset the return date and mark the book as unavailable
                record.return_date = None
                record.book.available = False
                record.book.save()
                record.save()

        # Redirect to avoid form resubmission
        return redirect('borrowed_books_admin')

    return render(request, 'books/borrowed_books_admin.html', {'borrowed_books': borrowed_books})


@login_required
def borrowed_books_user(request):
    borrowed_books = BorrowRecord.objects.filter(
        borrower_name=request.user.username, return_date__isnull=True
    )
    return render(request, 'books/borrowed_books_user.html', {'borrowed_books': borrowed_books, 'user': request.user})


# View Profile (Role-based)
@login_required
def view_profile(request):
    if request.user.is_staff:
        return render(request, 'books/profile_view.html', {'user': request.user})
    else:
        return render(request, 'books/profile_view_user.html', {'user': request.user})


# Edit Profile (Role-based)
@login_required
def edit_profile(request):
    if request.user.is_staff:
        return handle_profile_edit(request, 'books/profile_edit.html', 'view_profile')
    else:
        return handle_profile_edit(request, 'books/profile_edit_user.html', 'view_profile')


# Helper function for handling profile editing
def handle_profile_edit(request, template_name, redirect_view_name):
    user = request.user

    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password")
            confirm_password = form.cleaned_data.get("confirm_password")

            if password:
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    update_session_auth_hash(request, user)
                else:
                    form.add_error('confirm_password', 'The two passwords do not match.')

            return redirect(redirect_view_name)
    else:
        form = CustomUserEditForm(instance=user)

    return render(request, template_name, {'form': form})
