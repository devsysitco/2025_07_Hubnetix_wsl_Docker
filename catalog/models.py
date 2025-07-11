from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import random
import string
from datetime import datetime
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

#from .fields import CustomSummernoteTextField


class Category(models.Model):
    STYLE_CHOICES = [('grid', _('Grid')), ('list', _('List')), ('custom', _('Custom Design'))]

    id = models.AutoField(primary_key=True)
    Category_id = models.PositiveIntegerField(unique=True, blank=True, null=True, help_text=_("Custom auto-incremented ID"))
    name = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(2)], help_text=_("Display name for the category"))
    seo_name = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alternative name for SEO purposes"))
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text=_("URL-friendly version of the category name"))
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='grid', help_text=_("Visual display style for the category"))
    short_description = models.CharField(max_length=255, blank=True, null=True, help_text=_("Brief summary for search results or listings"))
    detailed_description = models.TextField(blank=True, null=True, help_text=_("Comprehensive description for SEO and context"))

    #Note Field
    #detailed_description = SummernoteTextField(blank=True, null=True, help_text=_("Comprehensive description for SEO and context"))
    #detailed_description = CustomSummernoteTextField(blank=True, null=True, help_text=_("Comprehensive description for SEO and context"))
    #detailed_description = CustomSummernoteTextField(blank=True, null=True, help_text=_("Comprehensive description for SEO and context"))
    
    
    # SEO Meta Fields
    meta_tags = models.CharField(max_length=255, blank=True, null=True, help_text=_("SEO-friendly title (if different from name)"))
    meta_description = models.TextField(blank=True, null=True, help_text=_("Short description for search engine snippets"))
    canonical_url = models.URLField(blank=True, null=True, help_text=_("Canonical URL to avoid duplicate content"))

    # Images with Alt Text
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])], help_text=_("Icon representing the category"))
    icon_alt = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alt text for the icon image"))

    banner = models.ImageField(upload_to='category_banners/', blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])], help_text=_("Large banner image at the top of the category page"))
    banner_alt = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alt text for the banner image"))

    side_image = models.ImageField(upload_to='category_side_images/', blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])], help_text=_("Side image for promoting sub-categories"))
    side_image_alt = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alt text for the side image"))

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subcategories', blank=True, null=True, help_text=_("Parent category for multi-level hierarchy"))
    is_active = models.BooleanField(default=True, help_text=_("Indicates if the category is currently active"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def get_hierarchy_string(self):
        """
        Recursively builds the full category hierarchy string
        """
        if self.parent is None:
            return self.name
        else:
            return f"{self.parent.get_hierarchy_string()} -> {self.name}"
    
    def __str__(self):
        return self.get_hierarchy_string()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        original_slug = self.slug
        counter = 1
        while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        if not self.meta_tags:
            self.meta_tags = self.name

        if not self.meta_description:
            self.meta_description = self.short_description or self.name

        super().save(*args, **kwargs)

@receiver(post_save, sender='catalog.Category')
def set_category_id(sender, instance, created, **kwargs):
    if created and instance.Category_id is None:
        post_save.disconnect(set_category_id, sender='catalog.Category')
        try:
            instance.Category_id = instance.id
            instance.save()
        finally:
            post_save.connect(set_category_id, sender='catalog.Category')


############################################################################################

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(2)], help_text=_("Descriptive and concise product name"))
    seo_name = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alternative name for SEO purposes"))
    slug = models.SlugField(max_length=255, unique=True, help_text=_("URL-friendly version of the product name"))
    short_description = models.CharField(max_length=255, blank=True, null=True, help_text=_("Brief summary for listings or previews"))
    detailed_description = models.TextField(blank=True, null=True, help_text=_("Detailed explanation including features and benefits"))
    # detailed_description = CustomSummernoteTextField(blank=True, null=True, help_text=_("Detailed explanation including features and benefits"))

    MEASUREMENT_CHOICES = [
        ("Nos", "Nos"),
        ("305 Mtr Box", "305 Mtr Box"),
        ("500 Mtr Box", "500 Mtr Box"),
        ("305 Mtr Roll", "305 Mtr Roll"),
        ("500 Mtr Roll", "500 Mtr Roll"),
        ("Mtr", "Mtr"),
    ]

    measurement = models.CharField(max_length=50, blank=True, null=True, choices=MEASUREMENT_CHOICES, help_text=_("Measurement of the product"))

    
    # Add new fields for latest and featured products
    is_latest = models.BooleanField(default=False, help_text=_("Flag to mark product as latest"))
    latest_marked_at = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp when product was marked as latest"))
    is_featured = models.BooleanField(default=False, help_text=_("Flag to mark product as featured"))
    featured_marked_at = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp when product was marked as featured"))

    categories = models.ManyToManyField('Category', related_name='products', blank=True, help_text=_("Categories this product belongs to"))
    
    main_image = models.ImageField(upload_to='product_images/main/', blank=True, null=True, 
                                   validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])], 
                                   help_text=_("Primary image representing the product"))
    main_image_alt = models.CharField(max_length=255, blank=True, null=True, help_text=_("Alt text for the main image"))

    quantity_in_stock = models.PositiveIntegerField(default=0, help_text=_("Available quantity of the product"))

    meta_tags = models.CharField(max_length=255, blank=True, null=True, help_text=_("SEO-friendly title (if different from name)"))
    meta_description = models.TextField(blank=True, null=True, help_text=_("Short description for search engine snippets"))
    canonical_url = models.URLField(blank=True, null=True, help_text=_("Canonical URL to avoid duplicate content"))

    # created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_products')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Get current time for timestamp updates
        current_time = timezone.now()

        # Handle slug generation
        if not self.slug:
            self.slug = slugify(self.name)

        original_slug = self.slug
        counter = 1
        while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        # Handle meta tags and description
        if not self.meta_tags:
            self.meta_tags = self.name

        if not self.meta_description:
            self.meta_description = self.short_description or self.name

        # Handle latest and featured status timestamps
        if self.pk:  # If the object already exists
            old_instance = Product.objects.get(pk=self.pk)
            
            # Handle latest status change
            if old_instance.is_latest != self.is_latest:
                if self.is_latest:
                    self.latest_marked_at = current_time
                else:
                    self.latest_marked_at = None
            
            # Handle featured status change
            if old_instance.is_featured != self.is_featured:
                if self.is_featured:
                    self.featured_marked_at = current_time
                else:
                    self.featured_marked_at = None
        else:  # If this is a new object
            if self.is_latest:
                self.latest_marked_at = current_time
            if self.is_featured:
                self.featured_marked_at = current_time

        super().save(*args, **kwargs)
    
    


class ProductImage(models.Model):
    product_image = models.ImageField(
        upload_to='product_images/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])],
        help_text=_("Additional images for the product")
    )
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    alt_text = models.CharField(max_length=255, help_text=_("Alternative text for the image"), blank=True, null=True)
    #created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_product_images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - Image"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    specification_title = models.CharField(max_length=255, help_text=_("Specification heading"))
    specification = models.TextField(help_text=_("Specification value"))
    
    #created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_specifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.specification_title}: {self.specification}"


class ProductDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('manual', _('User Manual')),
        ('specification', _('Technical Specification')),
        ('brochure', _('Product Brochure')),
        ('other', _('Other Document'))
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents', help_text=_("Product associated with this document"))
    title = models.CharField(max_length=255, help_text=_("Title of the document"))
    document = models.FileField(upload_to='product_documents/', validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx'])], help_text=_("Uploadable document related to the product"))
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='Product Documentation', help_text=_("Classification of the document"))
    #created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_product_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.product.name}"
    

from django.core.validators import MinLengthValidator, MinValueValidator

# class Datasheet(models.Model):
#     name = models.CharField(max_length=255,  validators=[MinLengthValidator(2)], help_text=_("Descriptive and concise product name"))
#     description = models.TextField(blank=True, null=True, help_text=_("Detailed explanation including features and benefits"))
#     file = models.FileField(upload_to='datasheets/products/')
    
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='datasheets')

#     size = models.CharField(max_length=50, blank=True, null=True, help_text=_("Size (e.g., 5 MB, 10x10x5 cm)"))
#     width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], help_text=_("Width (cm/inches)"))
#     depth = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], help_text=_("Depth (cm/inches)"))
#     height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], help_text=_("Height (cm/inches)"))
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"Datasheet for {self.product.name}"
    
#     def get_filename(self):
#         return self.file.name.split('/')[-1] if self.file else ''

#     class Meta:
#         ordering = ['name']


class Datasheet(models.Model):
    name = models.CharField(max_length=255, validators=[MinLengthValidator(2)], help_text=_("Descriptive and concise product name"))
    description = models.TextField(blank=True, null=True, help_text=_("Detailed explanation including features and benefits"))
    file = models.FileField(upload_to='datasheets/products/')
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='datasheets')

    include_part_number = models.BooleanField(default=False, help_text=_("Check to include part_number or reference number"))

    # Add the new part number field
    part_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Product part number or reference number")
    )

    include_size_dimensions = models.BooleanField(default=False, help_text=_("Check to include size and dimension details"))
    size = models.CharField(max_length=50, blank=True, null=True, help_text=_("Size (e.g., 5 MB, 10x10x5 cm)"))

    width = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    depth = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
        
    )
    height = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
        
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Datasheet for {self.product.name}"
    
    def get_filename(self):
        return self.file.name.split('/')[-1] if self.file else ''

    class Meta:
        ordering = ['name']

    

    




