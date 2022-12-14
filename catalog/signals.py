from django.db.models.signals import post_save,post_delete
from .models import Product
from django.dispatch import receiver
import glob
import os
from pathlib import Path
from SnackBar import settings
from django.db import models
import shutil

# @receiver(post_delete,sender=Product)
# def delete_profile(sender,instance,*args,**kwargs):
#     for f in glob.iglob(str(Path.joinpath(settings.BASE_DIR, f'build/static/media/{request.user.username}/{product.name}/products/thumbnails/').absolute())+'/**/*.jpg', recursive=True):
#         os.remove(f)
#     print("Product Deleted")

def _delete_file(path, dir):
   """ Deletes file from filesystem. """
   if os.path.isfile(path):
       os.remove(path)
       shutil.rmtree(dir, ignore_errors=True)

@receiver(models.signals.post_delete, sender=Product)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    print('image deleted')
    if instance.image:
        _delete_file(instance.image, '')

@receiver(models.signals.post_delete, sender=Product)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes thumbnail files on `post_delete` """
    print('thumbnails deleted')
    if instance.thumbnail:
        for thumbnail in instance.thumbnail:
            print(str(Path.joinpath(settings.BASE_DIR, 'media/'+thumbnail)))
            path = str(Path.joinpath(settings.BASE_DIR, 'media/'+thumbnail))
            dir = str(Path.joinpath(settings.BASE_DIR, 'media/'+thumbnail)).split('thumbnails')[0]
            _delete_file(path, dir)
