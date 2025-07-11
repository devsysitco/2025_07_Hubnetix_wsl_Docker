from django.shortcuts import render
from functools import wraps
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model() 

# Create your views here.
def seo_manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'seomanagerid' in request.session:
            try:
                user = User.objects.get(id=request.session['seomanagerid'])
                if user.account_type and user.account_type.id == 2:
                    # Update last activity timestamp
                    request.session['last_activity'] = now().timestamp()
                    # Temporarily login this user for the duration of this request
                    auth_login(request, user)
                    return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                pass 
        return redirect('account-login-page')
    return wrapper


###########################################################################

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from catalog.models import Product,Category
from admin_dashboard.models import NewsArticle,BlogPost,JobListing





@seo_manager_required
def dashboard_view(request):
    total_categories = Category.objects.filter(deleted_at__isnull=True).count()
    total_products = Product.objects.filter(deleted_at__isnull=True).count()
    total_news = NewsArticle.objects.filter(deleted_at__isnull=True).count()
    total_blogs = BlogPost.objects.filter(deleted_at__isnull=True).count()
    total_jobs = JobListing.objects.filter(deleted_at__isnull=True).count()

    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_news': total_news,
        'total_blogs': total_blogs,
        'total_jobs': total_jobs,
    }
    return render(request, 'seo_dashboard.html', context)

@seo_manager_required
def dashboard_logout(request):
    if 'seomanagerid' in request.session:
        del request.session['seomanagerid']
    logout(request)
    return redirect('account-login-page')




#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################



from django.shortcuts import render, redirect, get_object_or_404
from .forms import CategoryForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CategoryForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@seo_manager_required
def category_list(request):
    queryset = Category.objects.filter(deleted_at__isnull=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(slug__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')
    
    valid_sort_fields = ['name', 'created_at', 'style']
    if sort_by not in valid_sort_fields:
        sort_by = 'name'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        category_list = paginator.page(page)
    except PageNotAnInteger:
        category_list = paginator.page(1)
    except EmptyPage:
        category_list = paginator.page(paginator.num_pages)
    
    context = {
        'category_list': category_list,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_categories': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'seo_category_list.html', context)


@seo_manager_required

def category_details(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'seo_category_details.html', {'category': category})


@seo_manager_required

def category_edit(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':

        form = CategoryForm(request.POST, request.FILES, instance=category)
        try:
            if form.is_valid():

                updated_category = form.save()
                messages.success(request, f'Category "{updated_category.name}" updated successfully')
                return redirect('seo_dashboard-category_list')
            else:

                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:

        form = CategoryForm(instance=category)

    return render(request, 'seo_category_form.html', {
        'form': form, 
        'category': category,  
        'edit_mode': True  
    })


#################################################################################################
#################################################################################################
#################################################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from catalog.models import ProductImage,ProductDocument,ProductSpecification
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse



#####################################################################################################

@seo_manager_required

def product_list(request):
    queryset = Product.objects.filter(deleted_at__isnull=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(slug__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    

    category_filter = request.GET.get('category', '')
    if category_filter:
        queryset = queryset.filter(categories__id=category_filter)
    

    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'in_stock':
        queryset = queryset.filter(quantity_in_stock__gt=0)
    elif stock_filter == 'out_of_stock':
        queryset = queryset.filter(quantity_in_stock=0)
    
    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')

    valid_sort_fields = ['name', 'created_at', 'quantity_in_stock']
    if sort_by not in valid_sort_fields:
        sort_by = 'name'
    

    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)
    
    page = request.GET.get('page', 1)
    per_page = 100  
    paginator = Paginator(queryset, per_page)
    
    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        product_list = paginator.page(1)
    except EmptyPage:
        product_list = paginator.page(paginator.num_pages)
    
    categories = Category.objects.filter(deleted_at__isnull=True)
    
    context = {
        'product_list': product_list,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'sort_by': sort_by,
        'order': order,
        'total_products': queryset.count(),
        'per_page': per_page
    }

    print(context)
    
    return render(request, 'seo_product_list.html', context)



####################################################

@seo_manager_required

def product_details(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related('images'), pk=pk)
    return render(request, 'seo_product_details.html', {'product': product})







#####################################################################################################
########################################################################################################

from django.views.decorators.http import require_POST

@seo_manager_required

@require_POST
def delete_product_image(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk, deleted_at__isnull=True)
        
        # Delete the physical file
        if product.main_image:
            product.main_image.delete(save=False)
        
        # Clear the field
        product.main_image = None
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Image deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




########################################################################################################################
########################################################################################################################
########################################################################################################################
# 2025-01-02


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import ProductForm, ProductImageFormSet

@seo_manager_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # Initialize forms with POST data and files
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        
        # Print debug info
        if not image_formset.is_valid():
            print("Formset errors:", image_formset.errors)
            print("Management form data:", image_formset.management_form.data)
            
        if product_form.is_valid() and image_formset.is_valid():
            try:
                # Save the product first
                product = product_form.save()
                
                # Save only non-empty forms
                instances = image_formset.save(commit=False)
                for instance in instances:
                    # Only save if there's an image or if it's an existing record
                    if instance.pk or (hasattr(instance, 'product_image') and instance.product_image):
                        instance.product = product
                        instance.save()
                
                # Handle deletions
                for obj in image_formset.deleted_objects:
                    obj.delete()
                
                messages.success(request, 'Product updated successfully.')
                return redirect('seo_dashboard-products_list')
                
            except Exception as e:
                print(f"Error saving product: {str(e)}")
                messages.error(request, f'Error saving product: {str(e)}')
        else:
            # If validation fails, display error message
            messages.error(request, 'Please correct the errors below.')
            print("Product form errors:", product_form.errors)
            print("Image formset errors:", image_formset.errors)
    else:
        # GET request handling
        product_form = ProductForm(instance=product)
        image_formset = ProductImageFormSet(instance=product)
    
    context = {
        'product_form': product_form,
        'image_formset': image_formset,
        'product': product,
        'title': f'Edit Product: {product.name}'
    }
    
    return render(request, 'seo_product_edit_form.html', context)




#######################################################################################
#######################################################################################
#######################################################################################

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import OldUrlRedirect
from .forms import OldUrlRedirectForm

@seo_manager_required

def old_url_redirect_list(request):
    queryset = OldUrlRedirect.objects.all()

    print("#######################")
    print(queryset)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(old_slug__icontains=search_query) | 
            Q(new_slug__icontains=search_query) |
            Q(url_type__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'old_slug')
    order = request.GET.get('order', 'asc')
    
    valid_sort_fields = ['old_slug', 'new_slug', 'url_type']
    if sort_by not in valid_sort_fields:
        sort_by = 'old_slug'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        redirects = paginator.page(page)
    except PageNotAnInteger:
        redirects = paginator.page(1)
    except EmptyPage:
        redirects = paginator.page(paginator.num_pages)
    
    context = {
        'redirects': redirects,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_redirects': queryset.count(),
        'per_page': per_page
    }
    
    print('######################')
    print(context)
    
    return render(request, 'old_url_redirect_list.html', context)

@seo_manager_required
def old_url_redirect_details(request, pk):
    redirect_entry = get_object_or_404(OldUrlRedirect, pk=pk)
    return render(request, 'old_url_redirect_details.html', {'redirect_entry': redirect_entry})

@seo_manager_required
def old_url_redirect_create(request):
    if request.method == 'POST':
        form = OldUrlRedirectForm(request.POST)
        try:
            if form.is_valid():
                redirect_entry = form.save()
                messages.success(request, f'Redirect from "{redirect_entry.old_slug}" created successfully.')
                return redirect('seo_dashboard-old_url_redirect_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = OldUrlRedirectForm()
    
    return render(request, 'old_url_redirect_form.html', {
        'form': form,
        'edit_mode': False,
    })

################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OldUrlRedirect
from .forms import OldUrlRedirectForm
import logging

logger = logging.getLogger(__name__)

@seo_manager_required
def old_url_redirect_edit(request, pk):
    try:
        # Fetch the existing redirect entry
        redirect_entry = get_object_or_404(OldUrlRedirect, pk=pk)
        
        if request.method == 'POST':
            # Create form with POST data and existing instance
            form = OldUrlRedirectForm(request.POST, instance=redirect_entry)
            
            if form.is_valid():
                try:
                    # Save the updated redirect
                    updated_redirect = form.save()
                    messages.success(request, f'Redirect "{updated_redirect.old_slug}" updated successfully.')
                    return redirect('seo_dashboard-old_url_redirect_list')
                except Exception as save_error:
                    logger.error(f"Error saving redirect: {save_error}")
                    messages.error(request, f'Error saving redirect: {save_error}')
            else:
                # Log form validation errors
                logger.error(f"Form validation errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            # GET request - create form with existing instance
            form = OldUrlRedirectForm(instance=redirect_entry)
        
        # Render the edit form
        return render(request, 'old_url_redirect_form.html', {
            'form': form,
            'redirect_entry': redirect_entry,
            'edit_mode': True
        })
    
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in old_url_redirect_edit: {e}")
        messages.error(request, f'An unexpected error occurred: {e}')
        return redirect('seo_dashboard-old_url_redirect_list')

#################################################################################

@seo_manager_required
def old_url_redirect_delete(request, pk):
    redirect_entry = get_object_or_404(OldUrlRedirect, pk=pk)

    if request.method == 'POST':
        try:
            redirect_entry.delete()
            response_data = {
                'success': True, 
                'message': f'Redirect from "{redirect_entry.old_slug}" deleted successfully.',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('seo_dashboard-old_url_redirect_list')

        except Exception as e:
            response_data = {'success': False, 'error': str(e)}
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('seo_dashboard-old_url_redirect_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


############################################################################################
############################################################################################
############################################################################################

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from admin_dashboard.models import NewsArticle,BlogPost
from .forms import NewsArticleForm
from django.shortcuts import get_object_or_404

@seo_manager_required
def news_article_list(request):
    queryset = NewsArticle.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(short_description__icontains=search_query) |
            Q(full_content__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'date_published')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'category', 'date_published']
    if sort_by not in valid_sort_fields:
        sort_by = 'date_published'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        news_articles = paginator.page(page)
    except PageNotAnInteger:
        news_articles = paginator.page(1)
    except EmptyPage:
        news_articles = paginator.page(paginator.num_pages)
    
    context = {
        'news_articles': news_articles,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_articles': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'seo_news_article_list.html', context)

@seo_manager_required
def news_article_details(request, pk):
    news_article = get_object_or_404(NewsArticle, pk=pk)
    return render(request, 'seo_news_article_details.html', {'news_article': news_article })


@seo_manager_required
def news_article_edit(request, pk):
    news_article = get_object_or_404(NewsArticle, pk=pk)
    
    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES, instance=news_article)
        try:
            if form.is_valid():
                updated_article = form.save()
                messages.success(request, f'News article "{updated_article.title}" updated successfully')
                return redirect('seo_dashboard-news_article_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = NewsArticleForm(instance=news_article)
    
    return render(request, 'seo_news_article_form.html', {
        'form': form,
        'news_article': news_article,
        'edit_mode': True
    })


############################################################################################
############################################################################################
############################################################################################

from .forms import BlogPostForm

@seo_manager_required
def blog_post_list(request):
    queryset = BlogPost.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(short_description__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'date_published')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'category', 'date_published']
    if sort_by not in valid_sort_fields:
        sort_by = 'date_published'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        blog_posts = paginator.page(page)
    except PageNotAnInteger:
        blog_posts = paginator.page(1)
    except EmptyPage:
        blog_posts = paginator.page(paginator.num_pages)
    
    context = {
        'blog_posts': blog_posts,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_posts': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'seo_blog_post_list.html', context)

@seo_manager_required
def blog_post_details(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'seo_blog_post_details.html', {'blog_post': blog_post })

@seo_manager_required
def blog_post_edit(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog_post)
        try:
            if form.is_valid():
                updated_post = form.save()
                messages.success(request, f'Blog post "{updated_post.title}" updated successfully')
                return redirect('seo_dashboard-blog_post_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = BlogPostForm(instance=blog_post)

    return render(request, 'seo_blog_post_form.html', {
        'form': form,
        'blog_post': blog_post,
        'edit_mode': True
    })


##################################################################################
##################################################################################
##################################################################################

from admin_dashboard.models import Project
from .forms import ProjectForm

@seo_manager_required
def project_list(request):
    queryset = Project.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(short_description__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'category', 'status', 'created_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    queryset = queryset.order_by(f'-{sort_by}' if order == 'desc' else sort_by)
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)
    
    context = {
        'projects': projects,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_projects': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'seo_project_list.html', context)

@seo_manager_required
def project_details(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'seo_project_details.html', {'project': project})

@seo_manager_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        try:
            if form.is_valid():
                updated_project = form.save()
                messages.success(request, f'Project "{updated_project.title}" updated successfully.')
                return redirect('seo_dashboard-project_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'seo_project_form.html', {
        'form': form,
        'project': project,
        'edit_mode': True,
    })














