from django.db import models
from jsonfield.fields import JSONField


class UserCache(models.Model):
    aiml_kernel = models.CharField(max_length=1024*100)


class RequestCache(models.Model):
    cache_id = models.CharField(max_length=100)
    cache = JSONField()
    user = models.ForeignKey(UserCache, on_delete=models.CASCADE, null=True)
