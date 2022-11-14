import datetime
import string
import time
from django.utils.http import http_date
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
from django.middleware.csrf import get_token
from django.conf import settings

def unmask_cipher_token(token):
    """
    Given a token (assumed to be a string of CSRF_ALLOWED_CHARS, of length
    CSRF_TOKEN_LENGTH, and that its first half is a mask), use it to decrypt
    the second half to produce the original secret.
    """
    CSRF_SECRET_LENGTH = 32
    CSRF_ALLOWED_CHARS = string.ascii_letters + string.digits
    mask = token[:CSRF_SECRET_LENGTH]
    token = token[CSRF_SECRET_LENGTH:]
    chars = CSRF_ALLOWED_CHARS
    pairs = zip((chars.index(x) for x in token), (chars.index(x) for x in mask))
    return "".join(chars[x - y] for x, y in pairs)  # Note negative values are ok

# Create your views here.
@api_view(['GET'])
@ensure_csrf_cookie
def setCsrfCookie(request):
    token = unmask_cipher_token(get_token(request))
    request.META['CSRF_COOKIE'] = token
    context = {"success": "Cookies Set", "csrftoken": token}
    response = JsonResponse(data=context)
    # response['Set-Cookie'] = "csrftoken={}; Path=/; SameSite=None; Secure".format(token)
    # cookies = response['Set-Cookie']
    print(get_token(request))
    return response
    

@api_view(['GET'])
@csrf_protect
def isAuthenticated(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Not authenticated.'})
    else:
        return Response({'success': 'User is authenticated ', 'username': str(request.user.username)})

@api_view(['POST'])
@csrf_protect
def signup(request):
    data = request.data
    try:
        username = data['username']
        password = data['password']
        email = data['email']
        password2 = data['password2']

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken', 'username': 'username error'})
        else:
            if len(username) < 3:
                return Response({'error': 'Username can\'t have less than three initials', 'username': 'username error'})
            else:
                if password == 'google-auth':
                    return Response({'error': 'Please choose a stronger password.'})
                if password != password2:
                    return Response({'error': 'Passwords do not match', 'password2': 'password error'})
                else:
                    if len(password) < 6:
                        return Response({'error': 'Password must be atleast 6 characters', 'password': 'password error'})
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
                            return Response({'detail': 'Account created but couldn\'t send activation email. Please contact admin at osamwelian3@gmail.com'})

                        # send_mail("Verification Code", "This is your test verification code: 1234", 'no-reply@snackbar.com', [email])

                        user = User.objects.get(username=username)
                        user = UserSerializer(user)
                        return Response({ "success": "User created successfully", "data": user.data })
    except Exception as e:
        print('Sign_up Exception: '+ str(e))
        return Response({"error": "Something went wrong trying to sign you up. Contact osamwelian3@gmail.com"})

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
        return Response({'error': 'Activation link is invalid!'})

@api_view(['POST'])
@csrf_protect
def signin(request):
    # print(request.META['CSRF_COOKIE'])
    try:
        data = request.data
        username = data['username']
        password = data['password']

        if len(username) < 1 and len(password) < 1:
            return Response({'error': 'Please provide username and password.'})
        elif password == 'google-auth':
            return Response({'error': 'Invalid credentials.'})
        else:
            if not User.objects.filter(username=username).exists():
                return Response({'error': 'User with that user name does not exist.'})
            else:
                user = authenticate(username=username, password=password)
                if not User.objects.get(username=username).is_active:
                    return Response({'detail': 'You have not activated your account. Check your email for a link to activate your account.'})
                else:
                    if user is not None:
                        login(request, user)
                        token = unmask_cipher_token(get_token(request))

                        key = settings.SESSION_COOKIE_NAME
                        value = request.session.session_key
                        max_age = request.session.get_expiry_age()
                        expires_time = time.time() + max_age
                        expires = http_date(expires_time)
                        max_age=max_age
                        expires=expires
                        domain=settings.SESSION_COOKIE_DOMAIN
                        path=settings.SESSION_COOKIE_PATH
                        secure=settings.SESSION_COOKIE_SECURE or None
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None
                        samesite=settings.SESSION_COOKIE_SAMESITE
                        print(max_age)
                        sessionkey = set_cookie(key, value, max_age, expires, path, domain, secure, httponly, samesite)

                        request.META['CSRF_COOKIE'] = token
                        print('token: '+get_token(request))
                        print('csrf: '+token)
                        # print(str(sessionkey).split(':', 1)[1])
                        response = Response({'success': 'Login successful', 'username': username, 'csrftoken': token, 'sessionid': value}) # str(str(sessionkey).split(':', 1)[1])
                        # response['Set-Cookie'] = "csrftoken={}; Path=/; SameSite=None; Secure".format(token)
                        # response['Set-Cookie'] = "sessionid=iantest; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax; Secure" # .format(request.session.session_key)
                        return response
                    else:
                        return Response({'error': 'Invalid credentials...'})
    except Exception as e:
        print('Sign_in Exception' + str(e))
        return Response({'error': 'Something went wrong trying to sign you in. Contact osamwelian3@gmail.com'})

@api_view(['GET'])
def log_out(request):
    # print(request.META['CSRF_COOKIE'])
    try:
        if not request.user.is_authenticated:
            return Response({'detail': 'You are already logged out'})
        else:
            logout(request)
            return Response({'success': 'Logout success.'})
    except Exception as e:
        print('Log_out Exception' + str(e))
        return Response({'error': 'Something went wrong trying to log you out. Contact osamwelian3@gmail.com'})

@api_view(['GET'])
@csrf_protect
def delete_account(request, username):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        if User.objects.filter(username=username).exists():
            if user.is_superuser or user.is_staff:
                User.objects.filter(username=username).delete()
                return Response({'success': 'User account succesfuly deleted'})
            else:
                return Response({'error': 'Your user rights dont allow you to perform this action. Login as an administrator'})
        else:
            return Response({'error': 'User does not exist'})
    else:
        return Response({'error': 'sign in to perform this action'})


def set_cookie(
        key,
        value="",
        max_age=None,
        expires=None,
        path="/",
        domain=None,
        secure=False,
        httponly=False,
        samesite=None,
    ):
    """
    Set a cookie.

    ``expires`` can be:
    - a string in the correct format,
    - a naive ``datetime.datetime`` object in UTC,
    - an aware ``datetime.datetime`` object in any time zone.
    If it is a ``datetime.datetime`` object then calculate ``max_age``.

    ``max_age`` can be:
    - int/float specifying seconds,
    - ``datetime.timedelta`` object.
    """
    from django.utils import timezone
    from django.http.cookie import SimpleCookie
    cookies = SimpleCookie()
    cookies[key] = value
    if expires is not None:
        if isinstance(expires, datetime.datetime):
            if datetime.timezone.is_naive(expires):
                expires = timezone.make_aware(expires, datetime.timezone.utc)
            delta = expires - datetime.datetime.now(tz=datetime.timezone.utc)
            # Add one second so the date matches exactly (a fraction of
            # time gets lost between converting to a timedelta and
            # then the date string).
            delta = delta + datetime.timedelta(seconds=1)
            # Just set max_age - the max_age logic will set expires.
            expires = None
            if max_age is not None:
                raise ValueError("'expires' and 'max_age' can't be used together.")
            max_age = max(0, delta.days * 86400 + delta.seconds)
        else:
            cookies[key]["expires"] = expires
    else:
        cookies[key]["expires"] = ""
    if max_age is not None:
        if isinstance(max_age, datetime.timedelta):
            max_age = max_age.total_seconds()
        cookies[key]["max-age"] = int(max_age)
        # IE requires expires, so set it if hasn't been already.
        if not expires:
            cookies[key]["expires"] = http_date(time.time() + max_age)
    if path is not None:
        cookies[key]["path"] = path
    if domain is not None:
        cookies[key]["domain"] = domain
    if secure:
        cookies[key]["secure"] = True
    if httponly:
        cookies[key]["httponly"] = True
    if samesite:
        if samesite.lower() not in ("lax", "none", "strict"):
            raise ValueError('samesite must be "lax", "none", or "strict".')
        cookies[key]["samesite"] = samesite
    return cookies[key]
