from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class GoogleSocialUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    audience = models.CharField(max_length=255)
    expiration = models.CharField(max_length=255)
    notbefore = models.CharField(max_length=255)
    issuedat = models.CharField(max_length=255)
    jwtid = models.CharField(max_length=255)
    authorizedparty = models.CharField(max_length=255)

    class Meta:
        db_table = 'GoogleSocialUser'

    def __str__(self) -> str:
        return self.user.username
