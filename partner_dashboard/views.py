from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from catalog.models import Product,Category
from functools import wraps
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import JsonResponse

User = get_user_model() 

def partner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'partnermanagerid' in request.session:
            try:
                user = User.objects.get(id=request.session['partnermanagerid'])
                if user.account_type and user.account_type.id == 3:
                    # Update last activity timestamp
                    request.session['last_activity'] = now().timestamp()
                    # Temporarily login this user for the duration of this request
                    auth_login(request, user)
                    return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                pass
        return redirect('account-login-page')
    return wrapper




@partner_required
def dashboard_view(request):
    total_resource = Resource.objects.filter(deleted_at__isnull=True).count()
    


    context = {
        'total_resource': total_resource,
    }
    return render(request, 'partner_dashboard.html', context)


def dashboard_logout(request):
	logout(request)
	request.session.clear()
	return redirect('account-login-page')

###########################################################################################################
###########################################################################################################

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
import os
from admin_dashboard .models import Resource
from django.http import FileResponse, Http404


@partner_required
def resource_list(request):
    queryset = Resource.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(resource_type__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'resource_type', 'created_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(1)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)
    
    context = {
        'resources': resources,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_resources': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'partner_resource_list.html', context)

@partner_required
def resource_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'partner_resource_details.html', {'resource': resource})


@partner_required
def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    try:
        response = FileResponse(resource.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(resource.file.name)}"'
        return response
    except FileNotFoundError:
        raise Http404("File not found")