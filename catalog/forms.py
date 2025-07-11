from django import forms
from .models import Category
from django.core.exceptions import ValidationError
from django.db.models import Count
#from django_summernote.fields import SummernoteWidget


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name', 'style', 'short_description', 'detailed_description', 
            'icon', 'banner', 'side_image', 'parent', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'style': forms.Select(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short description'}),
            #'detailed_description': SummernoteWidget(attrs={'class': 'form-control', 'placeholder': 'Enter detailed description'}),
            #'detailed_description': SummernoteWidget(),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter detailed description'}),
            'icon': forms.FileInput(attrs={'class': 'form-control'}), 
            'banner': forms.FileInput(attrs={'class': 'form-control'}), 
            'side_image': forms.FileInput(attrs={'class': 'form-control'}),  
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'name': 'Category Name',
            'style': 'Display Style',
            'short_description': 'Short Description',
            'detailed_description': 'Detailed Description',
            'icon': 'Icon',
            'banner': 'Banner',
            'side_image': 'Side Image',
            'parent': 'Parent Category',
            'is_active': 'Active'
        }
        help_texts = {
            'name': 'Display name for the category',
            'style': 'Visual display style for the category',
            'short_description': 'Brief summary for search results or listings',
            'detailed_description': 'Comprehensive description for SEO and context',
            'icon': 'Icon representing the category',
            'banner': 'Large banner image at the top of the category page',
            'side_image': 'Side image for promoting sub-categories',
            'parent': 'Parent category for multi-level hierarchy',
            'is_active': 'Indicates if the category is currently active'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].required = True
        self.fields['icon'].required = True
        self.fields['short_description'].required = True
        
        # Set form input classes and handle errors
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control is-invalid'})
        
        # Get categories without products
        categories_without_products = Category.objects.annotate(
            product_count=Count('products')
        ).filter(product_count=0, deleted_at__isnull=True)
        
        # If editing an existing category
        if self.instance.pk:
            # Avoid circular references by excluding self and potential children
            # Manual way to prevent circular references without using tree methods
            def get_all_children_ids(category_id, all_categories):
                """Recursively get all children IDs"""
                children_ids = [c.pk for c in all_categories if c.parent_id == category_id]
                result = children_ids.copy()
                for child_id in children_ids:
                    result.extend(get_all_children_ids(child_id, all_categories))
                return result
            
            # Get all categories for our recursive function
            all_categories = Category.objects.filter(deleted_at__isnull=True)
            
            # Get all descendant IDs including self
            descendant_ids = [self.instance.pk] + get_all_children_ids(self.instance.pk, all_categories)
            
            # Exclude self and all descendants
            categories_without_products = categories_without_products.exclude(
                pk__in=descendant_ids
            )
        
        self.fields['parent'].queryset = categories_without_products

    

#######################################################################################################
# 2024-12-18

from django import forms
from .models import Product, Category, ProductImage, ProductDocument
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, ProductImage, ProductDocument, ProductSpecification
import json
from django.db.models import Q


class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.filter(deleted_at__isnull=True).filter(
            ~Q(id__in=Category.objects.filter(parent__isnull=False).values_list('parent', flat=True))
        ),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'multiple': 'multiple'
        }),
        required=True,
        help_text='Select one or more categories for this product'
    )

    additional_images = forms.FileField(
        required=False,
        label='Additional Images',
        help_text='Select multiple images for the product gallery'
    )

    additional_documents = forms.FileField(
        required=False,
        label='Additional Documents',
        help_text='Select multiple documents for the product'
    )

    specifications = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = [
            'name',
            'short_description',
            'detailed_description',
            'main_image',
            'measurement',  # Add new measurement field
            'quantity_in_stock',
            'categories',
            'is_latest',
            'is_featured',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter product name'}),
            'short_description': forms.TextInput(attrs={'placeholder': 'Enter short description'}),
            'detailed_description': forms.Textarea(attrs={'placeholder': 'Enter detailed description'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'measurement': forms.Select(attrs={'class': 'form-control'}),  # Add new widget
            'quantity_in_stock': forms.NumberInput(attrs={'placeholder': 'Enter stock quantity'}),
            'is_latest': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Product Name',
            'short_description': 'Short Description',
            'detailed_description': 'Detailed Description',
            'main_image': 'Main Image',
            'measurement': 'Measurement Unit',  # Add new label
            'quantity_in_stock': 'Quantity in Stock',
            'is_latest': 'Mark as Latest Product',
            'is_featured': 'Mark as Featured Product',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['short_description'].required = True
        self.fields['detailed_description'].required = True
        self.fields['main_image'].required = True
        self.fields['measurement'].required = False  # Add measurement field requirement

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control is-invalid'})

        # Configure additional fields for multi-upload
        self.fields['additional_images'].widget.attrs.update({
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*'
        })
        self.fields['additional_documents'].widget.attrs.update({
            'class': 'form-control',
            'multiple': True,
            'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx,.csv,.ppt,.pptx'
        })

        # Add help text for fields
        self.fields['is_latest'].help_text = 'Check to mark this product as latest. The timestamp will be automatically set.'
        self.fields['is_featured'].help_text = 'Check to mark this product as featured. The timestamp will be automatically set.'
        self.fields['measurement'].help_text = 'Select the measurement unit for the product'  # Add help text for measurement


    def clean_name(self):
        """
        Custom validation for product name uniqueness
        """
        name = self.cleaned_data.get('name')
        if not name:
            return name

        # Get the current instance if we're editing
        instance = getattr(self, 'instance', None)
        
        # Build the query to check for duplicate names
        query = Product.objects.filter(name__iexact=name)
        
        # If we're editing, exclude the current instance from the check
        if instance and instance.pk:
            query = query.exclude(pk=instance.pk)
            
        # If we found any other products with this name
        if query.exists():
            raise ValidationError("Product with this Name already exists.")
            
        return name

    def clean_specifications(self):
        """
        Validate specifications format and content
        """
        specs = self.cleaned_data.get('specifications')
        if not specs:
            return []

        try:
            if isinstance(specs, str):
                specs = json.loads(specs)
            
            # Convert dict format to list format if necessary
            if isinstance(specs, dict):
                specs = [{'title': k, 'value': v} for k, v in specs.items()]
            
            # Validate each specification
            for spec in specs:
                if not isinstance(spec, dict):
                    raise ValidationError("Invalid specification format")
                
                if 'title' not in spec or 'value' not in spec:
                    raise ValidationError("Specifications must have both title and value")
                
                if not spec['title'].strip() or not spec['value'].strip():
                    raise ValidationError("Specification title and value cannot be empty")
                
        except json.JSONDecodeError:
            raise ValidationError("Invalid specification format")
        except (KeyError, AttributeError):
            raise ValidationError("Invalid specification structure")

        return specs

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Handle specifications
            specs_data = self.cleaned_data.get('specifications', [])
            
            # Delete existing specifications
            ProductSpecification.objects.filter(product=instance).delete()

            # Create new specifications
            for spec in specs_data:
                ProductSpecification.objects.create(
                    product=instance,
                    specification_title=spec['title'].strip(),
                    specification=spec['value'].strip()
                )

            # Handle categories
            instance.categories.clear()
            instance.categories.add(*self.cleaned_data['categories'])

            # Handle images
            images = self.files.getlist('additional_images')
            for image in images:
                ProductImage.objects.create(
                    product=instance,
                    product_image=image
                )

            # Handle documents
            documents = self.files.getlist('additional_documents')
            for document in documents:
                ProductDocument.objects.create(
                    product=instance,
                    title=document.name.split('.')[0],
                    document=document
                )

        return instance

#########################################################################################################################
#################################################################################################################################

from django import forms
from django.db.models import Q
from .models import Product, ProductSpecification, Category
import json
from django.core.exceptions import ValidationError
from django.utils import timezone

class EditProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.filter(deleted_at__isnull=True).filter(
            ~Q(id__in=Category.objects.filter(parent__isnull=False).values_list('parent', flat=True))
        ),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'multiple': 'multiple'
        }),
        required=True
    )
    specifications_data = forms.JSONField(
        required=False,
        widget=forms.HiddenInput()
    )

    is_latest = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = Product
        fields = [
            'name', 'short_description', 'detailed_description',
            'main_image', 'measurement', 'quantity_in_stock', 'categories',  # Added measurement
            'is_latest', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'detailed_description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5
            }),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'measurement': forms.Select(attrs={'class': 'form-control'}),  # Added measurement widget
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {  # Added labels section
            'measurement': 'Measurement Unit',
        }
        help_texts = {  # Added help_texts section
            'measurement': 'Select the measurement unit for the product',
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Set measurement field as optional
        self.fields['measurement'].required = False
        
        if instance:
            # Get all specifications for this product
            specs = instance.specifications.all()
            if specs.exists():
                specs_list = [
                    {
                        'title': spec.specification_title,
                        'value': spec.specification
                    }
                    for spec in specs
                ]
                self.initial['specifications_data'] = json.dumps(specs_list)

            # Set initial values for latest and featured status
            self.initial['is_latest'] = instance.is_latest
            self.initial['is_featured'] = instance.is_featured

    def clean_specifications_data(self):
        specs = self.cleaned_data.get('specifications_data')
        if not specs:
            return []
            
        try:
            if isinstance(specs, str):
                specs = json.loads(specs)
            if not isinstance(specs, list):
                raise ValidationError("Specifications must be a valid JSON array")
            
            # Validate each specification
            for spec in specs:
                if not isinstance(spec, dict):
                    raise ValidationError("Each specification must be an object")
                if 'title' not in spec or 'value' not in spec:
                    raise ValidationError("Each specification must have a title and value")
                if not spec['title'].strip() or not spec['value'].strip():
                    raise ValidationError("Specification title and value cannot be empty")
            
            return specs
        except json.JSONDecodeError:
            raise ValidationError("Invalid specification format")

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            # Get the current time for timestamp tracking
            current_time = timezone.now()
            
            # Check if latest status changed
            if instance.pk:
                old_instance = Product.objects.get(pk=instance.pk)
                if old_instance.is_latest != instance.is_latest:
                    instance.latest_marked_at = current_time if instance.is_latest else None
                if old_instance.is_featured != instance.is_featured:
                    instance.featured_marked_at = current_time if instance.is_featured else None
            else:
                if instance.is_latest:
                    instance.latest_marked_at = current_time
                if instance.is_featured:
                    instance.featured_marked_at = current_time
            
            instance.save()
            self.save_m2m()  # Save many-to-many fields (categories)
            
            # Handle specifications
            specs_data = self.cleaned_data.get('specifications_data', [])
            if isinstance(specs_data, str):
                specs_data = json.loads(specs_data)
            
            # Delete all existing specifications
            instance.specifications.all().delete()
            
            # Create new specifications
            for spec in specs_data:
                ProductSpecification.objects.create(
                    product=instance,
                    specification_title=spec['title'],
                    specification=spec['value']
                )
        
        return instance
    
################################################################################


from .models import Datasheet
from django.core.validators import MinLengthValidator, MinValueValidator


# class DatasheetForm(forms.ModelForm):
#     class Meta:
#         model = Datasheet
#         fields = [
#             'name',
#             'description',
#             'file',
#             'product'
#         ]
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter datasheet name'}),
#             'description': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter detailed description'}),
#             'file': forms.FileInput(attrs={'class': 'form-control'}),
#             'product': forms.Select(attrs={'class': 'form-control'})
#         }
#         labels = {
#             'name': 'Datasheet Name',
#             'description': 'Description',
#             'file': 'Datasheet File',
#             'product': 'Associated Product'
#         }
#         help_texts = {
#             'name': 'Descriptive and concise product name',
#             'description': 'Detailed explanation including features and benefits',
#             'file': 'Upload the datasheet file (PDF, DOC, etc.)',
#             'product': 'Select the product this datasheet belongs to'
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Set required fields
#         self.fields['name'].required = True
#         self.fields['file'].required = True
#         self.fields['product'].required = True
        
#         # Set form input classes and handle errors
#         for field_name, field in self.fields.items():
#             if not isinstance(field.widget, forms.SelectMultiple):
#                 field.widget.attrs.update({'class': 'form-control'})
#             if self.errors.get(field_name):
#                 field.widget.attrs.update({'class': 'form-control is-invalid'})

#         # Filter out deleted products from the product choices
#         self.fields['product'].queryset = self.fields['product'].queryset.filter(
#             deleted_at__isnull=True
#         )

# class DatasheetForm(forms.ModelForm):
#     class Meta:
#         model = Datasheet
#         fields = [
#             'name',
#             'description',
#             'file',
#             'product',
#             'include_size_dimensions',
#             'size',
#             'width',
#             'depth',
#             'height',
#         ]
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter datasheet name'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter detailed description'}),
#             'file': forms.FileInput(attrs={'class': 'form-control'}),
#             'product': forms.Select(attrs={'class': 'form-control'}),
#             'include_size_dimensions': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'include_size_dimensions'}),
#             'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter size (e.g., 5 MB, 10x10x5 cm)'}),
#             'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter width (cm/inches)', 'step': '0.01'}),
#             'depth': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter depth (cm/inches)', 'step': '0.01'}),
#             'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter height (cm/inches)', 'step': '0.01'}),
#         }
#         labels = {
#             'name': 'Datasheet Name',
#             'description': 'Description',
#             'file': 'Datasheet File',
#             'product': 'Associated Product',
#             'include_size_dimensions': 'Include Size and Dimensions',
#             'size': 'Size',
#             'width': 'Width',
#             'depth': 'Depth',
#             'height': 'Height',
#         }
#         help_texts = {
#             'name': 'Descriptive and concise product name',
#             'description': 'Detailed explanation including features and benefits',
#             'file': 'Upload the datasheet file (PDF, DOC, etc.)',
#             'product': 'Select the product this datasheet belongs to',
#             'include_size_dimensions': 'Check to include size and dimension details',
#             'size': 'Size (e.g., 5 MB, 10x10x5 cm)',
#             'width': 'Width (cm/inches)',
#             'depth': 'Depth (cm/inches)',
#             'height': 'Height (cm/inches)',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Set required fields
#         self.fields['name'].required = True
#         self.fields['file'].required = True
#         self.fields['product'].required = True
#         # Size and dimension fields are optional unless include_size_dimensions is True
#         self.fields['size'].required = False
#         self.fields['width'].required = False
#         self.fields['depth'].required = False
#         self.fields['height'].required = False
        
#         # Set form input classes and handle errors
#         for field_name, field in self.fields.items():
#             if not isinstance(field.widget, (forms.SelectMultiple, forms.CheckboxInput)):
#                 field.widget.attrs.update({'class': 'form-control'})
#             if self.errors.get(field_name):
#                 field.widget.attrs.update({'class': 'form-control is-invalid'})
        
#         # Filter out deleted products from the product choices
#         self.fields['product'].queryset = self.fields['product'].queryset.filter(deleted_at__isnull=True)
        
#         # If editing an existing instance, set initial visibility based on include_size_dimensions
#         if self.instance and self.instance.include_size_dimensions:
#             self.fields['size'].widget.attrs['style'] = ''
#             self.fields['width'].widget.attrs['style'] = ''
#             self.fields['depth'].widget.attrs['style'] = ''
#             self.fields['height'].widget.attrs['style'] = ''
#         else:
#             self.fields['size'].widget.attrs['style'] = 'display: none;'
#             self.fields['width'].widget.attrs['style'] = 'display: none;'
#             self.fields['depth'].widget.attrs['style'] = 'display: none;'
#             self.fields['height'].widget.attrs['style'] = 'display: none;'

#     def clean(self):
#         cleaned_data = super().clean()
#         include_size_dimensions = cleaned_data.get('include_size_dimensions')
        
#         # If include_size_dimensions is True, enforce that at least one size/dimension field is filled
#         if include_size_dimensions:
#             size = cleaned_data.get('size')
#             width = cleaned_data.get('width')
#             depth = cleaned_data.get('depth')
#             height = cleaned_data.get('height')
#             if not (size or width or depth or height):
#                 self.add_error('include_size_dimensions', 'At least one of size, width, depth, or height must be provided when including size and dimensions.')
        
#         return cleaned_data


from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Datasheet

class DatasheetForm(forms.ModelForm):
    class Meta:
        model = Datasheet
        fields = [
            'name',
            'description',
            'file',
            'product',
            'include_part_number',
            'part_number',
            'include_size_dimensions',
            'size',
            'width',
            'depth',
            'height',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter datasheet name'),
                'autocomplete': 'off',
                'minlength': '2',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Enter detailed description'),
                'rows': 4,
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xlsx,.xls',
            }),
            'product': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': _('Select a product'),
            }),
            'include_part_number': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'include_part_number',
                'role': 'switch',
            }),
            'part_number': forms.TextInput(attrs={
                'class': 'form-control part-number-field',
                'placeholder': _('Enter part number or reference number'),
            }),
            'include_size_dimensions': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'include_size_dimensions',
                'role': 'switch',
            }),
            'size': forms.TextInput(attrs={
                'class': 'form-control dimension-input',
                'placeholder': _('Enter the size'),
            }),
            'width': forms.TextInput(attrs={
                'class': 'form-control dimension-input',
                'placeholder': _('Enter width with unit (e.g., 10 cm, 5 inches)'),
            }),
            'depth': forms.TextInput(attrs={
                'class': 'form-control dimension-input',
                'placeholder': _('Enter depth with unit (e.g., 10 cm, 5 inches)'),
            }),
            'height': forms.TextInput(attrs={
                'class': 'form-control dimension-input',
                'placeholder': _('Enter height with unit (e.g., 10 cm, 5 inches)'),
            }),
        }
        labels = {
            'name': _('Datasheet Name'),
            'description': _('Description'),
            'file': _('Datasheet File'),
            'product': _('Associated Product'),
            'include_part_number': _('Include Part Number'),
            'part_number': _('Part Number'),
            'include_size_dimensions': _('Include Size and Dimensions'),
            'size': _('Size'),
            'width': _('Width'),
            'depth': _('Depth'),
            'height': _('Height'),
        }
        help_texts = {
            'name': _('Provide a descriptive and concise name (minimum 2 characters)'),
            'description': _('Detailed explanation including features and benefits'),
            'file': _('Upload datasheet file (Supported formats: PDF, DOC, DOCX, XLS, XLSX)'),
            'product': _('Select the product this datasheet belongs to'),
            'include_part_number': _('Enable to add part number or reference number'),
            'part_number': _('Product part number or reference number'),
            'include_size_dimensions': _('Enable to add size and dimension details'),
            'size': _('General size information (e.g., 5 MB, 10x10x5 cm)'),
            'width': _('Width with unit (e.g., 10 cm, 5 inches)'),
            'depth': _('Depth with unit (e.g., 10 cm, 5 inches)'),
            'height': _('Height with unit (e.g., 10 cm, 5 inches)'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['name'].required = True
        self.fields['file'].required = True
        self.fields['product'].required = True
        
        # Make optional fields
        self.fields['part_number'].required = False
        self.fields['size'].required = False
        self.fields['width'].required = False
        self.fields['depth'].required = False
        self.fields['height'].required = False
        
        # Filter active products
        self.fields['product'].queryset = self.fields['product'].queryset.filter(
            deleted_at__isnull=True
        ).order_by('name')

        # Set initial values for new records
        if not self.instance.pk:
            self.initial['created_by'] = self.user.username if self.user else ''
        self.initial['updated_by'] = self.user.username if self.user else ''

    def clean(self):
        cleaned_data = super().clean()
        include_size_dimensions = cleaned_data.get('include_size_dimensions')
        include_part_number = cleaned_data.get('include_part_number')
        
        # Validate size and dimensions
        if include_size_dimensions:
            dimension_values = [
                cleaned_data.get('size'),
                cleaned_data.get('width'),
                cleaned_data.get('depth'),
                cleaned_data.get('height')
            ]
            if not any(dimension_values):
                raise forms.ValidationError(
                    _("When size and dimensions are enabled, at least one measurement field must be provided.")
                )
        
        # Validate part number
        if include_part_number and not cleaned_data.get('part_number'):
            raise forms.ValidationError(
                _("Part number is required when 'Include Part Number' is enabled.")
            )
        
        return cleaned_data

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx']
            
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    _("Invalid file format. Supported formats: PDF, DOC, DOCX, XLS, XLSX")
                )
            
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError(
                    _("File size cannot exceed 10MB")
                )
        return file







