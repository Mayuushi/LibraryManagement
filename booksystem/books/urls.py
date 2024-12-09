from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.book_list, name='book_list'),  # List all books
    path('booklist/', views.book_list_user, name='book_list_user'),  # List all books for user
    path('new/', views.register_book, name='register_book'),  # Register new book
    path('edit/<int:pk>/', views.update_book, name='update_book'),  # Edit book
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),  # Delete book
    path('available/', views.available_books, name='available_books'),  # List available books
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),  # Borrow a book
    path('return/<int:book_id>/', views.return_book, name='return_book'),  # Return a book
    path('borrowed_books/', views.borrowed_books, name='borrowed_books'),  # All borrowed books
    path('borrowed_books_user/', views.borrowed_books_user, name='borrowed_books_user'),  # User-specific borrowed books
    path('borrowed_books/admin/', views.borrowed_books_admin, name='borrowed_books_admin'),  # Admin view of borrowed books
    path('profile/', views.view_profile, name='view_profile'),  # View profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Edit profile
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Logout
    path('admin/users/', views.all_users, name='all_users'),
    path('books/all/', views.all_books, name='all_books'),
    path('books/edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('borrowed_books/delete/<int:record_id>/', views.delete_borrow_record, name='delete_borrow_record'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
