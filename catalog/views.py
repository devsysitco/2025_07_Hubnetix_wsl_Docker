# Create your views here.
###################################################################
# 2024-12-16

from django.shortcuts import render, redirect, get_object_or_404
from .models import Category,Product
from .forms import CategoryForm,ProductForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category
from .forms import CategoryForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from admin_dashboard.views import admin_required


@admin_required
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
    
    return render(request, 'category_list.html', context)

@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                category = form.save()
                messages.success(request, f'Category {category.name} created successfully')
                return redirect('admin_dashboard-category_list')
            else:

                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = CategoryForm()
    
    return render(request, 'category_form.html', {
        'form': form,
        'edit_mode': False
    })

@admin_required
def category_details(request, pk):

    category = get_object_or_404(Category, pk=pk)


    return render(request, 'category_details.html', {'category': category})



@admin_required
def category_edit(request, pk):

    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':

        form = CategoryForm(request.POST, request.FILES, instance=category)
        try:
            if form.is_valid():

                updated_category = form.save()
                messages.success(request, f'Category "{updated_category.name}" updated successfully')
                return redirect('admin_dashboard-category_list')
            else:

                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:

        form = CategoryForm(instance=category)

    return render(request, 'category_form.html', {
        'form': form, 
        'category': category,  
        'edit_mode': True  
    })




@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        try:

            category.deleted_at = timezone.now()
            category.is_active = False
            category.save()


            response_data = {
                'success': True, 
                'message': f'Category "{category.name}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-category_list')

        except Exception as e:

            response_data = {
                'success': False, 
                'error': str(e)
            }


            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)
            

            messages.error(request, str(e))
            return redirect('admin_dashboard-category_list')


    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


#################################################################################################
#################################################################################################
#################################################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductForm
from .models import ProductImage,ProductDocument,ProductSpecification
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse

@admin_required
def product_create(request):
    """
    View for creating a new product
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        try:
            with transaction.atomic():
                if form.is_valid():
                    # Save the product and related data
                    product = form.save()
                    
                    messages.success(
                        request,
                        f"Product '{product.name}' created successfully!"
                    )
                    return redirect('admin_dashboard-products_list')
                else:
                    # Handle form errors
                    for field, field_errors in form.errors.items():
                        for error in field_errors:
                            # Get the field label or use the field name if no label
                            field_label = form.fields[field].label or field
                            messages.error(request, f"{field_label}: {error}")
                            
        except Exception as e:
            # Handle unexpected errors
            messages.error(
                request,
                f"An unexpected error occurred while creating the product: {str(e)}"
            )
            
    else:
        # GET request - display empty form
        form = ProductForm()

    # Render the form template
    return render(request, 'product_form.html', {
        'form': form,
        'edit_mode': False,
        'page_title': 'Add Product',
        'submit_button_text': 'Create Product'
    })

#####################################################################################################


@admin_required
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
    
    return render(request, 'product_list.html', context)


@admin_required
def product_details(request, pk):
    product = get_object_or_404(Product.objects.select_related(
        ).prefetch_related(
            'categories',
            'images',
            'specifications',
            'documents'
        ), pk=pk)

    documents_by_type = {}
    for doc in product.documents.all():
        if doc.document_type not in documents_by_type:
            documents_by_type[doc.document_type] = []
        documents_by_type[doc.document_type].append(doc)

    context = {
        'product': product,
        'documents_by_type': documents_by_type
    }
    
    return render(request, 'product_details.html', context)

# def download_document(request, doc_id):
#     document = get_object_or_404(ProductDocument, pk=doc_id)
#     response = FileResponse(document.document)
#     response['Content-Disposition'] = f'attachment; filename="{document.document.name}"'
#     return response

def download_document(request, doc_id):
    document = get_object_or_404(ProductDocument, pk=doc_id)
    response = FileResponse(document.document, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{document.document.name}"'
    return response

from django.http import FileResponse, HttpResponse


def view_document(request, doc_id):
    print("#################################")
    document = get_object_or_404(ProductDocument, pk=doc_id)
    print(doc_id)
    print(document)
    
    try:
        response = FileResponse(document.document.open('rb'))
        response['Content-Disposition'] = f'inline; filename="{document.document.name}"'
        return response
    except Exception as e:
        return HttpResponse(f"Error accessing the document: {str(e)}", status=500)





#####################################################################################################
########################################################################################################

from django.views.decorators.http import require_POST

@admin_required
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
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone

@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            # Mark the product as deleted without actually removing it from the database
            product.deleted_at = timezone.now()
            product.save()

            response_data = {
                'success': True, 
                'message': f'Product "{product.name}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-products_list')

        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-products_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

########################################################################################################################
########################################################################################################################
########################################################################################################################
# 2025-01-02

from django.http import Http404
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EditProductForm

def handle_images(request, product):
    """
    Handle product image uploads and deletions
    """
    # Delete selected images
    image_ids_to_remove = request.POST.getlist('images_to_remove', [])
    ProductImage.objects.filter(id__in=image_ids_to_remove, product=product).delete()

    # Add new images
    for img in request.FILES.getlist('additional_images'):
        ProductImage.objects.create(product=product, product_image=img)

def handle_documents(request, product):
    """
    Handle product document uploads and deletions
    """
    # Delete selected documents
    doc_ids_to_remove = request.POST.getlist('documents_to_remove', [])
    ProductDocument.objects.filter(id__in=doc_ids_to_remove, product=product).delete()

    # Add new documents
    for doc in request.FILES.getlist('additional_documents'):
        ProductDocument.objects.create(
            product=product,
            title=doc.name.split('.')[0],
            document=doc
        )

def get_product_details(product_id):
    """
    Get all details related to a product including specifications, images, and documents
    """
    try:
        product = Product.objects.get(id=product_id)
        specifications = list(product.specifications.values(
            'specification_title',
            'specification'
        ))
        
        # Convert specifications to list format
        spec_list = [
            {
                'title': spec['specification_title'],
                'value': spec['specification']
            } for spec in specifications
        ]
        
        images = product.images.all()
        documents = product.documents.all()
        
        return {
            "product": product,
            "specifications": spec_list,
            "images": images,
            "documents": documents
        }
    except Product.DoesNotExist:
        raise Http404("Product not found")

def process_specifications(post_data):
    """
    Process specifications from POST data and return as list
    Handles multiple specifications with same title
    """
    specifications = []
    i = 0
    
    while True:
        title_key = f'specification_title_{i}'
        value_key = f'specification_{i}'
        
        # Break if no more specifications found
        if title_key not in post_data or value_key not in post_data:
            break
            
        title = post_data.get(title_key)
        value = post_data.get(value_key)
        
        # Only add if both title and value are present
        if title and value:
            specifications.append({
                'title': title,
                'value': value
            })
            
        i += 1
    
    return specifications

@transaction.atomic
def process_edit_form(request, product_id):
    """
    Process the edit form submission with transaction atomic
    """
    try:
        product = Product.objects.get(id=product_id)
        form = EditProductForm(request.POST, request.FILES, instance=product)
        print("###############")

        if form.is_valid():
            
            # Save the main product data
            product = form.save()
            
            # Process specifications
            specifications = process_specifications(request.POST)
            print("Processed specifications:", specifications)  # Debug log
            
            # Delete existing specifications
            product.specifications.all().delete()

            # Create new specifications
            for spec in specifications:
                ProductSpecification.objects.create(
                    product=product,
                    specification_title=spec['title'],
                    specification=spec['value']
                )
            
            # Handle media files
            handle_images(request, product)
            handle_documents(request, product)

            return {"success": True, "message": "Product updated successfully."}
        else:
            
            return {"success": False, "errors": form.errors}
            
    except Product.DoesNotExist:
        return {"success": False, "errors": "Product not found"}
    except Exception as e:
        return {"success": False, "errors": str(e)}


@admin_required
def product_edit(request, pk):
   
    if request.method == 'POST':
        result = process_edit_form(request, pk)

        print(f"Edit form process result: {result}")
        
        if result["success"]:
            messages.success(request, result["message"])
            
            # Make sure we have a valid pk before redirecting
            if pk:
                return redirect('admin_dashboard-product_details', pk=pk)
            else:
                return redirect('admin_dashboard-products')  # Fallback to products list
        else:
            product_details = get_product_details(pk)
            form = EditProductForm(instance=product_details["product"])
            
            # Extract errors from the result dictionary
            errors = result.get("errors", {})
            
            # Convert the errors dictionary into a user-friendly format
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")

            context = {
                'form': form,
                'product': product_details["product"],
                'is_edit': True,
                'errors': errors,
                'existing_images': product_details["images"],
                'existing_documents': product_details["documents"],
                'specifications_json': product_details["specifications"],
            }
            
            return render(request, 'product_edit_form.html', context)

    else:
        # GET request - show edit form
        product_details = get_product_details(pk)
        form = EditProductForm(instance=product_details["product"])
        context = {
            'form': form,
            'product': product_details["product"],
            'is_edit': True,
            'existing_images': product_details["images"],
            'existing_documents': product_details["documents"],
            'specifications_json': product_details["specifications"],
        }
    
    return render(request, 'product_edit_form.html', context)


###########################################################################

from django.http import JsonResponse
from .models import Product

def check_product_name(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        product_id = request.POST.get('product_id')  # For edit mode
        
        # Build query to check for duplicate names
        query = Product.objects.filter(name__iexact=name, deleted_at__isnull=True)
        
        # If editing, exclude the current product
        if product_id:
            query = query.exclude(id=product_id)
            
        exists = query.exists()
        
        return JsonResponse({
            'exists': exists,
            'message': 'Product with this Name already exists.' if exists else ''
        })



###################################################################
###################################################################
###################################################################


from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Datasheet
from .forms import DatasheetForm

@admin_required
def datasheet_list(request):
    queryset = Datasheet.objects.filter(deleted_at__isnull=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['name', 'product', 'created_at']
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
        datasheets = paginator.page(page)
    except PageNotAnInteger:
        datasheets = paginator.page(1)
    except EmptyPage:
        datasheets = paginator.page(paginator.num_pages)
    
    context = {
        'datasheets': datasheets,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'total_datasheets': queryset.count(),
        'per_page': per_page
    }
    
    return render(request, 'datasheet_list.html', context)

@admin_required
def datasheet_create(request):
    if request.method == 'POST':
        form = DatasheetForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                datasheet = form.save()
                messages.success(request, f'Datasheet "{datasheet.name}" created successfully.')
                return redirect('admin_dashboard-datasheet_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = DatasheetForm()
    
    return render(request, 'datasheet_form.html', {
        'form': form,
        'edit_mode': False,
    })

@admin_required
def datasheet_edit(request, pk):
    datasheet = get_object_or_404(Datasheet, pk=pk)

    if request.method == 'POST':
        form = DatasheetForm(request.POST, request.FILES, instance=datasheet)
        try:
            if form.is_valid():
                updated_datasheet = form.save()
                messages.success(request, f'Datasheet "{updated_datasheet.name}" updated successfully')
                return redirect('admin_dashboard-datasheet_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = DatasheetForm(instance=datasheet)

    return render(request, 'datasheet_form.html', {
        'form': form,
        'datasheet': datasheet,
        'edit_mode': True
    })

@admin_required
def datasheet_details(request, pk):
    datasheet = get_object_or_404(Datasheet, pk=pk)
    return render(request, 'datasheet_details.html', {'datasheet': datasheet})

@admin_required
def datasheet_delete(request, pk):
    datasheet = get_object_or_404(Datasheet, pk=pk)

    if request.method == 'POST':
        try:
            # Soft delete logic
            datasheet.deleted_at = timezone.now()
            datasheet.save()

            response_data = {
                'success': True, 
                'message': f'Datasheet "{datasheet.name}" deleted successfully',
                'id': pk
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)

            messages.success(request, response_data['message'])
            return redirect('admin_dashboard-datasheet_list')

        except Exception as e:
            response_data = {
                'success': False, 
                'error': str(e)
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data, status=400)

            messages.error(request, str(e))
            return redirect('admin_dashboard-datasheet_list')

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)






