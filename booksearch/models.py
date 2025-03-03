from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    google_book_id = models.CharField(max_length=255, unique=True)  # Google Books API のID
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255, blank=True, null=True)  # 著者情報がない場合に対応
    description = models.TextField(blank=True, null=True)  # 説明なしの本もある
    published_date = models.CharField(max_length=10, blank=True, null=True)  # YYYY 形式にも対応
    thumbnail = models.URLField(blank=True, null=True)  # サムネがない場合もある

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーとのリレーション
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # 本とのリレーション

    def __str__(self):
        return f"{self.user.username}'s favorite - {self.book.title if self.book else '削除された本'}"
