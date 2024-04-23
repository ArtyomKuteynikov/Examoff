from django.db import models
from django.db.models import Count, Q
from ckeditor.fields import RichTextField


TICKET_STATUSES = [
    (0, 'Новый'),
    (1, 'Решается'),
    (2, 'Решен')
]

TICKET_TYPES = [
    (0, 'Order'),
    (1, 'Question')
]


class FAQ(models.Model):
    title = models.CharField(max_length=128)
    text = RichTextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_faq"
        ordering = ('created',)
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
