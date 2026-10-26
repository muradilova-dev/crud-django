from django.db import models
from django.urls import reverse


class Item(models.Model):
    """Универсальная модель для CRUD. Поля легко заменить под своё задание."""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('crud:detail', args=[self.pk])
