from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.views import unmask_cipher_token
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from SnackBar.serializer import UserSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .models import GoogleSocialUser
import jwt

User = get_user_model()

# Create your views here.
@api_view(['POST'])
@csrf_protect
def socialLogin(request):
    try:
        data = request.data
        credential = data['credential']
        UserObject = jwt.decode(credential, options={"verify_signature": False})
        if GoogleSocialUser.objects.filter(jwtid=UserObject['jti']):
            return Response({'error': 'Already used token. Try again.'})
        email = UserObject['email']
        if GoogleSocialUser.objects.filter(subject=UserObject['sub']).exists():
            socialUser = GoogleSocialUser.objects.get(subject=UserObject['sub'])
            user = User.objects.get(email=email)
            socialUser.expiration = UserObject['exp']
            socialUser.notbefore = UserObject['nbf']
            socialUser.issuedat = UserObject['iat']
            socialUser.jwtid = UserObject['jti']
            
            socialUser.save()
        else:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                username = UserObject['given_name']+UserObject['family_name']
                username = username.lower()
                email = UserObject['email']
                user = User.objects.create_user(username=username, email=email, password='google-auth')
                user.is_active = True
                user.save()
        
            subject = UserObject['sub']
            audience = UserObject['aud']
            expiration = UserObject['exp']
            notbefore = UserObject['nbf']
            issuedat = UserObject['iat']
            jwtid = UserObject['jti']
            authorizedparty = UserObject['azp']
            
            socialUser = GoogleSocialUser(user=user, subject=subject, audience=audience, expiration=expiration, notbefore=notbefore, issuedat=issuedat, jwtid=jwtid, authorizedparty=authorizedparty)
            socialUser.save()

            if not user.is_active:
                user.is_active = True
                user.save()

        AuthUser = authenticate(request, username=user.username, password='google-auth')
        
        if AuthUser is not None:
            login(request, user, backend='utils.PasswordlessAuthBackend.PasswordlessAuthBackend')
            token = unmask_cipher_token(get_token(request))

            value = request.session.session_key

            request.META['CSRF_COOKIE'] = token
            # print(str(sessionkey).split(':', 1)[1])
            response = Response({'success': 'Login successful', 'username': user.username, 'csrftoken': token, 'sessionid': value}) # str(str(sessionkey).split(':', 1)[1])
            # response['Set-Cookie'] = "csrftoken={}; Path=/; SameSite=None; Secure".format(token)
            # response['Set-Cookie'] = "sessionid=iantest; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax; Secure" # .format(request.session.session_key)
            return response
        else:
            return Response({'error': 'There was a problem logging in. Please try again.'})
    except Exception as e:
        print('Sign_in Exception' + str(e))
        return Response({'error': 'Something went wrong trying to sign you in. Contact osamwelian3@gmail.com'})

