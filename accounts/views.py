from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from SnackBar.serializer import UserSerializer
from django.contrib.auth.models import User



# Create your views here.
@api_view(['GET'])
@ensure_csrf_cookie
def setCsrfCookie(request):
    return JsonResponse({"Success": "Cookies Set"})

@csrf_protect
@api_view(['POST'])
def signup(request):
    data = request.data
    try:
        username = data['username']
        password = data['password']
        email = data['email']
        password2 = data['password2']

        if User.objects.filter(username=username).exists():
            return Response({'Error': 'Username is already taken'})
        else:
            if len(username) < 3:
                return Response({'Error': 'Username can\'t have less than three initials'})
            else:
                if password != password2:
                    return Response({'Error': 'Passwords do not match'})
                else:
                    if len(password) < 6:
                        return Response({'Error': 'Password must be atleast 6 characters'})
                    else:
                        user = User.objects.create_user(username=username, email=email, password=password)
                        user.is_active = False
                        user.save()

                        send_mail("Verification Code", "This is your test verification code: 1234", 'no-reply@snackbar.com', [email])

                        user = User.objects.get(username=username)
                        user = UserSerializer(user)
                        return Response({ "data": user.data })
    except Exception as e:
        print('Exception: '+ str(e))
        return Response({"Error": "Something went wrong trying to sign you up. Contact osamwelian3@gmail.com"})
