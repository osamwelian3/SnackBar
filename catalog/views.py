from django.shortcuts import get_object_or_404, render
from . import serializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category, Product
from SnackBar import settings

# Create your views here.
@api_view(['GET'])
def product_index(request):
    context = {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
    }
    products = Product.objects.all()
    products = serializer.ProductSerializer(products, many=True)
    return Response({'success': 'success', 'products': products.data, 'context': context})

@api_view(['GET'])
def category_index(request):
    context = {
        'site_name': settings.SITE_NAME,
        'meta_keywords': settings.META_KEYWORDS,
        'meta_description': settings.META_DESCRIPTION,
    }
    categories = Category.objects.all()
    categories = serializer.CategorySerializer(categories, many=True)
    return Response({'success': 'success', 'categories': categories.data, 'context': context})

@api_view(['GET'])
def show_category(request, category_slug):
    c = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = c.product_set.filter(is_active=True)
    category = serializer.CategorySerializer(c)
    c_product = serializer.ProductSerializer(products, many=True)
    return Response({'success': 'success', 'category': category.data, 'products': c_product.data})

@api_view(['GET'])
def show_product(request, product_slug):
    p = get_object_or_404(Product, slug=product_slug, is_active=True)
    categories = p.categories.filter(is_active=True)
    product = serializer.ProductSerializer(p)
    categories = serializer.CategorySerializer(categories, many=True)
    return Response({'success': 'success', 'product': product.data, 'categories': categories.data})

@api_view(['POST'])
def test_upload(request):
    from django.core.files.storage import FileSystemStorage
    if request.method == 'POST':
        files = request.FILES
        print(files)
        num_uploads = len(files.getlist('thumb'))
        import os
        import glob
        from pathlib import Path
        dir_path = Path.joinpath(settings.BASE_DIR, 'build/static/media/products/thumbnails/').absolute()
        loop = 1
        num_files = 0
        for f in glob.iglob(str(Path.joinpath(settings.BASE_DIR, 'build/static/media/products/thumbnails/').absolute())+'/**/*.jpg', recursive=True):
            num_files += 1
        print('existing files are ' + str(num_files))
        for r in range(1,5):
            l = r-1
            if not os.path.isfile(str(Path.joinpath(settings.BASE_DIR, 'build/static/media/products/thumbnails/').absolute())+'/'+'thumb-'+str(r)+'.jpg'):
                from PIL import Image
                img = Image.open(files.getlist('thumb')[l])
                x = 316.3840316993858
                y = 320.7766412914743
                width = 487.7054755664634
                height = 487.7054755664634
                cropped = img.crop((x, y, x+width, y+height))
                cropped.save(str(Path.joinpath(settings.BASE_DIR, 'build/static/media/products/thumbnails/').absolute())+'/'+'thumb-'+str(r)+'.jpg')
                if l == (num_uploads-1):
                    break;
                l += 1
        slots = 4-num_files
        if slots == 0:
            return Response({'error': 'No free slots. Delete some thumbnail images to upload new ones. You have used all your 4 slots for this product.'})
        if num_uploads > slots:
            uploaded = slots
            return Response({'success': 'Added only {} thumbnail images. You are allowed 4 slots and {} are already used. Delete some to make space for new uploads'.format(uploaded, num_files)})
        else:
            uploaded = num_uploads
            return Response({'success': 'Added {} thumbnail images.'.format(uploaded)})

@api_view(['GET'])
def delete_image(request, filename):
    import os
    import glob
    from pathlib import Path
    dir_path = Path.joinpath(settings.BASE_DIR, 'build/static/media').absolute()
    print(settings.BASE_DIR)
    for file in glob.iglob(str(Path.joinpath(settings.BASE_DIR, 'build/').absolute())+'/**/*.jpg', recursive=True):
        if filename in file:
            print(file)
            os.remove(file)
    return Response({'success'})
