from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from SnackBar.serializer import UserSerializer
from SnackBar.tokens import account_activation_token
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout



# Create your views here.
@api_view(['GET'])
@ensure_csrf_cookie
def setCsrfCookie(request):
    return JsonResponse({"Success": "Cookies Set"})

@csrf_protect
@api_view(['GET'])
def isAuthenticated(request):
    if not request.user.is_authenticated:
        return Response({'Detail': 'Not authenticated.'})
    else:
        return Response({'Detail': 'User is authenticated ' + str(request.user.username)})

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

                        current_site = get_current_site(request)
                        mail_subject = 'Activate your account.'
                        message = render_to_string('email_template.html', {
                                    'user': user,
                                    'domain': current_site.domain,
                                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                    'token': account_activation_token.make_token(user),
                                })
                        try:
                            send_mail(mail_subject, message, 'no-reply@snackbar.com', [email])
                        except Exception as e:
                            print('Send_Mail_Exception: ' + str(e))
                            return Response({'Detail': 'Account created but couldn\'t send activation email. Please contact admin at osamwelian3@gmail.com'})

                        # send_mail("Verification Code", "This is your test verification code: 1234", 'no-reply@snackbar.com', [email])

                        user = User.objects.get(username=username)
                        user = UserSerializer(user)
                        return Response({ "data": user.data })
    except Exception as e:
        print('Sign_up Exception: '+ str(e))
        return Response({"Error": "Something went wrong trying to sign you up. Contact osamwelian3@gmail.com"})

@api_view(['GET'])
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        response = render_to_string('redirect.html', { 'success': 'Thank you for your email confirmation. Now you can login your account.', 'site_url': str(request.scheme)+ '://' +str(get_current_site(request))})
        return HttpResponse(response)
    else:
        return Response({'Failed': 'Activation link is invalid!'})

@csrf_protect
@api_view(['POST'])
def signin(request):
    try:
        data = request.data
        username = data['username']
        password = data['password']

        if len(username) < 1 and len(password) < 1:
            return Response({'Error': 'Please provide username and password.'})
        else:
            if not User.objects.filter(username=username).exists():
                return Response({'Error': 'User with that user name does not exist.'})
            else:
                user = authenticate(username=username, password=password)
                if not User.objects.get(username=username).is_active:
                    return Response({'Detail': 'You have not activated your account. Check your email for a link to activate your account.'})
                else:
                    if user is not None:
                        login(request, user)
                        return Response({'Success': 'Login successful'})
                    else:
                        return Response({'Failed': 'Invalid credentials...'})
    except Exception as e:
        print('Sign_in Exception' + str(e))
        return Response({'Error': 'Something went wrong trying to sign you in. Contact osamwelian3@gmail.com'})

@csrf_protect
@api_view(['GET'])
def log_out(request):
    try:
        if not request.user.is_authenticated:
            return Response({'Detail': 'You are already logged out'})
        else:
            logout(request)
            return Response({'Success': 'Logout success.'})
    except Exception as e:
        print('Log_out Exception' + str(e))
        return Response({'Error': 'Something went wrong trying to log you out. Contact osamwelian3@gmail.com'})

@csrf_protect
@api_view(['GET'])
def delete_account(request, username):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        if User.objects.filter(username=username).exists():
            if user.is_superuser or user.is_staff:
                User.objects.filter(username=username).delete()
                return Response({'success': 'User account succesfuly deleted'})
            else:
                return Response({'perm-error': 'Your user rights dont allow you to perform this action. Login as an administrator'})
        else:
            return Response({'error': 'User does not exist'})
    else:
        return Response({'error': 'sign in to perform this action'})
