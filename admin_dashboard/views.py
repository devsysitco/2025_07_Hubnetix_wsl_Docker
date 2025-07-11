from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from catalog.models import Product,Category
from .models import NewsArticle,BlogPost,JobListing
from functools import wraps
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model() 

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'adminid' in request.session:
            try:
                user = User.objects.get(id=request.session['adminid'])
                if user.account_type and user.account_type.id == 1:
                    # Update last activity timestamp
                    request.session['last_activity'] = now().timestamp()
                    # Temporarily login this user for the duration of this request
                    auth_login(request, user)
                    return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                pass
        return redirect('account-login-page')
    return wrapper




@admin_required
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
    return render(request, 'admin_dashboard.html', context)

@admin_required
def dashboard_logout(request):
	logout(request)
	request.session.clear()
	return redirect('account-login-page')

###########################################################################################################
###########################################################################################################

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import NewsArticle
from .forms import NewsArticleForm
from django.shortcuts import get_object_or_404

@admin_required
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
    
    return render(request, 'news_article_list.html', context)

@admin_required
def news_article_details(request, pk):
    news_article = get_object_or_404(NewsArticle, pk=pk)
    return render(request, 'news_article_details.html', {'news_article': news_article })

@admin_required
def news_article_create(request):
    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                news_article = form.save()
                messages.success(request, f'News Article "{news_article.title}" created successfully.')
                return redirect('admin_dashboard-news_article_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = NewsArticleForm()
    
    return render(request, 'news_article_form.html', {
        'form': form,
        'edit_mode': False,
    })

@admin_required
def news_article_edit(request, pk):
    news_article = get_object_or_404(NewsArticle, pk=pk)
    
    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES, instance=news_article)
        try:
            if form.is_valid():
                updated_article = form.save()
                messages.success(request, f'News article "{updated_article.title}" updated successfully')
                return redirect('admin_dashboard-news_article_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = NewsArticleForm(instance=news_article)
    
    return render(request, 'news_article_form.html', {
        'form': form,
        'news_article': news_article,
        'edit_mode': True
    })


from django.utils import timezone
from django.http import JsonResponse

@admin_required
def news_article_delete(request, pk):
    news_article = get_object_or_404(NewsArticle, pk=pk)

    if request.method == 'POST':
        try:
            # Soft delete logic
            news_article.deleted_at = timezone.now()
            news_article.is_active = False
            news_article.save()

            response_data = {
                'success': True, 
                'message': f'News article "{news_article.title}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-news_article_list')

        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-news_article_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)







###########################################################################################################
###########################################################################################################

from .models import BlogPost
from .forms import BlogPostForm

@admin_required
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
    
    return render(request, 'blog_post_list.html', context)


@admin_required
def blog_post_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                blog_post = form.save()
                messages.success(request, f'Blog Post "{blog_post.title}" created successfully.')
                return redirect('admin_dashboard-blog_post_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = BlogPostForm()
    
    return render(request, 'blog_post_form.html', {
        'form': form,
        'edit_mode': False,
    })





@admin_required
def blog_post_edit(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog_post)
        try:
            if form.is_valid():
                updated_post = form.save()
                messages.success(request, f'Blog post "{updated_post.title}" updated successfully')
                return redirect('admin_dashboard-blog_post_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = BlogPostForm(instance=blog_post)

    return render(request, 'blog_post_form.html', {
        'form': form,
        'blog_post': blog_post,
        'edit_mode': True
    })

@admin_required
def blog_post_details(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog_post_details.html', {'blog_post': blog_post })


@admin_required
def blog_post_delete(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        try:
            # Soft delete logic
            blog_post.deleted_at = timezone.now()
            blog_post.is_active = False
            blog_post.save()

            response_data = {
                'success': True, 
                'message': f'Blog post "{blog_post.title}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-blog_post_list')

        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-blog_post_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


###########################################################################################################
###########################################################################################################



from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import JobListing
from .forms import JobListingForm

@admin_required
def job_listing_list(request):
    queryset = JobListing.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(job_title__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(job_location__icontains=search_query) |
            Q(job_description__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'date_posted')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['job_title', 'department', 'job_location', 'date_posted']
    if sort_by not in valid_sort_fields:
        sort_by = 'date_posted'
    
    if order == 'desc':
        queryset = queryset.order_by(f'-{sort_by}')
    else:
        queryset = queryset.order_by(sort_by)

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        job_listings = paginator.page(page)
    except PageNotAnInteger:
        job_listings = paginator.page(1)
    except EmptyPage:
        job_listings = paginator.page(paginator.num_pages)
    
    context = {
        'job_listings': job_listings,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_listings': queryset.count(),
        'per_page': per_page,
    }
    
    return render(request, 'job_listing_list.html', context)

@admin_required
def job_listing_details(request, pk):
    job_listing = get_object_or_404(JobListing, pk=pk)
    return render(request, 'job_listing_details.html', {'job_listing': job_listing})


@admin_required
def job_listing_create(request):
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            job_listing = form.save()
            messages.success(request, f'Job listing "{job_listing.job_title}" created successfully.')
            return redirect('admin_dashboard-job_listing_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = JobListingForm()
    
    return render(request, 'job_listing_form.html', {'form': form, 'edit_mode': False})

@admin_required
def job_listing_edit(request, pk):
    job_listing = get_object_or_404(JobListing, pk=pk)
    
    if request.method == 'POST':
        form = JobListingForm(request.POST, instance=job_listing)
        if form.is_valid():
            updated_listing = form.save()
            messages.success(request, f'Job listing "{updated_listing.job_title}" updated successfully.')
            return redirect('admin_dashboard-job_listing_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = JobListingForm(instance=job_listing)
    
    return render(request, 'job_listing_form.html', {'form': form, 'job_listing': job_listing, 'edit_mode': True})


@admin_required
def job_listing_delete(request, pk):
    job_listing = get_object_or_404(JobListing, pk=pk)
    
    if request.method == 'POST':
        try:
            job_listing.deleted_at = timezone.now()
            job_listing.active = False
            job_listing.save()
            response_data = {
                'success': True,
                'message': f'Job listing "{job_listing.job_title}" deleted successfully.',
                'id': pk
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-job_listing_list')
        except Exception as e:
            response_data = {'success': False, 'error': str(e)}
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('admin_dashboard-job_listing_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


#############################################################################################
#############################################################################################


from .models import Project
from .forms import ProjectForm

@admin_required
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
    
    return render(request, 'project_list.html', context)

@admin_required
def project_details(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project_details.html', {'project': project})

@admin_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                project = form.save()
                messages.success(request, f'Project "{project.title}" created successfully.')
                return redirect('admin_dashboard-project_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = ProjectForm()
    
    return render(request, 'project_form.html', {
        'form': form,
        'edit_mode': False,
    })



@admin_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        try:
            if form.is_valid():
                updated_project = form.save()
                messages.success(request, f'Project "{updated_project.title}" updated successfully.')
                return redirect('admin_dashboard-project_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'project_form.html', {
        'form': form,
        'project': project,
        'edit_mode': True,
    })

@admin_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        try:
            # Soft delete logic
            project.deleted_at = timezone.now()
            project.is_active = False
            project.save()
            
            response_data = {
                'success': True, 
                'message': f'Project "{project.title}" deleted successfully.',
                'id': pk
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-project_list')
        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('admin_dashboard-project_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


######################################################################################


from .models import JobApplication, ContactSubmission, NewsletterSubscription

# Job Application Views
@admin_required
def job_application_list(request):
    queryset = JobApplication.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['full_name', 'email', 'position', 'created_at', 'updated_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    queryset = queryset.order_by(f'-{sort_by}' if order == 'desc' else sort_by)
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        applications = paginator.page(page)
    except PageNotAnInteger:
        applications = paginator.page(1)
    except EmptyPage:
        applications = paginator.page(paginator.num_pages)
    
    context = {
        'applications': applications,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_applications': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'job_application_list.html', context)

@admin_required
def job_application_details(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, deleted_at__isnull=True)
    return render(request, 'job_application_details.html', {'application': application})

@admin_required
def job_application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, deleted_at__isnull=True)
    
    if request.method == 'POST':
        try:
            # Soft delete
            application.deleted_at = timezone.now()
            application.save()
            
            response_data = {
                'success': True,
                'message': f'Application from "{application.full_name}" deleted successfully.',
                'id': pk
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-job_application_list')
        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('admin_dashboard-job_application_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


###################################################################################################


# Contact Submission Views
@admin_required
def contact_submission_list(request):
    queryset = ContactSubmission.objects.filter(deleted_at__isnull=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['full_name', 'email', 'created_at', 'updated_at']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    queryset = queryset.order_by(f'-{sort_by}' if order == 'desc' else sort_by)
    
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        submissions = paginator.page(1)
    except EmptyPage:
        submissions = paginator.page(paginator.num_pages)
    
    context = {
        'submissions': submissions,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_submissions': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'contact_submission_list.html', context)

@admin_required
def contact_submission_details(request, pk):
    submission = get_object_or_404(ContactSubmission, pk=pk, deleted_at__isnull=True)
    return render(request, 'contact_submission_details.html', {'submission': submission})

@admin_required
def contact_submission_delete(request, pk):
    submission = get_object_or_404(ContactSubmission, pk=pk, deleted_at__isnull=True)
    
    if request.method == 'POST':
        try:
            # Soft delete
            submission.deleted_at = timezone.now()
            submission.save()
            
            response_data = {
                'success': True,
                'message': f'Contact submission from "{submission.full_name}" deleted successfully.',
                'id': pk
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-contact_submission_list')
        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('admin_dashboard-contact_submission_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

###################################################################################################

# Newsletter Subscription Views
@admin_required
def newsletter_subscription_list(request):
    queryset = NewsletterSubscription.objects.filter(deleted_at__isnull=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(email__icontains=search_query)
    
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['email', 'subscribed_at', 'created_at', 'updated_at', 'is_active']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    queryset = queryset.order_by(f'-{sort_by}' if order == 'desc' else sort_by)
    
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        subscriptions = paginator.page(page)
    except PageNotAnInteger:
        subscriptions = paginator.page(1)
    except EmptyPage:
        subscriptions = paginator.page(paginator.num_pages)
    
    context = {
        'subscriptions': subscriptions,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_subscriptions': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'newsletter_subscription_list.html', context)

@admin_required
def newsletter_subscription_delete(request, pk):
    subscription = get_object_or_404(NewsletterSubscription, pk=pk, deleted_at__isnull=True)
    
    if request.method == 'POST':
        try:
            # Soft delete
            subscription.deleted_at = timezone.now()
            subscription.is_active = False  # Additional state change for NewsletterSubscription
            subscription.save()
            
            response_data = {
                'success': True,
                'message': f'Newsletter subscription "{subscription.email}" deleted successfully.',
                'id': pk
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-newsletter_subscription_list')
        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            
            messages.error(request, str(e))
            return redirect('admin_dashboard-newsletter_subscription_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@admin_required
def newsletter_subscription_toggle_status(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        subscription_id = request.POST.get('subscription_id')
        
        try:
            subscription = get_object_or_404(NewsletterSubscription, pk=subscription_id, deleted_at__isnull=True)
            
            # Toggle the status
            subscription.is_active = not subscription.is_active
            subscription.save()
            
            response_data = {
                'success': True,
                'message': f'Subscription for "{subscription.email}" has been {"enabled" if subscription.is_active else "disabled"}.',
                'is_active': subscription.is_active
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


#######################################################################################
#######################################################################################

from django.utils.text import slugify

@admin_required
def fill_all_missing_fields(request, model, model_name):
    
    # Get all instances from the database
    instances = model.objects.all()
    count = 0
    
    for instance in instances:
        updated = False
        
        # Generate slug from title if not provided
        if not instance.slug:
            base_slug = slugify(instance.title)
            instance.slug = base_slug
            updated = True
            
            # Handle duplicate slugs
            original_slug = instance.slug
            counter = 1
            
            while model.objects.filter(slug=instance.slug).exclude(id=instance.id).exists():
                instance.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Set default SEO fields if not provided
        if not instance.meta_tags:
            instance.meta_tags = instance.title
            updated = True
        
        if not instance.meta_description:
            instance.meta_description = instance.short_description or instance.title
            updated = True
        
        # Only save if we made changes
        if updated:
            # Use save method directly on the model to avoid infinite recursion
            super(model, instance).save()
            count += 1


@admin_required
def fill_all_models_fields(request):
    models = [
        (BlogPost, "blog posts"),
        (Project, "projects"),
        (NewsArticle, "news articles"),
    ]

    for model, model_name in models:
        fill_all_missing_fields(request, model, model_name)

    messages.success(request, "Updated all blog posts, projects, and news articles with missing fields.")
    return redirect('admin_dashboard-dashboard')  # Update with your actual URL name



################################################################################################
################################################################################################

from user_account.models import Partner
from .forms import PartnerForm


def partner_list(request):
    queryset = Partner.objects.filter(is_active = True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(email__icontains=search_query) |
            Q(partner_company_name__icontains=search_query) |
            Q(business_type__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', '-date_joined')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['email', 'partner_company_name', 'partnership_level', 'date_joined']
    if sort_by.replace('-', '') not in valid_sort_fields:
        sort_by = '-date_joined'
    
    queryset = queryset.order_by(sort_by)
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = 100
    paginator = Paginator(queryset, per_page)
    
    try:
        partners = paginator.page(page)
    except PageNotAnInteger:
        partners = paginator.page(1)
    except EmptyPage:
        partners = paginator.page(paginator.num_pages)
    
    context = {
        'partners': partners,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_partners': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'partner_list.html', context)

@login_required
def partner_details(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    return render(request, 'partner_details.html', {'partner': partner})

@login_required
def partner_create(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        try:
            if form.is_valid():
                partner = Partner.objects.create_user(
                    email=form.cleaned_data['email'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    partner_company_name=form.cleaned_data['partner_company_name'],
                    business_type=form.cleaned_data['business_type'],
                    partnership_level=form.cleaned_data['partnership_level']
                )
                messages.success(request, f'Partner "{partner.partner_company_name}" created successfully.')
                return redirect('admin_dashboard-partner_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = PartnerForm()
    
    return render(request, 'partner_form.html', {
        'form': form,
        'edit_mode': False,
    })


def partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    
    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)
        try:
            if form.is_valid():
                updated_partner = form.save()
                messages.success(request, f'Partner "{updated_partner.partner_company_name}" updated successfully')
                return redirect('admin_dashboard-partner_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = PartnerForm(instance=partner)
        form.fields['password'].initial = ''
    
    return render(request, 'partner_form.html', {
        'form': form,
        'partner': partner,
        'edit_mode': True
    })

@login_required
def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == 'POST':
        try:
            partner.is_active = False
            partner.save()

            response_data = {
                'success': True,
                'message': f'Partner "{partner.partner_company_name}" deactivated successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-partner_list')

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-partner_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)




###################################################################################################

import os
from .models import Resource
from .forms import ResourceForm
from django.http import FileResponse, Http404

@admin_required
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
    
    return render(request, 'resource_list.html', context)

@admin_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                resource = form.save()
                messages.success(request, f'Resource "{resource.title}" created successfully.')
                return redirect('admin_dashboard-resource_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = ResourceForm()
    
    return render(request, 'resource_form.html', {
        'form': form,
        'edit_mode': False,
    })

@admin_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk)

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        try:
            if form.is_valid():
                updated_resource = form.save()
                messages.success(request, f'Resource "{updated_resource.title}" updated successfully')
                return redirect('admin_dashboard-resource_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = ResourceForm(instance=resource)

    return render(request, 'resource_form.html', {
        'form': form,
        'resource': resource,
        'edit_mode': True
    })

@admin_required
def resource_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'resource_details.html', {'resource': resource})


@admin_required
def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    try:
        response = FileResponse(resource.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(resource.file.name)}"'
        return response
    except FileNotFoundError:
        raise Http404("File not found")

@admin_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)

    if request.method == 'POST':
        try:
            # Handle file deletion
            if resource.file:
                if os.path.isfile(resource.file.path):
                    os.remove(resource.file.path)
            
            # Soft delete logic
            resource.deleted_at = timezone.now()
            resource.save()

            response_data = {
                'success': True, 
                'message': f'Resource "{resource.title}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-resource_list')

        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-resource_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


################################################################################################
################################################################################################
################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Banner, OfficeLocation
from .forms import BannerForm, OfficeLocationForm

# Banner Views
@admin_required
def banner_list(request):
    queryset = Banner.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(banner_type__icontains=search_query) |
            Q(alt_text__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'banner_type', 'order', 'created_at']
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
        banners = paginator.page(page)
    except PageNotAnInteger:
        banners = paginator.page(1)
    except EmptyPage:
        banners = paginator.page(paginator.num_pages)
    
    context = {
        'banners': banners,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_banners': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'banner_list.html', context)

@admin_required
def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                banner = form.save()
                messages.success(request, f'Banner "{banner.title}" created successfully.')
                return redirect('admin_dashboard-banner_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = BannerForm()
    
    return render(request, 'banner_form.html', {
        'form': form,
        'edit_mode': False,
    })

@admin_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        try:
            if form.is_valid():
                updated_banner = form.save()
                messages.success(request, f'Banner "{updated_banner.title}" updated successfully')
                return redirect('admin_dashboard-banner_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = BannerForm(instance=banner)

    return render(request, 'banner_form.html', {
        'form': form,
        'banner': banner,
        'edit_mode': True
    })

@admin_required
def banner_details(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    return render(request, 'banner_details.html', {'banner': banner})

@admin_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)

    if request.method == 'POST':
        try:
            banner.soft_delete()
            response_data = {
                'success': True,
                'message': f'Banner "{banner.title}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-banner_list')

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-banner_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


#########################################################################################


# # Office Location Views
@admin_required
def office_location_list(request):
    queryset = OfficeLocation.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(office_country__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['title', 'office_country', 'created_at']
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
        office_locations = paginator.page(page)
    except PageNotAnInteger:
        office_locations = paginator.page(1)
    except EmptyPage:
        office_locations = paginator.page(paginator.num_pages)
    
    context = {
        'office_locations': office_locations,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_locations': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'office_location_list.html', context)

@admin_required
def office_location_create(request):
    if request.method == 'POST':
        form = OfficeLocationForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                office = form.save()
                messages.success(request, f'Office Location "{office.title}" created successfully.')
                return redirect('admin_dashboard-office_location_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = OfficeLocationForm()
    
    return render(request, 'office_location_form.html', {
        'form': form,
        'edit_mode': False,
    })

@admin_required
def office_location_edit(request, pk):
    office = get_object_or_404(OfficeLocation, pk=pk)

    if request.method == 'POST':
        form = OfficeLocationForm(request.POST, request.FILES, instance=office)
        try:
            if form.is_valid():
                updated_office = form.save()
                messages.success(request, f'Office Location "{updated_office.title}" updated successfully')
                return redirect('admin_dashboard-office_location_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = OfficeLocationForm(instance=office)

    return render(request, 'office_location_form.html', {
        'form': form,
        'office': office,
        'edit_mode': True
    })

@admin_required
def office_location_details(request, pk):
    office = get_object_or_404(OfficeLocation, pk=pk)
    return render(request, 'office_location_details.html', {'office': office})

@admin_required
def office_location_delete(request, pk):
    office = get_object_or_404(OfficeLocation, pk=pk)

    if request.method == 'POST':
        try:
            office.soft_delete()
            response_data = {
                'success': True,
                'message': f'Office Location "{office.title}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-office_location_list')

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-office_location_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)