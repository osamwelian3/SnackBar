from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=32, default='')
    last_name = models.CharField(max_length=32, default='')
    other_name = models.CharField(max_length=32, default='')
    email = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=13, default='')
    city = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'UserProfile'

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name
