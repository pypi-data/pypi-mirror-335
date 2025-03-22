from datetime import datetime

from django.db import models


class Article(models.Model):
    date: datetime = models.DateTimeField(null=True)
