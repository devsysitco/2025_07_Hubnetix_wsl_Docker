from django.shortcuts import render,redirect
from django.utils import timezone
from admin_dashboard.models import BlogPost, JobListing, NewsArticle, Project, Banner
from django.templatetags.static import static

# from django.views.decorators.cache import cache_control
# Create your views here.

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
def error_404(request, *args, **kwargs):
    return render(request, '404_robo.html', status=404)


def truncate_words(text, num_words):
    words = text.split()
    return ' '.join(words[:num_words])



# def home_page(request):
#     current_time = timezone.now()

#     # Get latest active blog posts
#     blog_posts = BlogPost.objects.filter(
#         is_active=True,
#         deleted_at__isnull=True,
#         date_published__lte=current_time
#     ).order_by('-date_published')[:3]

#     # Process blog posts
#     for post in blog_posts:
#         post.short_description = truncate_words(post.short_description, 15)

#     # Get latest active projects
#     projects = Project.objects.filter(
#         is_active=True,
#         deleted_at__isnull=True
#     ).order_by('-created_at')[:3]

#     # Create context with both blog posts and projects
#     context = {
#         'page_title': 'Home Page',
#         'blog_posts': blog_posts,
#         'projects': projects
#     }

#     print("#############################HOME PAGE###################")
#     return render(request, 'home.html', context)



def home_page(request):
    # current_time = timezone.now()

    # Get latest active blog posts
    # blog_posts = BlogPost.objects.filter(
    #     is_active=True,
    #     deleted_at__isnull=True,
    #     date_published__lte=current_time
    # ).order_by('-date_published')[:3]

    # # Process blog posts
    # for post in blog_posts:
    #     post.short_description = truncate_words(post.short_description, 15)

    # # Get latest active projects
    # projects = Project.objects.filter(
    #     is_active=True,
    #     deleted_at__isnull=True
    # ).order_by('-created_at')[:3]

    # Get slider banners with optimized query
    slider_banners = Banner.objects.filter(
        banner_type='slider',
        is_active=True,
        deleted_at__isnull=True
    ).order_by('order')  # Remove .values() to get full model instances

    # Get single banners (about and sustainability) with optimized query
    single_banners = Banner.objects.filter(
        banner_type__in=['about', 'sustainability'],
        is_active=True,
        deleted_at__isnull=True
    )  # Remove .values() to get full model instances

    # Process single banners into a dictionary for easier template access
    banner_dict = {
        banner.banner_type: {
            'image': banner.image.url if banner.image else None,
            'alt_text': banner.alt_text,
            'url': banner.url,
            'meta_title': banner.meta_title,
            'meta_description': banner.meta_description
        } for banner in single_banners
    }

    print(banner_dict)

    # Get latest products with their categories
    latest_products = Product.objects.filter(
        is_latest=True,
        deleted_at__isnull=True,
        latest_marked_at__isnull=False
    ).select_related().prefetch_related(
        'categories'
    ).order_by('-latest_marked_at')[:3]

    # Get featured products with their categories
    featured_products = Product.objects.filter(
        is_featured=True,
        deleted_at__isnull=True,
        featured_marked_at__isnull=False
    ).select_related().prefetch_related(
        'categories'
    ).order_by('-featured_marked_at')[:3]

    # Create context with all required data
    context = {
        'page_title': 'Home Page',
        'slider_banners': slider_banners,
        'about_banner': banner_dict.get('about', {}),
        'sustainability_banner': banner_dict.get('sustainability', {}),
        # 'blog_posts': blog_posts,
        # 'projects': projects,
        'latest_products': latest_products,
        'featured_products': featured_products
    }

    return render(request, 'home.html', context)


######################################################################################################
######################################################################################################
######################################################################################################

from datetime import datetime, timedelta
import json
import random
import re
import time

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import EmailValidator, RegexValidator
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from user_account.models import Customer, User, OTP

# Constants
SESSION_TIMEOUT = getattr(settings, 'SESSION_TIMEOUT', 4000)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds
PASSWORD_MIN_LENGTH = 8
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 300  # 5 minutes in seconds
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10

def rate_limit_key(user_id, action):
    return f"rate_limit_{action}_{user_id}"

def is_rate_limited(user_id, action):
    key = rate_limit_key(user_id, action)
    attempts = cache.get(key, 0)
    if attempts >= RATE_LIMIT_ATTEMPTS:
        return True
    cache.set(key, attempts + 1, RATE_LIMIT_WINDOW)
    return False

def create_response(status, message=None, messages_list=None, data=None):
    """Standardized response creator"""
    response = {'status': status}
    if message:
        response['message'] = message
    if messages_list:
        response['messages'] = messages_list
    if data:
        response['data'] = data
    return JsonResponse(response)

def validate_strong_password(password):
    """Enhanced password validation"""
    errors = []
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    return errors

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def customer_signin(request):
    """Enhanced customer sign-in view with improved security and validation"""

    def check_existing_sessions(request):
        """Check and handle existing sessions"""
        session_types = {
            'adminid': 'Admin Dashboard',
            'seomanagerid': 'SEO Manager Dashboard',
            'partnermanagerid': 'Partner Manager Dashboard'
        }

        for session_key, dashboard_name in session_types.items():
            if session_key in request.session:
                request.session.flush()
                return True, dashboard_name
        return False, None

    try:
        # Parse request data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
            except json.JSONDecodeError:
                return create_response('error', 'Invalid request format')
        else:
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')

        # Validate input
        if not email or not password:
            return create_response('error', 'Email and password are required')

        try:
            user = User.objects.get(email=email)

            # Check account type
            if not user.account_type or user.account_type.id != 4:
                return create_response('error', 'Use Management dashboard for login')

            # Check rate limiting
            if is_rate_limited(user.id, 'signin'):
                return create_response('error', 'Too many attempts. Please try again later')

            # Check account lockout
            if user.is_locked_out and user.locked_out_until and user.locked_out_until > now():
                remaining_time = int((user.locked_out_until - now()).total_seconds())
                return create_response('error',
                    f"Account is locked. Try again in {remaining_time // 60} minutes")

            # Reset previous day's attempts
            if user.failed_attempts:
                failed_attempts = json.loads(user.failed_attempts)
                today = now().date()
                failed_attempts = [
                    attempt for attempt in failed_attempts
                    if attempt.split()[0] == str(today)
                ]
                user.failed_attempts = json.dumps(failed_attempts)
                user.login_attempts = len(failed_attempts)
                user.save(update_fields=['failed_attempts', 'login_attempts'])

        except User.DoesNotExist:
            # Use same response time as success to prevent timing attacks
            import time
            time.sleep(0.1)
            return create_response('error', 'Invalid email or password')

        # Authenticate user
        authenticated_user = authenticate(request, email=email, password=password)

        if authenticated_user and authenticated_user.account_type and authenticated_user.account_type.id == 4:
            # Check existing sessions
            has_existing_session, dashboard_name = check_existing_sessions(request)

            # Reset security counters
            authenticated_user.login_attempts = 0
            authenticated_user.is_locked_out = False
            authenticated_user.locked_out_until = None
            authenticated_user.failed_attempts = json.dumps([])
            authenticated_user.last_login_attempt = now()
            authenticated_user.save(update_fields=[
                'login_attempts', 'is_locked_out', 'locked_out_until',
                'failed_attempts', 'last_login_attempt'
            ])

            # Set up session
            request.session['customerid'] = authenticated_user.id
            auth_login(request, authenticated_user)

            # Configure session expiry
            request.session.set_expiry(SESSION_TIMEOUT)
            request.session['last_activity'] = now().timestamp()

            response_data = {'status': 'success', 'message': 'Login successful'}
            if has_existing_session:
                response_data['session_cleared'] = True
                response_data['previous_session'] = dashboard_name

            return JsonResponse(response_data)
        else:
            # Handle failed login
            user.login_attempts += 1

            failed_attempts = json.loads(user.failed_attempts) if user.failed_attempts else []
            failed_attempts.append(str(now()))
            user.failed_attempts = json.dumps(failed_attempts)

            if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.is_locked_out = True
                user.locked_out_until = now() + timedelta(seconds=LOCKOUT_DURATION)
                message = f"Too many failed attempts. Account locked for {LOCKOUT_DURATION // 60} minutes"
            else:
                message = "Invalid email or password"

            user.save(update_fields=[
                'login_attempts', 'failed_attempts',
                'is_locked_out', 'locked_out_until'
            ])

            return create_response('error', message)

    except Exception as e:
        return create_response('error', 'An unexpected error occurred')

@ensure_csrf_cookie
@csrf_protect
@require_POST
def customer_signup(request):
    """Enhanced customer sign-up view with improved validation and security"""

    try:
        # Parse and validate request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return create_response('error', 'Invalid request format')

        required_fields = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'username': 'Username',
            'phone': 'Phone',
            'password': 'Password'
        }

        # Check required fields
        missing_fields = []
        for field, label in required_fields.items():
            if not data.get(field, '').strip():
                missing_fields.append(label)

        if missing_fields:
            return create_response(
                'error',
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        # Clean and validate data
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        email = data['email'].strip().lower()
        username = data['username'].strip()
        phone = data['phone'].strip()
        phone_country_code = data.get('phone_country_code', '').strip()
        password = data['password']

        # Validate email
        try:
            EmailValidator()(email)
        except ValidationError:
            return create_response('error', 'Invalid email format')

        # Validate username
        username_validator = RegexValidator(
            r'^[\w.@+-]+$',
            'Username can only contain letters, numbers, and @/./+/-/_ characters'
        )
        try:
            username_validator(username)
            if len(username) < 3:
                return create_response('error', 'Username must be at least 3 characters long')
        except ValidationError as e:
            return create_response('error', str(e))

        # Validate names
        if len(first_name) < 2:
            return create_response('error', 'First name must be at least 2 characters long')
        if len(last_name) < 2:
            return create_response('error', 'Last name must be at least 2 characters long')

        # Validate phone (basic validation, consider using more robust validation)
        full_phone = f"{phone_country_code}{phone}" if phone_country_code else phone
        phone_validator = RegexValidator(
            r'^\+?1?\d{9,15}$',
            'Enter a valid phone number'
        )

        # try:
        #     phone_validator(full_phone)
        # except ValidationError:
        #     return create_response('error', 'Invalid phone number format')

        # Validate password

        # try:
        #     validate_password(password)
        #     password_errors = validate_strong_password(password)
        #     if password_errors:
        #         return create_response('error', password_errors[0], password_errors)
        # except ValidationError as e:
        #     return create_response('error', str(e.messages[0]), e.messages)

        # Check existing users
        if Customer.objects.filter(email=email).exists():
            return create_response('error', 'Email already registered')
        if Customer.objects.filter(username=username).exists():
            return create_response('error', 'Username already taken')

        # Create customer with transaction
        try:
            with transaction.atomic():
                customer = Customer.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )

                # Additional setup could go here (e.g., sending welcome email)

                return create_response(
                    'success',
                    'Account created successfully! You can now sign in.',
                    [{'tags': 'success', 'message': 'Account created successfully!'}]
                )

        except Exception as e:
            return create_response('error', 'Failed to create account')

    except Exception as e:
        return create_response('error', 'An unexpected error occurred')
    



@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def forgot_password(request):
    """Handle forgot password by sending OTP to user's email"""
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
        except json.JSONDecodeError:
            return create_response('error', 'Invalid request format')

        # Validate input
        if not email:
            return create_response('error', 'Email is required')

        # Validate email
        try:
            EmailValidator()(email)
        except ValidationError:
            return create_response('error', 'Invalid email format')

        # Check rate limiting
        if is_rate_limited(email, 'forgot_password'):
            return create_response('error', 'Too many requests. Please try again later')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Prevent user enumeration
            time.sleep(0.1)
            return create_response('error', 'Account not available in this email')
        
        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])

        # Store OTP
        with transaction.atomic():
            OTP.objects.filter(user=user, is_used=False).update(is_used=True)  # Invalidate old OTPs
            OTP.objects.create(user=user, otp=otp)

        # Send OTP email
        try:
            email_message = EmailMessage(
                subject='Password Reset OTP',
                body=f'''Dear {user.first_name or 'User'},

Your One-Time Password (OTP) for password reset is: {otp}

This OTP is valid for {OTP_EXPIRY_MINUTES} minutes. Please do not share it with anyone.

If you did not request this, please contact support.

Best regards,
Hubnetix Backend Office
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            email_message.send(fail_silently=False)
        except Exception as e:
            return create_response('error', 'Failed to send OTP email')

        #return create_response('success', 'OTP sent to your email')
        return create_response('success', 'OTP sent to your email.If you don’t receive an OTP, check your spam folder or contact support')


    except Exception as e:
        return create_response('error', 'An unexpected error occurred')

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def verify_otp(request):
    """Verify OTP for password reset"""
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            otp = data.get('otp', '').strip()
        except json.JSONDecodeError:
            return create_response('error', 'Invalid request format')

        # Validate input
        if not email or not otp:
            return create_response('error', 'Email and OTP are required')

        if not otp.isdigit() or len(otp) != OTP_LENGTH:
            return create_response('error', 'Invalid OTP format')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return create_response('error', 'Invalid request')

        # Check OTP
        try:
            otp_obj = OTP.objects.get(user=user, otp=otp, is_used=False)
            if not otp_obj.is_valid():
                return create_response('error', 'OTP has expired')
        except OTP.DoesNotExist:
            return create_response('error', 'Invalid OTP')

        # Mark OTP as used
        with transaction.atomic():
            otp_obj.is_used = True
            otp_obj.save()

        return create_response('success', 'OTP verified successfully')

    except Exception as e:
        return create_response('error', 'An unexpected error occurred')

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def reset_password(request):
    """Reset user's password after OTP verification"""
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
        except json.JSONDecodeError:
            return create_response('error', 'Invalid request format')

        # Validate input
        if not email or not password:
            return create_response('error', 'Email and password are required')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return create_response('error', 'Invalid request')

        # Check if user has a valid OTP
        if not OTP.objects.filter(user=user, is_used=True).exists():
            return create_response('error', 'Please verify OTP first')

        # Validate password strength
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(password, user=user)
        except ValidationError as e:
            return create_response('error', e.messages[0])

        # Reset password
        with transaction.atomic():
            user.set_password(password)
            user.save()
            OTP.objects.filter(user=user).delete()  # Clear all OTPs after reset

        return create_response('success', 'Password reset successfully')

    except Exception as e:
        return create_response('error', 'An unexpected error occurred')


# def home_logout_view(request):
#     logout(request)
#     messages.success(request, 'You have been successfully logged out.')
#     return redirect('home-page')

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from urllib.parse import unquote
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home_logout_view(request):
    # Get the 'next' parameter from POST or GET
    next_page = request.POST.get('next') or request.GET.get('next')

    # Perform logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')

    # Redirect to the next page if provided and valid
    if next_page and url_has_allowed_host_and_scheme(
        url=next_page,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return redirect(next_page)
    return redirect('home-page')





from functools import wraps
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib.auth import login as auth_login


def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'customerid' in request.session:
            try:
                user = User.objects.get(id=request.session['customerid'])
                # Check if user is a customer (account_type.id == 4)
                if user.account_type and user.account_type.id == 4:
                    # Update last activity timestamp
                    request.session['last_activity'] = now().timestamp()
                    # Temporarily login this user for the duration of this request
                    auth_login(request, user)
                    return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                pass
        return redirect('home-page')
    return wrapper


######################################################################################################
# profile management 

from django.contrib.auth import authenticate
from django.core.validators import EmailValidator, RegexValidator, ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

def create_response(status, message, messages=None):
    response = {'status': status, 'message': message}
    if messages:
        response['messages'] = messages
    return JsonResponse(response)

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["GET"])
def customer_profile(request):
    """Retrieve customer profile data"""
    try:
        if not request.session.get('customerid'):
            return create_response('error', 'Authentication required')
        
        user = Customer.objects.get(id=request.session['customerid'])
        profile_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'phone': user.phone
        }
        
        return JsonResponse({
            'status': 'success',
            'profile': profile_data
        })
    except Customer.DoesNotExist:
        return create_response('error', 'User not found')
    except Exception as e:
        return create_response('error', 'An unexpected error occurred')

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def customer_profile_update(request):
    """Update customer profile data"""
    try:
        if not request.session.get('customerid'):
            return create_response('error', 'Authentication required')
            
        data = json.loads(request.body)
        required_fields = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'username': 'Username',
            'phone': 'Phone'
        }

        missing_fields = []
        for field, label in required_fields.items():
            if not data.get(field, '').strip():
                missing_fields.append(label)

        if missing_fields:
            return create_response(
                'error',
                f"Missing required fields: {', '.join(missing_fields)}"
            )

        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        email = data['email'].strip().lower()
        username = data['username'].strip()
        phone = data['phone'].strip()
        phone_country_code = data.get('phone_country_code', '').strip()

        try:
            EmailValidator()(email)
        except ValidationError:
            return create_response('error', 'Invalid email format')

        username_validator = RegexValidator(
            r'^[\w.@+-]+$',
            'Username can only contain letters, numbers, and @/./+/-/_ characters'
        )
        try:
            username_validator(username)
            if len(username) < 3:
                return create_response('error', 'Username must be at least 3 characters long')
        except ValidationError as e:
            return create_response('error', str(e))

        if len(first_name) < 2:
            return create_response('error', 'First name must be at least 2 characters long')
        if len(last_name) < 2:
            return create_response('error', 'Last name must be at least 2 characters long')

        full_phone = f"{phone_country_code}{phone}" if phone_country_code else phone
        # phone_validator = RegexValidator(
        #     r'^\+?1?\d{9,15}$',
        #     'Enter a valid phone number'
        # )
        # try:
        #     phone_validator(full_phone)
        # except ValidationError:
        #     return create_response('error', 'Invalid phone number format')

        user = Customer.objects.get(id=request.session['customerid'])
        
        if email != user.email and Customer.objects.filter(email=email).exclude(id=user.id).exists():
            return create_response('error', 'Email already registered')
        if username != user.username and Customer.objects.filter(username=username).exclude(id=user.id).exists():
            return create_response('error', 'Username already taken')

        with transaction.atomic():
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.phone = phone
            user.save()

        return create_response('success', 'Profile updated successfully')
    except Customer.DoesNotExist:
        return create_response('error', 'User not found')
    except Exception as e:
        return create_response('error', 'An unexpected error occurred')

@ensure_csrf_cookie
@csrf_protect
@require_http_methods(["POST"])
def customer_password_change(request):
    """Change customer password"""
    try:
        if not request.session.get('customerid'):
            return create_response('error', 'Authentication required')
            
        data = json.loads(request.body)
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_new_password = data.get('confirm_new_password', '')

        if not all([current_password, new_password, confirm_new_password]):
            return create_response('error', 'All password fields are required')

        user = Customer.objects.get(id=request.session['customerid'])
        print('########################')
        print(user)
        
        if not user.check_password(current_password):
            return create_response('error', 'Current password is incorrect')

        if new_password != confirm_new_password:
            return create_response('error', 'New passwords do not match')

        # Basic password strength check (can be enhanced based on your requirements)
        if len(new_password) < 8:
            return create_response('error', 'New password must be at least 8 characters long')

        # Set up session
        # request.session['customerid'] = authenticated_user.id
        # auth_login(request, authenticated_user)
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        # Set up session
        request.session['customerid'] = user.id
        

        return create_response('success', 'Password changed successfully')
    except Customer.DoesNotExist:
        return create_response('error', 'User not found')
    except Exception as e:
        return create_response('error', 'An unexpected error occurred')
    

    

######################################################################################################
######################################################################################################
######################################################################################################

from django.shortcuts import render, get_object_or_404
from catalog.models import Category, Product, Datasheet
from django.http import HttpResponseRedirect

from django.shortcuts import get_object_or_404, redirect



import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone


def initialize_categories():
    """Initialize categories with default images"""

    # Get the current timestamp
    current_time = timezone.now()

    # Setup paths for default images
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'home_assets', 'media')

    # Define default image file names
    default_images = {
        'default-image.png': ['category_icons/lan.png', 'category_icons/cab.png', 'category_icons/p-line.png', 'category_icons/act-pro.png', 'category_icons/sec.png'],
        'default-image.png': ['category_banners/lanline_banner.jpeg', 'category_banners/cabline_banner.jpeg', 'category_banners/powline_banner.jpeg', 'category_banners/actline_banner.jpeg', 'category_banners/secline_banner.jpeg'],
        'default-image.png': ['category_side_images/lan_side.png', 'category_side_images/cab_side.png', 'category_side_images/pow_side.png', 'category_side_images/act_side.png', 'category_side_images/sec_side.png']
    }

    # Create media directories if they don't exist
    for dir_name in ['category_icons', 'category_banners', 'category_side_images']:
        os.makedirs(os.path.join(settings.MEDIA_ROOT, dir_name), exist_ok=True)

    # Category data with consistent image paths
    categories_data = [
        {
            'id': 1,
            'Category_id': 1,
            'name': 'LANLINE',
            'slug': 'structured-cabling-solutions-lanline',
            'style': 'grid',
            'short_description': 'Connects, Empowers, and Elevates with Reliability.',
            'detailed_description': 'LANLINE provides high-performance, reliable, and flexible cabling systems designed to optimize network infrastructure and ensure seamless communication.',
            'created_at': current_time,
            'updated_at': current_time,
            'is_active': True,
            'icon_path': 'category_icons/lan.png',
            'banner_path': 'category_banners/lanline_banner.jpeg',
            'side_image_path': 'category_side_images/lan_side.png'
        },
        {
            'id': 2,
            'Category_id': 2,
            'name': 'CABLINE',
            'slug': 'network-cabinets-and-racks-cabline',
            'style': 'grid',
            'short_description': 'Organizes, Protects, and Optimizes with Precision.',
            'detailed_description': 'CABLINE offers robust, efficient, and scalable infrastructure solutions designed to optimize network organization and equipment protection.',
            'created_at': current_time,
            'updated_at': current_time,
            'is_active': True,
            'icon_path': 'category_icons/cab.png',
            'banner_path': 'category_banners/cabline_banner.jpeg',
            'side_image_path': 'category_side_images/cab_side.png'
        },
        {
            'id': 3,
            'Category_id': 3,
            'name': 'POWLINE',
            'slug': 'ups-systems-powline',
            'style': 'grid',
            'short_description': 'Powers Resilient, Efficient, and Uninterrupted Energy.',
            'detailed_description': 'POWLINE provides advanced, reliable, and scalable power solutions designed to ensure uninterrupted energy supply for critical systems.',
            'created_at': current_time,
            'updated_at': current_time,
            'is_active': True,
            'icon_path': 'category_icons/p-line.png',
            'banner_path': 'category_banners/powline_banner.jpeg',
            'side_image_path': 'category_side_images/pow_side.png'
        },
        {
            'id': 4,
            'Category_id': 4,
            'name': 'ACTLINE',
            'slug': 'active-devices-switches-actline',
            'style': 'grid',
            'short_description': 'Fast, Smart, and Secure Connectivity.',
            'detailed_description': 'ACTLINE delivers cutting-edge networking solutions designed to ensure seamless connectivity, high performance, and efficient data transmission.',
            'created_at': current_time,
            'updated_at': current_time,
            'is_active': True,
            'icon_path': 'category_icons/act-pro.png',
            'banner_path': 'category_banners/actline_banner.jpeg',
            'side_image_path': 'category_side_images/act_side.png'
        },
        {
            'id': 5,
            'Category_id': 5,
            'name': 'SECLINE',
            'slug': 'security-surveillance-devices-veuline',
            'style': 'grid',
            'short_description': 'Secures, Connects, and Protects with Intelligence.',
            'detailed_description': 'SECLINE delivers intelligent, reliable, and integrated security and communication solutions to safeguard critical environments.',
            'created_at': current_time,
            'updated_at': current_time,
            'is_active': True,
            'icon_path': 'category_icons/sec.png',
            'banner_path': 'category_banners/secline_banner.jpeg',
            'side_image_path': 'category_side_images/sec_side.png'
        }
    ]

    def save_image(source_path, destination_path, category):
        """Helper function to save images"""
        try:
            # First try to use the actual image from static directory
            if os.path.exists(os.path.join(static_dir, source_path)):
                with open(os.path.join(static_dir, source_path), 'rb') as f:
                    return ContentFile(f.read(), name=os.path.basename(destination_path))
            # If not found, use default image
            else:
                default_image = next(name for name in ['default-image.png', 'default-image.png', 'default-image.png']
                                   if os.path.exists(os.path.join(static_dir, name)))
                with open(os.path.join(static_dir, default_image), 'rb') as f:
                    return ContentFile(f.read(), name=os.path.basename(destination_path))
        except Exception as e:
            print(f"Error saving image for category {category.name}: {str(e)}")
            return None

    # Create or update categories with images
    for data in categories_data:
        # Remove image paths from data before creating/updating category
        icon_path = data.pop('icon_path')
        banner_path = data.pop('banner_path')
        side_image_path = data.pop('side_image_path')

        # Get or create category
        category, created = Category.objects.get_or_create(
            id=data['id'],
            defaults=data
        )

        # Update images if they don't exist
        if not category.icon or not category.icon.name:
            icon_file = save_image(icon_path, icon_path, category)
            if icon_file:
                category.icon.save(os.path.basename(icon_path), icon_file, save=False)

        if not category.banner or not category.banner.name:
            banner_file = save_image(banner_path, banner_path, category)
            if banner_file:
                category.banner.save(os.path.basename(banner_path), banner_file, save=False)

        if not category.side_image or not category.side_image.name:
            side_image_file = save_image(side_image_path, side_image_path, category)
            if side_image_file:
                category.side_image.save(os.path.basename(side_image_path), side_image_file, save=False)

        # Save the category with all changes
        category.save()



def category_by_id(request, category_id):
    print("###############################--category_by_id--####################")

    initialize_categories()

    category = get_object_or_404(Category, id=category_id)
    return redirect('user_account-category_view', category_slug=category.slug)




def get_banner(category):
    while category:
        if category.banner:
            return category.banner.url
        category = category.parent
    return None


def category_view(request, category_slug):
    print("###############################--category_view--####################")

    category = get_object_or_404(Category, slug=category_slug)
    subcategories = Category.objects.filter(parent=category, deleted_at__isnull=True)
    banner_url = get_banner(category)

    subcategory_count = subcategories.count()
    absolute_url = request.build_absolute_uri()

    if subcategory_count == 0:
        products = Product.objects.filter(categories=category, deleted_at__isnull=True)

        context = {
            'category': category,
            'subcategories': subcategories,
            'subcategory_count': subcategory_count,
            'products': products,
            'banner_url': banner_url,
            'absolute_url': absolute_url,
        }
        return redirect('user_account-product_list_view', category_slug=category.slug)


    context = {
        'category': category,
        'subcategories': subcategories,
        'banner_url': banner_url,
        'absolute_url': absolute_url,
    }
    print(context)
    return render(request, 'category_home_list.html', context)




#####################################################################################



def product_list_view(request, category_slug):
    print("###############################--product_list_view_--####################")
    category = get_object_or_404(Category, slug=category_slug)

    subcategories = Category.objects.filter(parent=category, deleted_at__isnull=True)
    banner_url = get_banner(category)
    subcategory_count = subcategories.count()

    products = None
    absolute_url = request.build_absolute_uri()
    user_lists = []
    if request.user.is_authenticated:
        user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

    if subcategory_count == 0:
        # Modify the products query to prefetch datasheets
        products = Product.objects.filter(
            categories=category,
            deleted_at__isnull=True
        ).prefetch_related('datasheets')
        products_count = products.count()

        # Create a list of product IDs that have datasheets
        products_with_datasheets_ids = [
            product.id for product in products
            if product.datasheets.filter(deleted_at__isnull=True).exists()
        ]

        context = {
            'category': category,
            'user_lists': user_lists,
            'subcategories': subcategories,
            'subcategory_count': subcategory_count,
            'products': products,
            'products_count': products_count,
            'banner_url': banner_url,
            'absolute_url': absolute_url,
            'products_with_datasheets_ids': products_with_datasheets_ids,  # Add list of IDs to context
        }
        return render(request, 'product_home_list.html', context)


    context = {
        'category': category,
        'subcategories': subcategories,
        'subcategory_count': subcategory_count,
        'products': products,
        'absolute_url': absolute_url,
    }
    print(context)
    return render(request, 'category_home_list.html', context)


#####################################################################################



# def product_detail_view(request, category_slug, product_slug):
#     # Get the category by slug
#     category = get_object_or_404(Category, slug=category_slug)

#     user_lists = []
#     if request.user.is_authenticated:
#         user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')




#     # Get the product by slug and ensure it belongs to the specified category
    # product = get_object_or_404(
    #     Product.objects.select_related().prefetch_related(
    #         'categories',
    #         'images',
    #         'specifications',
    #         'documents',
    #         'datasheets'
    #     ),
    #     slug=product_slug,
    #     categories=category
    # )

#     active_datasheets = product.datasheets.filter(deleted_at__isnull=True)

#     # Handle documents
#     documents_by_type = {}
#     for doc in product.documents.all():
#         doc_type = doc.document_type or 'Uncategorized'
#         if doc_type not in documents_by_type:
#             documents_by_type[doc_type] = []
#         documents_by_type[doc_type].append(doc)

#     # Prepare context
#     context = {
#         'product': product,
#         'user_lists': user_lists,
#         'category': category,
#         'documents_by_type': documents_by_type,
#         'banner_url': "/media/banner_default_image/Hubnetix_default_Banner.JPG",
#         'absolute_url': request.build_absolute_uri(),
#     }


#     if active_datasheets.exists():
#         return render(request, 'product_home_detail_datasheet.html', context)
#     else:
#         return render(request, 'product_home_detail.html', context)

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# import json

# from django.shortcuts import get_object_or_404, render
# import json

# def product_detail_view(request, category_slug, product_slug):
#     # Get the category by slug
#     category = get_object_or_404(Category, slug=category_slug)

#     user_lists = []
#     if request.user.is_authenticated:
#         user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

#     # Get the product by slug and ensure it belongs to the specified category
    # product = get_object_or_404(
    #     Product.objects.select_related().prefetch_related(
    #         'categories',
    #         'images',
    #         'specifications',
    #         'documents',
    #         'datasheets'
    #     ),
    #     slug=product_slug,
    #     categories=category
    # )

#     # Ensure unique datasheets
#     active_datasheets = product.datasheets.filter(deleted_at__isnull=True).distinct()

#     filters = ["All", "None"]  # Part Numbers
#     width_filters = ["All", "None"]
#     depth_filters = ["All", "None"]
#     height_filters = ["All", "None"]
#     size_filters = ["All", "None"]
#     items = []

#     if active_datasheets.exists():
#         # Part Numbers filter
#         part_numbers = active_datasheets.filter(
#             include_part_number=True,
#             part_number__isnull=False
#         ).values_list('part_number', flat=True).distinct().order_by('part_number')
#         filters.extend([str(pn) for pn in part_numbers if pn])

#         # Size filter
#         sizes = active_datasheets.filter(
#             include_size_dimensions=True,
#             size__isnull=False
#         ).values_list('size', flat=True).distinct().order_by('size')
#         size_filters.extend([str(s) for s in sizes if s])

#         # Width filter
#         widths = active_datasheets.filter(
#             include_size_dimensions=True,
#             width__isnull=False
#         ).values_list('width', flat=True).distinct().order_by('width')
#         width_filters.extend([str(w) for w in widths if w])

#         # Depth filter
#         depths = active_datasheets.filter(
#             include_size_dimensions=True,
#             depth__isnull=False
#         ).values_list('depth', flat=True).distinct().order_by('depth')
#         depth_filters.extend([str(d) for d in depths if d])

#         # Height filter
#         heights = active_datasheets.filter(
#             include_size_dimensions=True,
#             height__isnull=False
#         ).values_list('height', flat=True).distinct().order_by('height')
#         height_filters.extend([str(h) for h in heights if h])

#         for datasheet in active_datasheets:
#             item = {
#                 "id": datasheet.id,
#                 "type": str(datasheet.part_number) if datasheet.include_part_number and datasheet.part_number else "",
#                 "ProductDescription": str(datasheet.name),
#                 "size": str(datasheet.size) if datasheet.include_size_dimensions and datasheet.size else "",
#                 "width": str(datasheet.width) if datasheet.include_size_dimensions and datasheet.width else "",
#                 "depth": str(datasheet.depth) if datasheet.include_size_dimensions and datasheet.depth else "",
#                 "height": str(datasheet.height) if datasheet.include_size_dimensions and datasheet.height else "",
#                 "pdfpath": datasheet.file.url if datasheet.file else "",
#                 "description": str(datasheet.description) if datasheet.description else str(datasheet.name)
#             }
#             items.append(item)

#     initial_data = {
#         "filters": filters,
#         "sizefilters": size_filters,
#         "widthfilters": width_filters,
#         "depthfilters": depth_filters,
#         "heightfilters": height_filters,
#         "items": items,
#     }

#     # Handle documents
#     documents_by_type = {}
#     for doc in product.documents.all():
#         doc_type = doc.document_type or 'Uncategorized'
#         if doc_type not in documents_by_type:
#             documents_by_type[doc_type] = []
#         documents_by_type[doc_type].append(doc)

#     # Prepare context
#     context = {
#         'product': product,
#         'user_lists': user_lists,
#         'category': category,
#         'documents_by_type': documents_by_type,
#         'banner_url': "/media/banner_default_image/Hubnetix_default_Banner.JPG",
#         'absolute_url': request.build_absolute_uri(),
#         'initial_data': json.dumps(initial_data, ensure_ascii=False)
#     }

#     print(context)

#     if active_datasheets.exists():
#         return render(request, 'product_home_detail_datasheet.html', context)
#     else:
#         return render(request, 'product_home_detail.html', context)


#################################################################################
#working

from django.shortcuts import get_object_or_404, render
import json

# def product_detail_view(request, category_slug, product_slug):
#     # Get the category by slug
#     category = get_object_or_404(Category, slug=category_slug)

#     user_lists = []
#     if request.user.is_authenticated:
#         user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

#     # Get the product by slug and ensure it belongs to the specified category
    # product = get_object_or_404(
    #     Product.objects.select_related().prefetch_related(
    #         'categories',
    #         'images',
    #         'specifications',
    #         'documents',
    #         'datasheets'
    #     ),
    #     slug=product_slug,
    #     categories=category
    # )

#     # Ensure unique datasheets
#     active_datasheets = product.datasheets.filter(deleted_at__isnull=True).distinct()

#     filters = ["All", "None"]  # Part Numbers
#     width_filters = ["All", "None"]
#     depth_filters = ["All", "None"]
#     height_filters = ["All", "None"]
#     size_filters = ["All", "None"]
#     items = []

#     if active_datasheets.exists():
#         # Part Numbers filter
#         part_numbers = active_datasheets.filter(
#             include_part_number=True,
#             part_number__isnull=False
#         ).values_list('part_number', flat=True).distinct().order_by('part_number')
#         filters.extend([str(pn) for pn in part_numbers if pn])

#         # Size filter
#         sizes = active_datasheets.filter(
#             include_size_dimensions=True,
#             size__isnull=False
#         ).values_list('size', flat=True).distinct().order_by('size')
#         size_filters.extend([str(s) for s in sizes if s])

#         # Width filter
#         widths = active_datasheets.filter(
#             include_size_dimensions=True,
#             width__isnull=False
#         ).values_list('width', flat=True).distinct().order_by('width')
#         width_filters.extend([str(w) for w in widths if w])

#         # Depth filter
#         depths = active_datasheets.filter(
#             include_size_dimensions=True,
#             depth__isnull=False
#         ).values_list('depth', flat=True).distinct().order_by('depth')
#         depth_filters.extend([str(d) for d in depths if d])

#         # Height filter
#         heights = active_datasheets.filter(
#             include_size_dimensions=True,
#             height__isnull=False
#         ).values_list('height', flat=True).distinct().order_by('height')
#         height_filters.extend([str(h) for h in heights if h])

#         for datasheet in active_datasheets:
#             item = {
#                 "id": datasheet.id,
#                 "type": str(datasheet.part_number) if datasheet.include_part_number and datasheet.part_number else "",
#                 "ProductDescription": str(datasheet.name),
#                 "size": str(datasheet.size) if datasheet.include_size_dimensions and datasheet.size else "",
#                 "width": str(datasheet.width) if datasheet.include_size_dimensions and datasheet.width else "",
#                 "depth": str(datasheet.depth) if datasheet.include_size_dimensions and datasheet.depth else "",
#                 "height": str(datasheet.height) if datasheet.include_size_dimensions and datasheet.height else "",
#                 "pdfpath": datasheet.file.url if datasheet.file else "",
#                 "description": str(datasheet.description) if datasheet.description else str(datasheet.name)
#             }
#             items.append(item)

#     initial_data = {
#         "filters": filters,
#         "sizefilters": size_filters,
#         "widthfilters": width_filters,
#         "depthfilters": depth_filters,
#         "heightfilters": height_filters,
#         "items": items,
#     }

#     # Handle documents
#     documents_by_type = {}
#     for doc in product.documents.all():
#         doc_type = doc.document_type or 'Uncategorized'
#         if doc_type not in documents_by_type:
#             documents_by_type[doc_type] = []
#         documents_by_type[doc_type].append(doc)

#     # Prepare context
#     context = {
#         'product': product,
#         'user_lists': user_lists,
#         'category': category,
#         'documents_by_type': documents_by_type,
#         'banner_url': "/media/banner_default_image/Hubnetix_default_Banner.JPG",
#         'absolute_url': request.build_absolute_uri(),
#         'initial_data': json.dumps(initial_data, ensure_ascii=False)
#     }

#     print(context)

#     if active_datasheets.exists():
#         return render(request, 'product_home_detail_datasheet.html', context)
#     else:
#         return render(request, 'product_home_detail.html', context)



# from django.shortcuts import get_object_or_404, render
# import json

# def product_detail_view(request, category_slug, product_slug):
#     # Get the category by slug
#     category = get_object_or_404(Category, slug=category_slug)

#     user_lists = []
#     if request.user.is_authenticated:
#         user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

#     # Get the product by slug and ensure it belongs to the specified category
#     product = get_object_or_404(
#         Product.objects.select_related().prefetch_related(
#             'categories',
#             'images',
#             'specifications',
#             'documents',
#             'datasheets'
#         ),
#         slug=product_slug,
#         categories=category
#     )

#     # Ensure unique datasheets
#     active_datasheets = product.datasheets.filter(deleted_at__isnull=True).distinct()

#     filters = ["All", "Without Part Number"]  # Part Numbers
#     width_filters = ["All", "Without Width"]
#     depth_filters = ["All", "Without Depth"]
#     height_filters = ["All", "Without Height"]
#     size_filters = ["All", "Without Size"]
#     items = []

#     if active_datasheets.exists():
#         # Part Numbers filter
#         part_numbers = active_datasheets.filter(
#             include_part_number=True,
#             part_number__isnull=False
#         ).values_list('part_number', flat=True).distinct().order_by('part_number')
#         filters.extend([str(pn) for pn in part_numbers if pn])

#         # Size filter
#         sizes = active_datasheets.filter(
#             include_size_dimensions=True,
#             size__isnull=False
#         ).values_list('size', flat=True).distinct().order_by('size')
#         size_filters.extend([str(s) for s in sizes if s])

#         # Width filter
#         widths = active_datasheets.filter(
#             include_size_dimensions=True,
#             width__isnull=False
#         ).values_list('width', flat=True).distinct().order_by('width')
#         width_filters.extend([str(w) for w in widths if w])

#         # Depth filter
#         depths = active_datasheets.filter(
#             include_size_dimensions=True,
#             depth__isnull=False
#         ).values_list('depth', flat=True).distinct().order_by('depth')
#         depth_filters.extend([str(d) for d in depths if d])

#         # Height filter
#         heights = active_datasheets.filter(
#             include_size_dimensions=True,
#             height__isnull=False
#         ).values_list('height', flat=True).distinct().order_by('height')
#         height_filters.extend([str(h) for h in heights if h])

#         for datasheet in active_datasheets:
#             item = {
#                 "id": datasheet.id,
#                 "type": str(datasheet.part_number) if datasheet.include_part_number and datasheet.part_number else "",
#                 "ProductDescription": str(datasheet.name),
#                 "size": str(datasheet.size) if datasheet.include_size_dimensions and datasheet.size else "",
#                 "width": str(datasheet.width) if datasheet.include_size_dimensions and datasheet.width else "",
#                 "depth": str(datasheet.depth) if datasheet.include_size_dimensions and datasheet.depth else "",
#                 "height": str(datasheet.height) if datasheet.include_size_dimensions and datasheet.height else "",
#                 "pdfpath": datasheet.file.url if datasheet.file else "",
#                 "description": str(datasheet.description) if datasheet.description else str(datasheet.name)
#             }
#             items.append(item)

#     initial_data = {
#         "filters": filters,
#         "sizefilters": size_filters,
#         "widthfilters": width_filters,
#         "depthfilters": depth_filters,
#         "heightfilters": height_filters,
#         "items": items,
#     }

#     # Handle documents
#     documents_by_type = {}
#     for doc in product.documents.all():
#         doc_type = doc.document_type or 'Uncategorized'
#         if doc_type not in documents_by_type:
#             documents_by_type[doc_type] = []
#         documents_by_type[doc_type].append(doc)

#     # Prepare context
#     context = {
#         'product': product,
#         'user_lists': user_lists,
#         'category': category,
#         'documents_by_type': documents_by_type,
#         'banner_url': "/media/banner_default_image/Hubnetix_default_Banner.JPG",
#         'absolute_url': request.build_absolute_uri(),
#         'initial_data': json.dumps(initial_data, ensure_ascii=False)
#     }

#     if active_datasheets.exists():
#         return render(request, 'product_home_detail_datasheet.html', context)
#     else:
#         return render(request, 'product_home_detail.html', context)


from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import json

def product_detail_view(request, category_slug, product_slug):
    # Get the category by slug
    category = get_object_or_404(Category, slug=category_slug)

    # Get user lists for authenticated users
    user_lists = []
    if request.user.is_authenticated:
        user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

    # Get the product by slug and ensure it belongs to the specified category
    product = get_object_or_404(
        Product.objects.select_related().prefetch_related(
            'categories',
            'images',
            'specifications',
            'documents',
            'datasheets'
        ),
        slug=product_slug,
        categories=category
    )

    # Ensure unique datasheets
    active_datasheets = product.datasheets.filter(deleted_at__isnull=True).distinct()

    filters = ["All", "Without Part Number"]  # Part Numbers
    width_filters = ["All", "Without Width"]
    depth_filters = ["All", "Without Depth"]
    height_filters = ["All", "Without Height"]
    size_filters = ["All", "Without Size"]
    items = []

    if active_datasheets.exists():
        # Part Numbers filter
        part_numbers = active_datasheets.filter(
            include_part_number=True,
            part_number__isnull=False
        ).values_list('part_number', flat=True).distinct().order_by('part_number')
        filters.extend([str(pn) for pn in part_numbers if pn])

        # Size filter
        sizes = active_datasheets.filter(
            include_size_dimensions=True,
            size__isnull=False
        ).values_list('size', flat=True).distinct().order_by('size')
        size_filters.extend([str(s) for s in sizes if s])

        # Width filter
        widths = active_datasheets.filter(
            include_size_dimensions=True,
            width__isnull=False
        ).values_list('width', flat=True).distinct().order_by('width')
        width_filters.extend([str(w) for w in widths if w])

        # Depth filter
        depths = active_datasheets.filter(
            include_size_dimensions=True,
            depth__isnull=False
        ).values_list('depth', flat=True).distinct().order_by('depth')
        depth_filters.extend([str(d) for d in depths if d])

        # Height filter
        heights = active_datasheets.filter(
            include_size_dimensions=True,
            height__isnull=False
        ).values_list('height', flat=True).distinct().order_by('height')
        height_filters.extend([str(h) for h in heights if h])

        # Prepare user lists for JavaScript
        user_lists_data = [{'id': ul.id, 'name': ul.name} for ul in user_lists]

        for datasheet in active_datasheets:
            item = {
                "id": datasheet.id,
                "product_id": product.id,
                "type": str(datasheet.part_number) if datasheet.include_part_number and datasheet.part_number else "",
                "ProductDescription": str(datasheet.name),
                "size": str(datasheet.size) if datasheet.include_size_dimensions and datasheet.size else "",
                "width": str(datasheet.width) if datasheet.include_size_dimensions and datasheet.width else "",
                "depth": str(datasheet.depth) if datasheet.include_size_dimensions and datasheet.depth else "",
                "height": str(datasheet.height) if datasheet.include_size_dimensions and datasheet.height else "",
                "pdfpath": datasheet.file.url if datasheet.file else "",
                "description": str(datasheet.description) if datasheet.description else str(datasheet.name),
                "include_part_number": datasheet.include_part_number,
                "include_size_dimensions": datasheet.include_size_dimensions,
                "isAuthenticated": bool(request.session.get('customerid', False)),  # Align with template's authentication check
                "user_lists": user_lists_data,
                "view_lists_url": reverse('home_list')
            }
            items.append(item)

    initial_data = {
        "filters": filters,
        "sizefilters": size_filters,
        "widthfilters": width_filters,
        "depthfilters": depth_filters,
        "heightfilters": height_filters,
        "items": items,
    }

    # Handle documents
    documents_by_type = {}
    for doc in product.documents.all():
        doc_type = doc.document_type or 'Uncategorized'
        if doc_type not in documents_by_type:
            documents_by_type[doc_type] = []
        documents_by_type[doc_type].append(doc)

    # Prepare context
    context = {
        'product': product,
        'user_lists': user_lists,
        'category': category,
        'documents_by_type': documents_by_type,
        'banner_url': "/media/banner_default_image/Hubnetix_default_Banner.JPG",
        'absolute_url': request.build_absolute_uri(),
        'initial_data': json.dumps(initial_data, ensure_ascii=False)
    }

    if active_datasheets.exists():
        return render(request, 'product_home_detail_datasheet.html', context)
    else:
        return render(request, 'product_home_detail.html', context)

######################################################################################################
######################################################################################################
######################################################################################################




def about_page(request):
    projects = Project.objects.filter(
        is_active=True,
        deleted_at__isnull=True
    ).order_by('-created_at')

    context = {
        'banner_url': static('home_assets/media/abt-banner.jpg'),
        'projects': projects
    }

    return render(request, 'about-us.html', context)


def contact_page(request):
    banner_url = static("home_assets/media/contact_bg.jpg")
    return render(request, 'contact_us.html', {'banner_url': banner_url})

#########################################################################################

from admin_dashboard.models import OfficeLocation
from django.core.serializers.json import DjangoJSONEncoder


# def partners_page(request):

#     # Fetch active office locations
#     office_locations = OfficeLocation.objects.filter(deleted_at__isnull=True)
    
    
#     active_countries = office_locations.values_list('office_country', flat=True).distinct()
    
    
#     office_country = [
#         country_choice 
#         for country_choice in OfficeLocation.OFFICE_COUNTRY 
#         if country_choice[0] in active_countries
#     ]

    
#     # Prepare locations data for JSON
#     office_locations_data = [
#         {
#             'title': loc.title,
#             'office_country': loc.office_country,
#             'address': loc.address,
#             'phone': loc.phone or '',
#             'email': loc.email or '',
#             'latitude': loc.latitude,
#             'longitude': loc.longitude,
#             'image': loc.image.url if loc.image else None
#         }
#         for loc in office_locations
#     ]
    
#     context = {
#         'banner_url': static("home_assets/media/surrport.jpg"),
#         'office_locations': office_locations,
#         'office_types': office_country,
#         'office_locations_json': json.dumps(office_locations_data, cls=DjangoJSONEncoder)
#     }
#     return render(request, 'partners.html', context)

# def partners_page(request):
#     # Fetch active office locations
#     office_locations = OfficeLocation.objects.filter(deleted_at__isnull=True)
    
#     active_countries = office_locations.values_list('office_country', flat=True).distinct()
    
#     office_country = [
#         country_choice 
#         for country_choice in OfficeLocation.OFFICE_COUNTRY 
#         if country_choice[0] in active_countries
#     ]
    
#     # Prepare locations data for JSON
#     office_locations_data = [
#         {
#             'title': loc.title,
#             'office_country': loc.office_country,
#             'partnership_type': loc.partnership_type,  # Added partnership_type here
#             'address': loc.address,
#             'phone': loc.phone or '',
#             'email': loc.email or '',
#             'latitude': loc.latitude,
#             'longitude': loc.longitude,
#             'image': loc.image.url if loc.image else None
#         }
#         for loc in office_locations
#     ]
    
#     context = {
#         'banner_url': static("home_assets/media/surrport.jpg"),
#         'office_locations': office_locations,
#         'office_types': office_country,
#         'office_locations_json': json.dumps(office_locations_data, cls=DjangoJSONEncoder)
#     }
#     return render(request, 'partners.html', context)

def partners_page(request):
    # Fetch active office locations
    office_locations = OfficeLocation.objects.filter(deleted_at__isnull=True)
    
    # Get distinct active countries
    active_countries = office_locations.values_list('office_country', flat=True).distinct()
    office_country = [
        country_choice 
        for country_choice in OfficeLocation.OFFICE_COUNTRY 
        if country_choice[0] in active_countries
    ]
    
    # Get distinct active partnership types
    active_partnership_types = office_locations.values_list('partnership_type', flat=True).distinct()
    partnership_types = [
        partnership_choice 
        for partnership_choice in OfficeLocation.PARTNERSHIP_TYPES 
        if partnership_choice[0] in active_partnership_types
    ]
    
    # Prepare locations data for JSON
    office_locations_data = [
        {
            'title': loc.title,
            'office_country': loc.office_country,
            'partnership_type': loc.partnership_type,
            'address': loc.address,
            'phone': loc.phone or '',
            'email': loc.email or '',
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'image': loc.image.url if loc.image else None
        }
        for loc in office_locations
    ]
    
    context = {
        'banner_url': static("home_assets/media/surrport.jpg"),
        'office_locations': office_locations,
        'office_types': office_country,
        'partnership_types': partnership_types,  # Add partnership_types to context
        'office_locations_json': json.dumps(office_locations_data, cls=DjangoJSONEncoder)
    }
    return render(request, 'partners.html', context)

##############################################################################

def partners_page_map(request):
    banner_url = static("home_assets/media/surrport.jpg")
    return render(request, 'partners_map.html', {'banner_url': banner_url})


#######################################################################

def support_page(request):
    banner_url = static("home_assets/media/surrport.jpg")
    return render(request, 'support.html', {'banner_url': banner_url})

def policy_page(request):
    banner_url = static("home_assets/media/policy.png")
    return render(request, 'policy.html', {'banner_url': banner_url})

def terms_page(request):
    banner_url = static("home_assets/media/terms.png")
    return render(request, 'terms.html', {'banner_url': banner_url})

def guide_page(request):
    banner_url = static("home_assets/media/e-book-bg.png")
    dummy_image = "home_assets/media/e-book-card.png"
    return render(request, 'e-book-detail.html', {'banner_url': banner_url, 'dummy_image': dummy_image})




######################################################################################################
######################################################################################################
######################################################################################################



def resources_page(request):

    banner_url = static("home_assets/media/resources_bg.jpg")
    current_time = timezone.now()


    selected_category = request.GET.get('category')


    blog_posts = BlogPost.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=current_time
    )


    if selected_category:
        blog_posts = blog_posts.filter(category=selected_category)


    blog_posts = blog_posts.order_by('-date_published')


    # Truncate descriptions
    for post in blog_posts:
        post.short_description = Truncator(post.short_description).words(20)

    context = {
        'banner_url': banner_url,
        'blog_posts': blog_posts,
        'selected_category': selected_category,
    }

    return render(request, 'resources.html', context)


##########################################################

def careers_page(request):

    banner_url = static("home_assets/media/career-bg.png")

    job_listings = JobListing.objects.filter(
        active=True,
        deleted_at__isnull=True
    ).order_by('-date_posted')

    context = {
        'banner_url': banner_url,
        'job_listings': job_listings
    }

    return render(request, 'career.html', context)


#######################################################



from django.utils import timezone
from django.utils.html import mark_safe
from itertools import chain

from django.utils.html import strip_tags
from django.utils.text import Truncator

# def news_page(request):
#     current_time = timezone.now()

#     selected_category = request.GET.get('category')

#     news_articles = list(NewsArticle.objects.filter(
#         is_active=True,
#         deleted_at__isnull=True,
#         date_published__lte=current_time,
#         is_event_news=False
#     ).order_by('-date_published'))

#     event_articles = list(NewsArticle.objects.filter(
#         is_active=True,
#         deleted_at__isnull=True,
#         is_event_news=True,
#         date_published__lte=current_time
#     ).order_by('-date_published'))

#     combined_articles = sorted(
#         news_articles + event_articles,
#         key=lambda article: article.date_published,
#         reverse=True
#     )


#     for article in combined_articles:
#         raw_text = strip_tags(article.short_description)
#         article.short_description = mark_safe(Truncator(raw_text).chars(300, truncate="..."))  # Trim to 100 chars

#     return render(request, 'news.html', {
#         'banner_url': "home_assets/media/news-bg.jpg",
#         'news_articles': news_articles,
#         'event_articles': event_articles,
#         'total_articles': len(news_articles),
#         'total_event_articles': len(event_articles)

#     })

from django.utils import timezone
from django.utils.html import mark_safe
from itertools import chain
from django.utils.html import strip_tags
from django.utils.text import Truncator

def news_page(request):
    current_time = timezone.now()

    # Get selected category from URL parameters
    selected_category = request.GET.get('category')

    # Base queries with common filters
    news_query = NewsArticle.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=current_time,
        is_event_news=False
    )

    event_query = NewsArticle.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        is_event_news=True,
        date_published__lte=current_time
    )

    # Apply category filter if selected
    if selected_category:
        news_query = news_query.filter(category=selected_category)
        event_query = event_query.filter(category=selected_category)

    # Convert to lists and sort
    news_articles = list(news_query.order_by('-date_published'))
    event_articles = list(event_query.order_by('-date_published'))

    combined_articles = sorted(
        news_articles + event_articles,
        key=lambda article: article.date_published,
        reverse=True
    )

    # Process short descriptions
    for article in combined_articles:
        raw_text = strip_tags(article.short_description)
        article.short_description = mark_safe(Truncator(raw_text).chars(300, truncate="..."))

    return render(request, 'news.html', {
        'banner_url': static("home_assets/media/news-bg.jpg"),
        'news_articles': news_articles,
        'event_articles': event_articles,
        'total_articles': len(news_articles),
        'total_event_articles': len(event_articles),
    })


#############################################################################################
from admin_dashboard.models import JobApplication
from admin_dashboard.forms import JobApplicationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse


def submit_application(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your application has been submitted successfully!'
                })
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('careers')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobApplicationForm()

    return render(request, 'careers.html', {'form': form})

###################################################################

from admin_dashboard.forms import ContactForm


def submit_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for contacting us! We will get back to you soon.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

###########################################################################################

from admin_dashboard.forms import NewsletterForm

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for subscribing to our newsletter!'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


################################################################################################

# def project_detail(request, pk):
#     project = get_object_or_404(Project, pk=pk, is_active=True, deleted_at__isnull=True)

#     context = {
#         'banner_url': "home_assets/media/abt-banner.jpg",
#         'project': project
#     }

#     return render(request, 'project_detail.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True, deleted_at__isnull=True)

    absolute_url = request.build_absolute_uri()

    context = {
        'banner_url': static("home_assets/media/abt-banner.jpg"),
        'project': project,
        'absolute_url': absolute_url
    }

    return render(request, 'project_detail.html', context)

################################################################################################



# def blog_detail(request, slug):
#     post = get_object_or_404(
#         BlogPost,
#         slug=slug,
#         is_active=True,
#         deleted_at__isnull=True,
#         date_published__lte=timezone.now()
#     )

#     absolute_url = request.build_absolute_uri()

#     context = {
#         'post': post,
#         'banner_url': "home_assets/media/resources_bg.jpg",
#         'absolute_url': absolute_url
#     }

#     return render(request, 'blog_detail.html', context)

from django.db.models import Count

def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    )

    # Get recent blogs (excluding current one)
    recent_blogs = BlogPost.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    ).exclude(id=post.id).order_by('-date_published')[:5]

    # Get all categories with their counts
    categories = BlogPost.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    ).values('category').annotate(
        count=Count('category')
    ).order_by('category')

    # Convert category choices to dict for easy lookup
    category_dict = dict(BlogPost.CATEGORY_CHOICES)

    # Add display names to categories
    for category in categories:
        category['display_name'] = category_dict.get(category['category'], category['category'])

    absolute_url = request.build_absolute_uri()

    context = {
        'post': post,
        'recent_blogs': recent_blogs,
        'categories': categories,
        'banner_url': static("home_assets/media/resources_bg.jpg"),
        'absolute_url': absolute_url
    }

    return render(request, 'blog_detail.html', context)


################################################################################################


# def news_detail(request, slug):
#     article = get_object_or_404(NewsArticle, slug=slug, is_active=True, deleted_at__isnull=True)

#     absolute_url = request.build_absolute_uri()

#     return render(request, 'news_detail.html', {
#         'article': article,
#         'absolute_url': absolute_url
#     })

from django.db.models import Count


def news_detail(request, slug):
    # Get the current article
    article = get_object_or_404(
        NewsArticle,
        slug=slug,
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    )

    # Get recent news articles (excluding current one)
    recent_news = NewsArticle.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    ).exclude(id=article.id).order_by('-date_published')[:3]

    # Get all categories with their counts
    categories = NewsArticle.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        date_published__lte=timezone.now()
    ).values('category').annotate(
        count=Count('category')
    ).order_by('category')

    # Convert category choices to dict for easy lookup
    category_dict = dict(NewsArticle.CATEGORY_CHOICES)

    # Add display names to categories
    for category in categories:
        category['display_name'] = category_dict.get(category['category'], category['category'])

    absolute_url = request.build_absolute_uri()

    context = {
        'article': article,
        'recent_news': recent_news,
        'categories': categories,
        'absolute_url': absolute_url
    }

    return render(request, 'news_detail.html', context)


################################################################################################


from admin_dashboard.forms import QuoteRequestForm

def request_quote(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Your request has been submitted successfully!'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

############################################################################################

from admin_dashboard.forms import CustomerServiceForm

def submit_customer_enquiry(request):
    if request.method == 'POST':
        form = CustomerServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Your enquiry has been submitted successfully!'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


############################################################################################

from admin_dashboard.forms import QuestionSubmissionForm


def submit_question(request):
    if request.method == 'POST':
        form = QuestionSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Your question has been submitted successfully!'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


############################################################################################

from admin_dashboard.forms import PartnerApplicationForm

def partner_application(request):
    if request.method == 'POST':
        form = PartnerApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Your application has been submitted successfully!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




#############################################################################################
#############################################################################################


from django.shortcuts import redirect, get_object_or_404
from seo_dashboard.models import OldUrlRedirect
from django.http import Http404

def   php_to_new_url_redirect(request, php_filename):
    print("#########################################")
    slug = php_filename.replace('.php', '')
    try:
        old_url_entry = get_object_or_404(OldUrlRedirect, old_slug=slug)
    except Http404:
        return redirect('home-page', permanent=True)

    if old_url_entry.url_type == 'category':
        return redirect('user_account-category_view',
                        category_slug=old_url_entry.new_slug,
                        permanent=True)
    elif old_url_entry.url_type == 'product':
        try:
            product = Product.objects.get(slug=old_url_entry.new_slug)
            category = product.categories.first()
            if category:
                return redirect('user_account-product_detail_view',
                                category_slug=category.slug,
                                product_slug=old_url_entry.new_slug,
                                permanent=True)
            else:
                return redirect('user_account-product_detail_view',
                                category_slug='-',
                                product_slug=old_url_entry.new_slug,
                                permanent=True)
        except Product.DoesNotExist:
            return redirect('home-page', permanent=True)

    elif old_url_entry.url_type == 'news':
        return redirect('home-news_detail',
                        slug=old_url_entry.new_slug,
                        permanent=True)
    elif old_url_entry.url_type == 'blog':
        return redirect('home-blog_detail',
                        slug=old_url_entry.new_slug,
                        permanent=True)
    elif old_url_entry.url_type == 'projects':
        return redirect('home-project_detail',
                        slug=old_url_entry.new_slug,
                        permanent=True)
    else:
        return redirect('home-page')


#############################################################################################
#############################################################################################
#############################################################################################

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.core.cache import cache

@require_http_methods(["GET"])
@cache_page(60 * 15)
def optimized_search(request):
    search_query = request.GET.get('q', '').strip()

    cache_key = f'search_{search_query}'
    cached_results = cache.get(cache_key)
    if cached_results:
        return JsonResponse(cached_results, safe=False)

    results = []
    if search_query:
        def normalize_text(text):
            return ''.join(text.lower().split())
        clean_search_query = normalize_text(search_query)

        # Product Query
        product_query = Product.objects.filter(
            Q(name__icontains=search_query),
            deleted_at__isnull=True
        ).select_related().prefetch_related('categories', 'datasheets')

        # Category Query
        category_query = Category.objects.filter(
            Q(name__icontains=search_query),
            is_active=True,
            deleted_at__isnull=True
        )

        # Datasheet Query
        datasheet_query = Datasheet.objects.filter(
            Q(name__icontains=search_query) |
            Q(part_number__icontains=search_query),
            deleted_at__isnull=True
        ).select_related('product')

        results = [
            *[{
                'type': 'product',
                'name': result.name,
                'name_slug': result.slug,
                'category_slug': result.categories.first().slug if result.categories.exists() else '',
                'description': result.short_description or 'N/A',
                'stock': result.quantity_in_stock,
                'has_datasheet': result.datasheets.exists()
            } for result in product_query[:20]],
            *[{
                'type': 'category',
                'name': result.name,
                'name_slug': result.slug,
            } for result in category_query[:10]],
            *[{
                'type': 'datasheet',
                'name': result.name,
                'product_name': result.product.name,
                'product_slug': result.product.slug,
                'category_slug': result.product.categories.first().slug if result.product.categories.exists() else '',
                'part_number': result.part_number or 'N/A',
                'file_url': result.file.url if result.file else ''  # Add file URL for datasheets
            } for result in datasheet_query[:10]]
        ]
        cache.set(cache_key, results, 900)

    return JsonResponse(results, safe=False)




######################################################################################################
######################################################################################################
######################################################################################################
# List Related Function


from django.contrib.auth.decorators import login_required
from  admin_dashboard.models import  TheList,ListItem,AdminRequestQuote, AdminRequestQuoteItem, Datasheet
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import xlwt


@customer_required
def home_list(request):
    user_lists = []

    if request.user.is_authenticated:
        # Optimize by fetching ordered lists once; create default if none exist
        user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', '-created_at')


        if not user_lists.exists():
            TheList.objects.create(user=request.user, name="Default List", is_default=True)
            user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    return render(request, "list.html", {
        "user_lists": user_lists,
        "is_authenticated": request.user.is_authenticated
    })


@customer_required
@csrf_protect
def get_active_list_count(request):
    if request.user.is_authenticated:
        active_count = TheList.objects.filter(user=request.user).count()
        print("######################")
        print(active_count)
        return JsonResponse({'active_count': active_count})
    return JsonResponse({'active_count': 0}, status=403)

# Consolidated list creation view (replaces create_list and create_list_modal)
from django.db import IntegrityError
import logging
logger = logging.getLogger(__name__)

@customer_required
@csrf_protect
def create_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.method == "POST":
        name = request.POST.get("list_name")
        note = request.POST.get("list_note", "")
        product_id = request.POST.get("product_id")

        if not name:
            return JsonResponse({"success": False, "error": "List name is required"})

        # Check if list already exists before creating
        if TheList.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({"success": False, "error": "A list with this name already exists"})

        try:
            logger.info(f"Creating list '{name}' for user {request.user.id}")

            # Use get_or_create to prevent duplicate creation
            new_list, created = TheList.objects.get_or_create(
                user=request.user,
                name=name,
                defaults={"note": note}
            )

            if not created:
                return JsonResponse({"success": False, "error": "A list with this name already exists"})

            if product_id:
                product = get_object_or_404(Product, id=product_id)
                ListItem.objects.create(list=new_list, product_id=product, product_name=product.name, quantity=1)

            return JsonResponse({
                "success": True,
                "list_id": new_list.id,
                "list_name": new_list.name,
                "created": created
            })

        except IntegrityError:
            return JsonResponse({"success": False, "error": "A list with this name already exists"})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@customer_required
def edit_list(request):
    if request.method == "POST":
        list_id = request.POST.get("list_id")
        the_list = get_object_or_404(TheList, id=list_id, user=request.user)
        new_name = request.POST.get("list_name")
        new_note = request.POST.get("list_note", None) # None if not provided

        # Update name if provided and not default
        if new_name and new_name != the_list.name and not the_list.is_default:
            if TheList.objects.filter(user=request.user, name=new_name).exists():
                return JsonResponse({"success": False, "error": "List name already exists"})
            the_list.name = new_name

        # Update note if provided (allow empty string)
        if new_note is not None and new_note != the_list.note:
            the_list.note = new_note

        the_list.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@customer_required
@csrf_protect
def delete_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)
    if request.method == "POST":
        list_id = request.POST.get("list_id")
        product_list = get_object_or_404(TheList, id=list_id, user=request.user)
        product_list.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@customer_required
@csrf_protect
def add_to_list(request):
    print("#########OK#######################")
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        # Get the raw list_ids[] value first
        list_ids = request.POST.get("list_ids[]")  # Get single value (might be comma-separated)

        # Handle list_ids based on whether it's a string or not
        if isinstance(list_ids, str):
            try:
                list_ids = [id.strip() for id in list_ids.split(",")]
            except (ValueError, AttributeError):
                return JsonResponse({"success": False, "error": "Invalid list IDs format"}, status=400)
        else:
            list_ids = request.POST.getlist("list_ids[]")  # Fallback to getlist for multiple values

        if not product_id or not list_ids:
            return JsonResponse({"success": False, "error": "Product and list selection required"}, status=400)

        product = get_object_or_404(Product, id=product_id)
        for list_id in list_ids:
            try:
                # Convert list_id to integer to match TheList model's id field
                list_id = int(list_id)
                product_list = get_object_or_404(TheList, id=list_id, user=request.user)
                existing_item = ListItem.objects.filter(list=product_list, product_id=product).first()
                if existing_item:
                    existing_item.quantity += 1
                    existing_item.save()
                else:
                    ListItem.objects.create(
                        list=product_list,
                        product_id=product,
                        product_name=product.name,
                        quantity=1
                    )
            except (ValueError, TypeError):
                return JsonResponse({"success": False, "error": f"Invalid list ID: {list_id}"}, status=400)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@customer_required
def get_user_lists(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)
    user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')
    lists_data = [{"id": lst.id, "name": lst.name, "is_default": lst.is_default} for lst in user_lists]
    return JsonResponse({"success": True, "lists": lists_data})

@customer_required
def list_items(request, list_id):
    product_list = get_object_or_404(TheList, id=list_id, user=request.user)
    list_items = ListItem.objects.filter(list=product_list).order_by('date_added')
    paginator = Paginator(list_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(list_items)
    for item in list_items:
        if item.product_id.measurement:
            print(f"{item.product_name}: {item.product_id.measurement}")
    return render(request, "list_items.html", {
        "list": product_list,
        "page_obj": page_obj,
        "is_authenticated": request.user.is_authenticated
    })


@customer_required
@csrf_exempt
def update_item_quantity(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity", 0))
        if quantity <= 0:
            return JsonResponse({"status": "error", "message": "Quantity must be greater than zero"})
        item = get_object_or_404(ListItem, id=item_id, list__user=request.user)
        item.quantity = quantity
        item.save()
        return JsonResponse({"status": "success", "message": "Quantity updated"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@customer_required
@csrf_exempt
def delete_selected_items(request):
    if request.method == "POST":
        item_ids = request.POST.getlist("item_ids[]") or json.loads(request.body).get("item_ids", [])
        if not item_ids:
            return JsonResponse({"status": "error", "message": "No items selected"})
        items = ListItem.objects.filter(id__in=item_ids, list__user=request.user)
        count = items.count()
        items.delete()
        return JsonResponse({"status": "success", "message": f"{count} items deleted"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

#####################################################################################

# @customer_required
# @csrf_exempt
# def request_for_quote(request, list_id):
#     if request.method == "POST":
#         try:
#             # Fetch the list and ensure it belongs to the user
#             the_list = get_object_or_404(TheList, id=list_id, user=request.user)
#             print(the_list)
#             list_items = ListItem.objects.filter(list=the_list)
#             print(list_items)

#             if not list_items.exists():
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Cannot request a quote for an empty list'
#                 }, status=400)

#             # Create a new AdminRequestQuote with all relevant data
#             quote_request = AdminRequestQuote.objects.create(
#                 user=request.user,
#                 user_username=request.user.username,
#                 list_name=the_list.name,
#                 list_note=the_list.note,
#                 total_items=list_items.count(),
#                 notes=f"Quote request for list: {the_list.name}"
#             )

#             # Create AdminRequestQuoteItem for each ListItem
#             for item in list_items:
#                 AdminRequestQuoteItem.objects.create(
#                     quote_request=quote_request,
#                     product=item.product_id,
#                     product_name=item.product_name,
#                     quantity=item.quantity
#                 )

#             # Notify user of success
#             messages.success(request, "Quote request submitted successfully.")

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Quote request submitted successfully',
#                 'quote_request_id': quote_request.id
#             })

#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"Error submitting quote request: {str(e)}"
#             }, status=400)

#     return JsonResponse({
#         'status': 'error',
#         'message': 'Invalid request method'
#     }, status=400)

import os
import tempfile
from datetime import datetime
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
import openpyxl

@customer_required
@csrf_exempt
def request_for_quote(request, list_id):
    if request.method == "POST":
        try:
            # Fetch the list and ensure it belongs to the user
            the_list = get_object_or_404(TheList, id=list_id, user=request.user)
            list_items = ListItem.objects.filter(list=the_list)

            if not list_items.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cannot request a quote for an empty list'
                }, status=400)

            # Create a new AdminRequestQuote with all relevant data
            quote_request = AdminRequestQuote.objects.create(
                user=request.user,
                user_username=request.user.username,
                list_name=the_list.name,
                list_note=the_list.note,
                total_items=list_items.count(),
                notes=f"Quote request for list: {the_list.name}"
            )

            # Create AdminRequestQuoteItem for each ListItem
            for item in list_items:
                AdminRequestQuoteItem.objects.create(
                    quote_request=quote_request,
                    product=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity
                )



            # Generate and send email with Excel attachment
            try:
                # Create Excel workbook
                wb = openpyxl.Workbook()



                # Customer Information Sheet
                user_sheet = wb.active
                user_sheet.title = "Customer Information"

                # Customer Details Section
                user_sheet.append(["Customer Details"])
                user_sheet.append(["Username", request.user.username])
                user_sheet.append(["Email", request.user.email])
                user_sheet.append(["Full Name", f"{request.user.first_name} {request.user.last_name}".strip()])
                user_sheet.append(["Phone", request.user.phone])

                # Empty Row for Separation
                user_sheet.append([])

                # Quote Details Section
                user_sheet.append(["Quote Request Details"])
                # user_sheet.append(["List Name", the_list.name])
                # user_sheet.append(["List Note", the_list.note])
                user_sheet.append(["Total Items", list_items.count()])
                user_sheet.append(["Request Date", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')])

                # Empty Row for Separation
                user_sheet.append([])

                # Requested Items Section
                user_sheet.append(["Requested Items"])
                user_sheet.append(["Product Category", "Product Name", "Quantity"])
                for item in list_items:
                    user_sheet.append([
                        str(item.product_id),
                        item.product_name,
                        item.quantity
                    ])


                # Save to temporary file and send email
                # Use a specific temporary directory with write permissions
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
                os.makedirs(temp_dir, exist_ok=True)  # Create temp directory if it doesn't exist

                with tempfile.NamedTemporaryFile(suffix='.xlsx', dir=temp_dir, delete=False) as tmp:
                    temp_file_path = tmp.name
                    wb.save(temp_file_path)
                    tmp.seek(0)

                    # Create email
                    email = EmailMessage(
                        subject=f'New Quote Request from {request.user.username} - {datetime.utcnow().strftime("%Y-%m-%d")}',
                        body=f'''New quote request received from {request.user.username}

List Name: {the_list.name}
Total Items: {list_items.count()}
Request Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please find the detailed quote request information in the attached Excel file.''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=['rashad.sysitco@gmail.com'],
                    )

                    # Attach Excel file
                    with open(temp_file_path, 'rb') as f:
                        email.attach(
                            f'quote_request_{quote_request.id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx',
                            f.read(),
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )

                    # Send email
                    email.send()

                # Clean up temporary file
                os.remove(temp_file_path)

            except Exception as email_error:
                # Log the email error but don't stop the quote request process
                print(f"Error sending email: {str(email_error)}")
                # You might want to add proper logging here

            # Notify user of success
            messages.success(request, "Quote request submitted successfully.")

            return JsonResponse({
                'status': 'success',
                'message': 'Quote request submitted successfully',
                'quote_request_id': quote_request.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Error submitting quote request: {str(e)}"
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


###########################################################################################

@customer_required
@csrf_exempt
def export_to_excel(request, list_id):
    product_list = get_object_or_404(TheList, id=list_id, user=request.user)
    list_items = ListItem.objects.filter(list=product_list).order_by("date_added")
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={product_list.name}_products.xls"
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet(f"{product_list.name} Products")
    headers = ["Product Name", "Description", "Categories", "Quantity"]
    style = xlwt.XFStyle()
    style.font.bold = True
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, style)
    for row, item in enumerate(list_items, 1):
        categories = ", ".join(category.name for category in item.product_id.categories.all())
        worksheet.write(row, 0, item.product_name)
        worksheet.write(row, 1, item.product_id.short_description)  # Adjust if field name differs
        worksheet.write(row, 2, categories)
        worksheet.write(row, 3, item.quantity)
    workbook.save(response)
    return response

@customer_required
@csrf_exempt
def download_specifications(request, list_id):
    product_list = get_object_or_404(TheList, id=list_id, user=request.user)
    list_items = ListItem.objects.filter(list=product_list).order_by("date_added")
    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename={product_list.name}_specifications.txt"
    for item in list_items:
        response.write(f"Product: {item.product_name}\nDescription: {item.product_id.short_description}\nQuantity: {item.quantity}\n{'-' * 50}\n")
    return response

@customer_required
@csrf_exempt
def download_product_list(request, list_id):
    product_list = get_object_or_404(TheList, id=list_id, user=request.user)
    list_items = ListItem.objects.filter(list=product_list).order_by("date_added")
    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename={product_list.name}_product_list.txt"
    response.write(f"Product List: {product_list.name}\nDate: {product_list.modified_date.strftime('%Y-%m-%d')}\n{'-' * 50}\n\n")
    for i, item in enumerate(list_items, 1):
        response.write(f"{i}. {item.product_name} - Qty: {item.quantity}\n")
    return response

@customer_required
def duplicate_list(request, list_id):
    if request.method == "POST":
        # Get the original list
        source_list = get_object_or_404(TheList, id=list_id, user=request.user)
        # Get the duplicate name from the form, default to empty string
        duplicate_name = request.POST.get("duplicate_name", "").strip()

        # Determine the new name
        if duplicate_name:
            new_name = duplicate_name
        else:
            new_name = f"{source_list.name} (Copy)"

        # Ensure the name is unique
        counter = 1
        base_name = new_name
        while TheList.objects.filter(user=request.user, name=new_name).exists():
            new_name = f"{base_name} ({counter})"
            counter += 1

        # Create the new list
        new_list = TheList(user=request.user, name=new_name, note=source_list.note)
        new_list.save()

        # Copy all items to the new list
        for item in ListItem.objects.filter(list=source_list):
            ListItem.objects.create(
                list=new_list,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity
            )

        return JsonResponse({"success": True, "list_id": new_list.id, "list_name": new_list.name})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@customer_required
def share_list(request, list_id):
    get_object_or_404(TheList, id=list_id, user=request.user)
    share_url = request.build_absolute_uri(f"/shared-list/{list_id}/")
    return JsonResponse({"success": True, "share_url": share_url})

@customer_required
def make_default_list(request, list_id):
    if request.method == "POST":
        TheList.objects.filter(user=request.user, is_default=True).update(is_default=False)
        product_list = get_object_or_404(TheList, id=list_id, user=request.user)
        product_list.is_default = True
        product_list.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


################################################################################################

# @customer_required
# @csrf_protect
# def add_to_list_datasheet(request):
#     print("----checking---")
#     if not request.user.is_authenticated:
#         return JsonResponse({"success": False, "error": "Login required"}, status=401)

#     if request.method == "POST":
#         product_id = request.POST.get("product_id")
#         datasheet_id = request.POST.get("datasheet_id")
#         datasheet_name = request.POST.get("datasheet_name")
#         list_ids = request.POST.getlist("list_ids[]")

#         # Print datasheet ID and name
#         print(f"Datasheet ID: {datasheet_id}, Datasheet Name: {datasheet_name}")

#         if not product_id or not list_ids:
#             return JsonResponse({"success": False, "error": "Product and list selection required"})

#         product = get_object_or_404(Product, id=product_id)
#         for list_id in list_ids:
#             product_list = get_object_or_404(TheList, id=list_id, user=request.user)
#             existing_item = ListItem.objects.filter(list=product_list, product_id=product).first()
#             if existing_item:
#                 existing_item.quantity += 1
#                 existing_item.save()
#             else:
#                 ListItem.objects.create(
#                     list=product_list,
#                     product_id=product,
#                     product_name=product.name,
#                     quantity=1
#                     # Optionally add datasheet_id or datasheet_name if needed in the model
#                 )

#         return JsonResponse({"success": True})

#     return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@customer_required
@csrf_protect
def add_to_list_datasheet(request):
    print("----checking---")
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        datasheet_id = request.POST.get("datasheet_id")
        datasheet_name = request.POST.get("datasheet_name")
        # Get the raw list_ids[] value first
        list_ids = request.POST.get("list_ids[]")

        # Print datasheet ID and name for debugging
        print(f"Datasheet ID: {datasheet_id}, Datasheet Name: {datasheet_name}")

        # Handle list_ids based on whether it's a string or not
        if isinstance(list_ids, str):
            try:
                list_ids = [id.strip() for id in list_ids.split(",")]
            except (ValueError, AttributeError):
                return JsonResponse({"success": False, "error": "Invalid list IDs format"}, status=400)
        else:
            list_ids = request.POST.getlist("list_ids[]")  # Fallback to getlist for multiple values

        if not product_id or not list_ids:
            return JsonResponse({"success": False, "error": "Product and list selection required"}, status=400)

        product = get_object_or_404(Product, id=product_id)
        datasheet = None

        # Handle datasheet if datasheet_id is provided
        if datasheet_id:
            datasheet = get_object_or_404(Datasheet, id=datasheet_id)

        for list_id in list_ids:
            try:
                # Convert list_id to integer to match TheList model's id field
                list_id = int(list_id)
                product_list = get_object_or_404(TheList, id=list_id, user=request.user)

                # Check for an existing item by datasheet if it exists, otherwise by product
                existing_item = (
                    ListItem.objects.filter(list=product_list, datasheet=datasheet).first()
                    if datasheet
                    else ListItem.objects.filter(list=product_list, product_id=product).first()
                )

                if existing_item:
                    # Update quantity if the item already exists
                    existing_item.quantity += 1
                    existing_item.save()
                else:
                    # Create a new ListItem
                    ListItem.objects.create(
                        list=product_list,
                        product_id=product,
                        product_name=datasheet.name if datasheet else product.name,
                        quantity=1,
                        datasheet=datasheet
                    )
            except (ValueError, TypeError):
                return JsonResponse({"success": False, "error": f"Invalid list ID: {list_id}"}, status=400)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

######################################################################################################
######################################################################################################
######################################################################################################



def latest_products_view(request):
    print("###############################--latest_products_view--####################")

    # Get latest products with their categories
    products = Product.objects.filter(
        is_latest=True,
        deleted_at__isnull=True,
        latest_marked_at__isnull=False
    ).select_related().prefetch_related(
        'categories'
    ).order_by('-latest_marked_at')

    products_count = products.count()

    # Get user lists if authenticated
    user_lists = []
    if request.user.is_authenticated:
        user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

    context = {
        'products': products,
        'products_count': products_count,
        'user_lists': user_lists,
        'page_title': 'Latest Products',
        'banner_url': static("home_assets/media/Latest_Products.png"),
        'absolute_url': request.build_absolute_uri(),
        'is_latest_page': True  # To identify this is latest products page
    }

    return render(request, 'product_featured_latest_listing.html', context)

def featured_products_view(request):
    print("###############################--featured_products_view--####################")

    # Get featured products with their categories
    products = Product.objects.filter(
        is_featured=True,
        deleted_at__isnull=True,
        featured_marked_at__isnull=False
    ).select_related().prefetch_related(
        'categories'
    ).order_by('-featured_marked_at')

    products_count = products.count()

    # Get user lists if authenticated
    user_lists = []
    if request.user.is_authenticated:
        user_lists = TheList.objects.filter(user=request.user).order_by('-is_default', 'name')

    context = {
        'products': products,
        'products_count': products_count,
        'user_lists': user_lists,
        'page_title': 'Featured Products',
        'banner_url': static("home_assets/media/Featured_Products.png"),
        'absolute_url': request.build_absolute_uri(),
        'is_featured_page': True  # To identify this is featured products page
    }

    return render(request, 'product_featured_latest_listing.html', context)