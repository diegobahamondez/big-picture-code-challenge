from django.db import models


class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    summary = models.TextField(null=True, blank=True)
    cover_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title
