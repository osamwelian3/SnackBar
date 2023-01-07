from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from catalog.models import Category, Product
import json
from django.core import serializers
from SnackBar import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from pathlib import Path
import os
import re

User = get_user_model()

# Create your views here.
def login_view(request):
    next = request.GET.get('next')
    if request.user.is_authenticated:
        if next is not None:
            return redirect(next)
        return redirect(reverse('dashboard'))
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if next is not None:
                    return redirect(next)
                return redirect(reverse('dashboard'))
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def dashboard(request, template_name="home/index.html"):
    return render(request, template_name, locals())

@login_required
def add_product(request, template_name='home/add_product.html'):
    if not request.user.is_staff:
        logout(request)
        return redirect(reverse('login', args='Login with a staff account to be able to add products'))
    if request.method == 'POST':
        print(request.POST)
        print(request.POST.get('slug'))
        from slugify import slugify
        product = Product.objects.create(
            user = User.objects.get(id=request.user.id),
            name = request.POST.get('name'),
            slug = slugify(request.POST.get('name')) if request.POST.get('slug') == '' or request.POST.get('slug') is None else request.POST.get('slug'),
            brand = request.POST.get('brand'),
            sku = request.POST.get('sku'),
            price = float(request.POST.get('price')),
            old_price = float(request.POST.get('old-price')) if request.POST.get('old-price') != '' else 0.00,
            image = '',
            thumbnail = '',
            image_caption = request.POST.get('caption'),
            quantity = int(request.POST.get('quantity')),
            description = request.POST.get('description'),
            meta_keywords = request.POST.get('meta-keywords'),
            meta_description = request.POST.get('meta-description')
        )
        print(request.FILES)
        upload = test_upload(request, product)
        upload_image(request, product)
        if 'success' in upload:
            print('upload success')
            print(request.POST.getlist('categories'))
            cats = Category.objects.filter(pk__in=[int(x) for x in request.POST.getlist('categories')])
            product = Product.objects.get(name=product.name)
            product.categories.set(request.POST.getlist('categories'))
            product.save()
            return redirect(reverse('my_products'))
    categories = Category.objects.all()

    return render(request, template_name, locals())

@login_required
def activate_product(request, product_slug):
    if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Operation not allowed'})
    product = ''
    try:
        product = Product.objects.get(slug=product_slug)
    except Exception as e:
        return JsonResponse({'error': 'can\'t activate/deactivate this product because '+ str(e) +''})

    if product.user.id == request.user.id:
        msg = ''
        if product.is_active:
            product.is_active = False
            msg = 'deactivated'
        else:
            product.is_active = True
            msg = 'activated'
        product.save()
        return JsonResponse({'success': msg})
    return JsonResponse({'error': 'can\'t activate/deactivate this product'})

@login_required
def update_product(request, product_slug):
    if not request.user.is_staff:
        logout(request)
        return redirect(reverse('login', args='Login with a staff account to be able to add products'))
    
    if request.method == 'POST':
        print(request.POST)
        print(request.POST.get('slug'))
        print('type of price ++++++++++++++++++++++++++')
        price = request.POST.get('price')
        from slugify import slugify
        product = Product.objects.get(slug=product_slug)
        product.name = request.POST.get('name'),
        product.slug = slugify(request.POST.get('name')) if request.POST.get('slug') == '' or request.POST.get('slug') is None else request.POST.get('slug'),
        product.brand = request.POST.get('brand'),
        product.sku = request.POST.get('sku'),
        product.price = float(price),
        product.old_price = float(request.POST.get('old-price')) if request.POST.get('old-price') != '' else 0.00,
        product.image_caption = request.POST.get('caption'),
        product.quantity = int(request.POST.get('quantity')),
        product.description = request.POST.get('description'),
        product.meta_keywords = request.POST.get('meta-keywords'),
        product.meta_description = request.POST.get('meta-description')
        product.save()
        
        print(request.FILES)
        if request.POST.get('image') != "":
            upload_image(request, product)
        if request.POST.get('thumbnails') != "":
            upload = test_upload(request, product)
            if 'success' in upload:
                print('upload success')
                print(request.POST.getlist('categories'))
                cats = Category.objects.filter(pk__in=[int(x) for x in request.POST.getlist('categories')])
                product = Product.objects.get(name=product.name)
                product.categories.set(request.POST.getlist('categories'))
                product.save()
                return redirect(reverse('my_products'))
    product = Product.objects.get(slug=product_slug)
    categories = Category.objects.filter(is_active=True)
    return render(request, "home/update_product.html", locals())

@login_required
def add_category(request, template_name='home/add_product.html'):
    if not request.user.is_staff:
        logout(request)
        return redirect(reverse('login', args='Login with a staff account to be able to add products'))
    
    if request.method == 'POST':
        print(request.POST)
        print(request.META.get('HTTP_X_REQUESTED_WITH'))
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        meta_keywords = request.POST.get('metakeywords')
        meta_description = request.POST.get('metadescription')
        is_active = True
        print(str(name) + ' ' + str(slug) + ' ' + str(description) + ' ' + str(meta_keywords) + ' ' + str(meta_description))
        if Category.objects.filter(name=name).exists():
            response = JsonResponse({'error': 'Category already exists'})
            return response
        category = Category(user=User.objects.get(id=request.user.id), name=name, slug=slug, description=description, is_active=is_active, meta_keywords=meta_keywords, meta_description=meta_description)
        category.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            categories = Category.objects.all()
            data = serializers.serialize('json', categories)
            struct = json.loads(data)
            data = json.dumps(struct[0])
            return JsonResponse({'categories': struct})
        
    categories = Category.objects.all()

    return render(request, template_name, locals())

@login_required(login_url='login')
def my_products(request, template_name='home/my_products.html'):
    categories = Category.objects.all()
    products = Product.objects.filter(user=request.user.id)
    return render(request, template_name, locals())

# Playground
def upload_image(request, product):
    from PIL import Image
    import glob
    if request.method == 'POST':
        file = request.FILES
        try:
            os.makedirs(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/').absolute()))
        except FileExistsError:
            pass
        img = Image.open(file.get('image'))
        x = float(request.POST.get('x-axis'))
        y = float(request.POST.get('y-axis'))
        width = float(request.POST.get('width'))
        height = float(request.POST.get('height'))
        cropped = img.crop((x, y, x+width, y+height))
        cropped = cropped.convert('RGB')
        cropped.save(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/').absolute())+'/'+ product.name +'.jpg')
        url = glob.glob(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/').absolute())+'/*.jpg', recursive=False)[0]
        product = Product.objects.get(name=product.name)
        product.image = url.split('media')[1].replace('/', '', 1)
        product.save()
    

def test_upload(request, product):
    from django.core.files.storage import FileSystemStorage
    if request.method == 'POST':
        files = request.FILES
        print(files)
        num_uploads = len(files.getlist('thumbnails'))
        print('numfiles '+str(num_uploads))
        import glob
        num_files = 0
        url_list = []
        for f in glob.iglob(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute())+'/**/*.jpg', recursive=True):
            num_files += 1
        for r in range(1,(num_uploads+1)):
            l = r-1
            if not os.path.isfile(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute())+'/'+'thumb-'+str(r)+'.jpg'):
                from PIL import Image
                try:
                    os.makedirs(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute()))
                except FileExistsError:
                    pass
                print(l)
                img = Image.open(files.getlist('thumbnails')[l])
                x = float(request.POST.get('x-axis'+str(r)))
                y = float(request.POST.get('y-axis'+str(r)))
                width = float(request.POST.get('width'+str(r)))
                height = float(request.POST.get('height'+str(r)))
                cropped = img.crop((x, y, x+width, y+height))
                cropped = cropped.convert('RGB')
                cropped.save(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute())+'/'+'thumb-'+str(r)+'.jpg')
                if l == (num_uploads-1):
                    break;
                l += 1
        slots = 4-num_files
        if slots == 0:
            return {'error': 'No free slots. Delete some thumbnail images to upload new ones. You have used all your 4 slots for this product.'}
        if num_uploads > slots:
            uploaded = slots
            for f in glob.iglob(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute())+'/**/*.jpg', recursive=True):
                url_list.append(f.split('SnackBar')[1].replace('/', '', 1))
            product = Product.objects.get(name=product.name)
            product.thumbnail = url_list
            product.save()
            return {'success': 'Added only {} thumbnail images. You are allowed 4 slots and {} are already used. Delete some to make space for new uploads'.format(uploaded, num_files)}
        else:
            uploaded = num_uploads
            for f in glob.iglob(str(Path.joinpath(settings.BASE_DIR, f'media/products/{request.user.username}/{product.name}/thumbnails/').absolute())+'/**/*.jpg', recursive=True):
                url_list.append(f.split('media')[1].replace('/', '', 1))
            product = Product.objects.get(name=product.name)
            product.thumbnail = url_list
            product.save()
            return {'success': 'Added {} thumbnail images.'.format(uploaded)}

def delete_thumbnail(request, product_slug, pos):
    product = Product.objects.get(slug=product_slug)

    # remove file from file storage
    path = str(Path.joinpath(settings.BASE_DIR, 'media/'+product.thumbnail[pos]))
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    thumb = product.thumbnail
    thumbnail = thumb.copy()
    thumbnail.pop(int(pos))
    product.thumbnail = thumbnail
    product.save()
    return JsonResponse({'success': 'thumbnail image deleted'})

# from PIL import Image

# img = Image.open('/home/samian/Desktop/IanUbuntu/Downloads/WhatsApp Image 2022-02-22 at 10.16.38 AM.jpeg')
# x = 316.3840316993858
# y = 320.7766412914743
# width = 487.7054755664634
# height = 487.7054755664634
# cropped = img.crop((x, y, x+width, y+height))
