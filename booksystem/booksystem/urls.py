# booksystem/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirect root URL to books/ app
def home_redirect(request):
    return redirect('books/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),  # Include books app URLs
    path('', home_redirect),  # Redirect the root URL to /books/
]
