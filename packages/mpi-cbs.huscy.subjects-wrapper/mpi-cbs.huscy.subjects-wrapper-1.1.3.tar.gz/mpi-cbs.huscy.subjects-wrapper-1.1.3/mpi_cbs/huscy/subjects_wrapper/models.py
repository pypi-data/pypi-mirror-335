from django.db import models

from huscy.subjects.models import Subject


class WrappedSubject(models.Model):
    pseudonym = models.CharField(primary_key=True, max_length=12)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return self.pseudonym
