from django.db import models


class AbstractDBImage(models.Model):
    path = models.CharField(max_length=255, unique=True)
    content_type = models.CharField(max_length=128)
    modified_on = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=255)
    content = models.BinaryField()

    class Meta:
        abstract = True


class DBImage(AbstractDBImage):
    pass
