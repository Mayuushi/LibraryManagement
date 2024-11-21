from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    registered_date = models.DateTimeField(default=timezone.now)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.title

    def is_available(self):
        """Returns True if the book is available for borrowing."""
        return self.available


class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=200)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.borrower_name} borrowed {self.book.title}"

    def mark_as_returned(self):
        """Marks the book as returned and sets its availability."""
        self.return_date = timezone.now()
        self.book.available = True
        self.book.save()
@receiver(post_save, sender=BorrowRecord)
def update_book_availability_on_borrow(sender, instance, created, **kwargs):
    if created:
        instance.book.available = False
        instance.book.save()

@receiver(post_delete, sender=BorrowRecord)
def update_book_availability_on_delete(sender, instance, **kwargs):
    if  instance.return_date:  # Book is still borrowed
        instance.book.available = True
        instance.book.save()
