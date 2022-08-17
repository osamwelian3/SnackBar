from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from SnackBar.serializer import UserProfileSerializer

# Create your views here.
@csrf_protect
@api_view(['POST'])
def update_profile(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'sign in to update your profile.'})
    else:
        data = request.data
        # Use try statement to make updating a single field possible by making them independent of each other
        try:
            first_name = data['first_name']
        except:
            first_name = ''
        try:
            last_name = data['last_name']
        except:
            last_name = ''
        try:
            other_name = data['other_name']
        except:
            other_name = ''
        try:
            email = data['email']
        except:
            email = request.user.email
        try:
            phone = data['phone']
        except:
            phone = ''
        try:
            city = data['city']
        except:
            city = ''

        str_length = len(first_name+last_name+other_name+phone+city)
        
        if str_length == 0:
            return Response({'detail': 'Can\'t update an empty profile'})
        else:
            try:
                if UserProfile.objects.filter(user=request.user).exists():
                    user_profile = UserProfile.objects.get(user=request.user)
                    user_profile.first_name = first_name
                    user_profile.last_name = last_name
                    user_profile.other_name = other_name
                    user_profile.email = email
                    user_profile.phone = phone
                    user_profile.city = city
                    # Dictionary comprehension to remove empty fields
                    data = {k: v for (k, v) in data.items() if len(v) > 0}
                    # Generate a list of fields to be updated from the data dictionary above
                    fields = [str(x) for x in data.keys()]
                    user_profile.save(update_fields=fields)
                    return Response({'success': 'Your profile was updated successfully'})
                else:
                    user_profile = UserProfile(user=request.user,first_name=first_name, last_name=last_name, other_name=other_name, email=email, phone=phone, city=city)
                    user_profile.save()
                    return Response({'success': 'Your profile was updated successfully'})
            except:
                return Response({'error': 'Something went wrong trying to update your profile'})

@csrf_protect
@api_view(['GET'])
def view_profile(request):
    try:
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user=request.user)
            user_profile = UserProfileSerializer(profile)
            return Response({'data': user_profile.data})
        else:
            return Response({'error': 'Please login to view your profile'})
    except Exception as e:
        print('View_profile Exception' + str(e))
        return Response({'error': 'Something went wrong trying to fetch your profile.'})
