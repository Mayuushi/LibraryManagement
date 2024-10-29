# books/models.py
from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    registered_date = models.DateTimeField(default=timezone.now)
    available = models.BooleanField(default=True)  # Tracks book availability

    def __str__(self):
        return self.title

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=200)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.borrower_name} borrowed {self.book.title}"
