from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='first name')
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='last name')
    # No additional fields needed for now, but you can add any time you need


class mytest(models.Model):
    val1 = models.EmailField(max_length=100)
    val2 = models.DateTimeField(auto_now_add=True)
    val3 = models.CharField(max_length=100)
    val4 = models.TextField()
    val5 = models.TextField()
    session = models.CharField(max_length=100, default='default_session')
    class Meta:
        db_table = 'chatpro_collection' 
        