##############################################################################
#   2024-12-13 login 

from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timedelta
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
import json
from django.utils import timezone  


User = get_user_model()

# def login_page(request):
#     return render(request,'login.html')


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth import logout
from django.urls import reverse

@ensure_csrf_cookie
@require_POST
def check_existing_session(request):
    if request.headers.get('X-Handle-Logout') == 'true':
        # If logout is requested, perform logout and return success
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
    
    if 'adminid' in request.session:
        return JsonResponse({
            'has_session': True,
            'session_type': 'Admin Dashboard',
            'redirect_url': reverse('admin_dashboard-dashboard')
        })
    elif 'seomanagerid' in request.session:
        return JsonResponse({
            'has_session': True,
            'session_type': 'SEO Manager Dashboard',
            'redirect_url': reverse('seo_dashboard-dashboard')
        })
    elif 'partnermanagerid' in request.session:
        return JsonResponse({
            'has_session': True,
            'session_type': 'Partner Manager Dashboard',
            'redirect_url': reverse('partner_dashboard-dashboard')
        })
    
    return JsonResponse({
        'has_session': False
    })


@ensure_csrf_cookie
def login_page(request):

    existing_session = None
    if 'adminid' in request.session:
        existing_session = 'Admin Dashboard'
        return redirect('admin_dashboard-dashboard')
    elif 'seomanagerid' in request.session:
        existing_session = 'SEO Manager Dashboard'
        return redirect('seo_dashboard-dashboard')
    elif 'partnermanagerid' in request.session:
        existing_session = 'Partner Manager Dashboard'
        return redirect('partner_dashboard-dashboard')
    else:
        request.session.flush()
        print("###############section cleared###########")
        
    if existing_session:
        messages.warning(request, f"You are currently logged in to {existing_session}. Please logout first before accessing another account.")
        
    return render(request, 'login.html')

    ##############################################


"""
Secure Login View with Features:
- Multi-factor login attempt tracking
- Account lockout after 5 failed attempts
- 15-minute lockout duration
- Session timeout (15 minutes)
- Restricted to specific account types
- Prevents brute-force attacks
"""




@ensure_csrf_cookie
def account_login(request):
    SESSION_TIMEOUT = getattr(settings, 'SESSION_TIMEOUT', 4000)
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15 * 60
    
    # Check for existing sessions first
    existing_session = None
    if 'adminid' in request.session:
        existing_session = 'Admin Dashboard'
        return redirect('admin_dashboard-dashboard')
    elif 'seomanagerid' in request.session:
        existing_session = 'SEO Manager Dashboard'
        return redirect('seo_dashboard-dashboard')
    elif 'partnermanagerid' in request.session:
        existing_session = 'Partner Manager Dashboard'
        return redirect('partner_dashboard-dashboard')
    else:
        request.session.flush()
        print("###############section cleared###########")
    

        
    if existing_session:
        messages.warning(request, f"You are currently logged in to {existing_session}. Please logout first before accessing another account.")
        return redirect('account-login-page')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            
            # Handle previous day's login attempts
            if user.failed_attempts:
                failed_attempts = json.loads(user.failed_attempts)
                today = now().date()
                failed_attempts = [
                    attempt for attempt in failed_attempts
                    if timezone.datetime.strptime(attempt, '%Y-%m-%d').date() == today
                ]
                user.failed_attempts = json.dumps(failed_attempts)
                user.login_attempts = len(failed_attempts)
                user.save()
            
            # Check for lockout
            if user.is_locked_out and user.locked_out_until and user.locked_out_until > now():
                remaining_time = int((user.locked_out_until - now()).total_seconds())
                messages.error(request, f"Account is locked. Try again in {remaining_time // 60} minutes.")
                return render(request, 'login.html')
    
        except User.DoesNotExist:
            user = None
        
        # Authenticate the user
        authenticated_user = authenticate(request, email=email, password=password)
        
        if authenticated_user:
            # Reset security counters
            authenticated_user.login_attempts = 0
            authenticated_user.is_locked_out = False
            authenticated_user.locked_out_until = None
            authenticated_user.failed_attempts = json.dumps([])
            authenticated_user.last_login_attempt = now()
            authenticated_user.save()
            
            
            if authenticated_user.account_type and authenticated_user.account_type.id == 1:  
                request.session['adminid'] = authenticated_user.id
                redirect_url = 'admin_dashboard-dashboard'
            elif authenticated_user.account_type and authenticated_user.account_type.id == 2:  
                request.session['seomanagerid'] = authenticated_user.id
                redirect_url = 'seo_dashboard-dashboard' 
            elif authenticated_user.account_type and authenticated_user.account_type.id == 3:
                request.session['partnermanagerid'] = authenticated_user.id
                redirect_url = 'partner_dashboard-dashboard' 
            else:
                messages.error(request, "Access denied. Invalid account type.")
                return render(request, 'login.html')
                
            # Standard login
            auth_login(request, authenticated_user)
            request.session.set_expiry(SESSION_TIMEOUT)
            request.session['last_activity'] = now().timestamp()
            
            return redirect(redirect_url)
        else:
            try:
                user = User.objects.get(email=email)
                user.login_attempts += 1
                
                failed_attempts = json.loads(user.failed_attempts) if user.failed_attempts else []
                failed_attempts.append(str(now().date()))
                user.failed_attempts = json.dumps(failed_attempts)
                
                if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.is_locked_out = True
                    user.locked_out_until = now() + timedelta(seconds=LOCKOUT_DURATION)
                    messages.error(request, f"Too many failed attempts. Account locked for {LOCKOUT_DURATION // 60} minutes.")
                else:
                    messages.error(request, "Invalid email or password.")
                
                user.save()
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
        
        return render(request, 'login.html')
    
    # Check for session timeout
    if request.user.is_authenticated:
        last_activity = request.session.get('last_activity')
        if last_activity and now().timestamp() - last_activity > SESSION_TIMEOUT:
            logout(request)
            messages.warning(request, "Session expired due to inactivity. Please log in again.")
    
    return render(request, 'login.html')


################################################################################

from django.http import JsonResponse
from .models import AccountType
from django.utils.translation import gettext as _
from admin_dashboard.views import admin_required


@admin_required
def create_account_type(request):

    return JsonResponse({'message': 'Please Contact Admin'})


    """
    Create account types with predefined configurations
    """
    try:
        # Define account types configurations
        account_types = [
            {
                'type': 'Admin',
                'description': '''
                Administrator account with full privileges.
                Access Levels:
                - Full system access
                - User management
                - Configuration settings
                - System monitoring
                '''.strip(),
                'is_active': True
            },
            {
                'type': 'SEO Manager',
                'description': '''
                SEO Manager account for content optimization.
                Access Levels:
                - SEO analytics
                - Content management
                - Performance tracking
                - Keyword optimization
                '''.strip(),
                'is_active': True
            },
            {
                'type': 'Partner',
                'description': '''
                Partner account type for business collaborators.
                Access Levels:
                - Partnership dashboard
                - Business analytics
                - Resource management
                - Collaboration tools
                '''.strip(),
                'is_active': True
            },
            {
                'type': 'Customer',
                'description': '''
                Customer account type for individual users.
                Access Levels:
                - Personal dashboard
                - Order tracking
                - Loyalty program
                - Customer support
                '''.strip(),
                'is_active': True
            }
        ]

        created_types = []
        
        # Create each account type
        for account_type in account_types:
            # Check if account type already exists
            existing_type = AccountType.objects.filter(type=account_type['type']).first()
            
            if existing_type:
                # Update existing account type
                existing_type.description = account_type['description']
                existing_type.is_active = account_type['is_active']
                existing_type.save()
                created_types.append(existing_type)
            else:
                # Create new account type
                new_type = AccountType.objects.create(
                    type=account_type['type'],
                    description=account_type['description'],
                    is_active=account_type['is_active']
                )
                created_types.append(new_type)

        # Prepare response data
        response_data = {
            'status': 'success',
            'message': _('Account types created/updated successfully'),
            'data': [{
                'id': type_obj.id,
                'type': type_obj.type,
                'description': type_obj.description,
                'is_active': type_obj.is_active
            } for type_obj in created_types]
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


################################################################################

from django.http import JsonResponse
from .models import SEOManager
from .models import AdminUser,Partner,Customer
from admin_dashboard.views import admin_required

@admin_required
def create_admin_user(request):
    print("####################")
    
    # admin = AdminUser.objects.get(email='admin@hubnetix.com')
    # print(admin.username)
    
    return JsonResponse({'message': 'Please Contact Admin'})

    # email = request.POST.get('email', 'admin@hubnetix.com')
    # username = request.POST.get('username', 'hubnetix_admin')
    # password = request.POST.get('password', 'admin@123')
    # first_name = request.POST.get('first_name', 'Admin')
    # last_name = request.POST.get('last_name', 'Hubnetix')
    # admin_level = request.POST.get('admin_level', 1)

    # admin_user = AdminUser.objects.create_user(
    #     email=email,
    #     username=username,
    #     password=password,
    #     first_name=first_name,
    #     last_name=last_name,
    #     admin_level=admin_level
    # )
    # return JsonResponse({'message': 'Admin user created successfully', 'user_id': admin_user.id})




    # email = request.POST.get('email', 'seo@hubnetix.com')
    # username = request.POST.get('username', 'seoexpert')
    # password = request.POST.get('password', 'admin@123')
    # first_name = request.POST.get('first_name', 'SEO')
    # last_name = request.POST.get('last_name', 'Expert')
    # managed_domains = request.POST.getlist('managed_domains', ['hubnetix.com'])
    # report_frequency = request.POST.get('report_frequency', 'weekly')
    
    # seo_manager = SEOManager.objects.create_user(
    #     email=email,
    #     username=username,
    #     password=password,
    #     first_name=first_name,
    #     last_name=last_name,
    #     managed_domains=managed_domains,
    #     report_frequency=report_frequency
    # )
    # return JsonResponse({'message': 'User created successfully', 'user_id': seo_manager.id})




    # Get data from POST request with default values
    # email = request.POST.get('email', 'partner_1@hubnetix.com')
    # username = request.POST.get('username', 'partner123_1')
    # password = request.POST.get('password', 'admin@123_1')
    # first_name = request.POST.get('first_name', 'Partner_1')
    # last_name = request.POST.get('last_name', 'User_1')
    # partner_company_name = request.POST.get('partner_company_name', 'Partner Company_1')  
    # business_type = request.POST.get('business_type', 'Technology')
    # partnership_level = request.POST.get('partnership_level', 'BRONZE')
    
    # try:
    #     # Create the partner user using create_user method
    #     partner = Partner.objects.create_user(
    #         email=email,
    #         username=username,
    #         password=password,
    #         first_name=first_name,
    #         last_name=last_name,
    #         partner_company_name=partner_company_name,
    #         business_type=business_type,
    #         partnership_level=partnership_level
    #     )
        
    #     return JsonResponse({
    #         'message': 'Partner user created successfully',
    #         'user_id': partner.id,
    #         'company': partner.partner_company_name,
    #         'partnership_level': partner.partnership_level
    #     })
        
    # except Exception as e:
    #     return JsonResponse({
    #         'error': str(e),
    #         'message': 'Failed to create partner user'
    #     }, status=400)


    # # Get data from POST request with default values
    # email = request.POST.get('email', 'customer_1@example.com')
    # username = request.POST.get('username', 'customer123')
    # password = request.POST.get('password', 'customer@123')
    # first_name = request.POST.get('first_name', 'Customer')
    # last_name = request.POST.get('last_name', 'User')

    # try:
    #     # Create the customer user using create_user method
    #     customer = Customer.objects.create_user(
    #         email=email,
    #         username=username,
    #         password=password,
    #         first_name=first_name,
    #         last_name=last_name
    #     )

    #     return JsonResponse({
    #         'message': 'Customer user created successfully',
    #         'user_id': customer.id,
    #         'username': customer.username,
    #         'email': customer.email
    #     })

    # except Exception as e:
    #     return JsonResponse({
    #         'error': str(e),
    #         'message': 'Failed to create customer user'
    #     }, status=400)











