from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# from .fields import CustomSummernoteTextField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError


class NewsArticle(models.Model):
    TITLE_MAX_LENGTH = 200
    CATEGORY_CHOICES = [
        ('product_launch', 'Product Launch'),
        ('industry_update', 'Industry Update'),
        ('other', 'Other'),
    ]
    slug = models.SlugField(max_length=255, null=True, unique=True, blank=True, help_text=_("URL-friendly version of the article title"))
    #slug = models.SlugField(max_length=255, null=True, blank=True, help_text=_("URL-friendly version of the article title"))
    title = models.CharField(max_length=TITLE_MAX_LENGTH, verbose_name='Title', help_text='The headline or title of the news article.')
    short_description = models.TextField(blank=True, null=True, verbose_name='Short Description', help_text='A brief summary of the news article.')
    full_content = models.TextField(blank=True, null=True, verbose_name='Full Content', help_text='The body of the news article, which can include text, images, and videos.')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Category', help_text='Category or type of news.')
    is_event_news = models.BooleanField(default=False, verbose_name='Is Event News', help_text='If True, this news is related to an event.')
    event_start_date = models.DateTimeField(blank=True, null=True, verbose_name='Event Start Date', help_text='The start date of the event (required if this is an event news).')
    event_end_date = models.DateTimeField(blank=True, null=True, verbose_name='Event End Date', help_text='The end date of the event (required if this is an event news).')
    featured_image = models.ImageField(blank=True, null=True, upload_to='news_icons/', verbose_name='News Icon', help_text='The icon image representing the news article, shown as a thumbnail or preview image.')
    featured_image_alt = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Featured Image Alt Text"), help_text=_("Alternative text for the featured image for accessibility and SEO."))
    date_published = models.DateTimeField(verbose_name='Date Published', help_text='The publication date of the news article.')
    is_active = models.BooleanField(default=True, verbose_name='Active', help_text='A boolean field to specify if the news is active (visible on the website).')
    
    meta_tags = models.CharField(max_length=255, blank=True, null=True, help_text=_("SEO-friendly title (if different from name)"))
    meta_description = models.TextField(blank=True, null=True, help_text=_("Short description for search engine snippets"))
    canonical_url = models.URLField(blank=True, null=True, help_text=_("Canonical URL to avoid duplicate content"))
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-date_published']

    def save(self, *args, **kwargs):
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Handle duplicate slugs
        original_slug = self.slug
        counter = 1
        
        while NewsArticle.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Set default SEO fields if not provided
        if not self.meta_tags:
            self.meta_tags = self.title
        
        if not self.meta_description:
            self.meta_description = self.short_description or self.title
        
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    TITLE_MAX_LENGTH = 200
    CATEGORY_CHOICES = [
        ('business_achievements', 'Business Achievements'),
        ('tech_news', 'Tech News'),
        ('how_to_guides', 'How-To Guides'),
        ('other', 'Other'),
    ]

    
    title = models.CharField(max_length=TITLE_MAX_LENGTH, verbose_name='Title', help_text='The headline of the blog post.')
    author = models.CharField(blank=True, null=True, max_length=255, verbose_name='Author', help_text='The name of the blog post author.')
    short_description = models.TextField(blank=True, null=True, verbose_name='Short Description', help_text='A teaser or brief description of the blog post.')
    content = models.TextField(blank=True, null=True, verbose_name='Content', help_text='The full content of the blog post, including text, images, videos, and other media.')
    #short_description = CustomSummernoteTextField(blank=True, null=True, verbose_name='Short Description', help_text='A teaser or brief description of the blog post.')
    #content = CustomSummernoteTextField(blank=True, null=True, verbose_name='Content', help_text='The full content of the blog post, including text, images, videos, and other media.')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Category', help_text='The blog category to help organize posts.')
    tags = models.CharField(max_length=200, verbose_name='Tags', help_text='Keywords or phrases associated with the blog post.')
    featured_image = models.ImageField(upload_to='blog_images/', verbose_name='Featured Image', help_text='The image that will appear at the top of the blog post or as a thumbnail.')
    featured_image_alt = models.CharField(max_length=255, blank=True, null=True, verbose_name='Image Alt Text', help_text='Alternative text for the featured image.')
    #author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Author', help_text='The name of the blog post author.')
    date_published = models.DateTimeField(verbose_name='Date Published', help_text='The publication date of the blog post.')
    is_active = models.BooleanField(default=True, verbose_name='Active', help_text='A boolean field to indicate if the blog post is currently live.')

    slug = models.SlugField(max_length=255, null=True, unique=True, blank=True, help_text='URL-friendly version of the blog title')
    #slug = models.SlugField(max_length=255, null=True, blank=True, help_text='URL-friendly version of the blog title')
    meta_tags = models.CharField(max_length=255, blank=True, null=True, help_text='SEO-friendly title (if different from name)')
    meta_description = models.TextField(blank=True, null=True, help_text='Short description for search engine snippets')
    canonical_url = models.URLField(blank=True, null=True, help_text='Canonical URL to avoid duplicate content')
    
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-date_published']
    
    def save(self, *args, **kwargs):
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Handle duplicate slugs
        original_slug = self.slug
        counter = 1
        
        while BlogPost.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Set default SEO fields if not provided
        if not self.meta_tags:
            self.meta_tags = self.title
        
        if not self.meta_description:
            self.meta_description = self.short_description or self.title
        
        super().save(*args, **kwargs)





class JobListing(models.Model):
    job_title = models.CharField(max_length=255, help_text="Job title")
    department = models.CharField(max_length=255, help_text="Department")
    job_location = models.CharField(max_length=255, help_text="Office location or remote")
    job_description = models.TextField(help_text="Job role, responsibilities, and requirements", blank=True, null=True)
    qualifications = models.TextField(help_text="Skills, experience, and education required", blank=True, null=True)
    #job_description = CustomSummernoteTextField(help_text="Job role, responsibilities, and requirements", blank=True, null=True)
    #qualifications = CustomSummernoteTextField(help_text="Skills, experience, and education required", blank=True, null=True)
    application_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link to apply for the job"
    )
    application_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="How to submit an application if no link is provided"
    )
    active = models.BooleanField(default=True, help_text="Is the job listing active?")
    date_posted = models.DateField(auto_now_add=True, help_text="Date posted")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.job_title
    
#################################################################################

from django.core.validators import FileExtensionValidator

class JobApplication(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    resume = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class ContactSubmission(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contact from {self.full_name} - {self.created_at.strftime('%Y-%m-%d')}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Subscription: {self.email}"


############################################################################################
# models.py

class Project(models.Model): 
    TITLE_MAX_LENGTH = 200
    
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    CATEGORY_CHOICES = [
        ('network_infrastructure', 'Network Infrastructure'),
        ('cybersecurity', 'Cybersecurity'),
        ('cloud_solutions', 'Cloud Solutions'),
        ('other', 'Other'),
    ]
    
    
    title = models.CharField(max_length=TITLE_MAX_LENGTH, verbose_name='Project Title', help_text='The title of the project.'); 
    short_description =models.TextField(blank=True, null=True, verbose_name='Short Description', help_text='A brief summary of the project.'); 
    content = models.TextField(blank=True, null=True, verbose_name='Content', help_text='Detailed information about the project, its objectives, scope, and significance.');

    #short_description = CustomSummernoteTextField(blank=True, null=True, verbose_name='Short Description', help_text='A brief summary of the project.'); 
    #content = CustomSummernoteTextField(blank=True, null=True, verbose_name='Content', help_text='Detailed information about the project, its objectives, scope, and significance.'); 
    category = models.CharField(blank=True, null=True, max_length=50, choices=CATEGORY_CHOICES, verbose_name='Project Category', help_text='The category the project falls under.'); 
    status = models.CharField(blank=True, null=True, max_length=20, choices=STATUS_CHOICES, default='ongoing', verbose_name='Project Status', help_text='The current state of the project.'); 
    featured_image = models.ImageField(upload_to='project_images/', blank=True, null=True, verbose_name='Featured Image', help_text='An image that represents the project.'); 
    featured_image_alt = models.CharField(max_length=255, blank=True, null=True, verbose_name='Image Alt Text', help_text='Alternative text for the featured image.')
    
    is_active = models.BooleanField(default=True, verbose_name='Active', help_text='Indicates if the project is visible on the website.'); 
    
    slug = models.SlugField(max_length=255, null=True, unique=True, blank=True, help_text='URL-friendly version of the project title')
    #slug = models.SlugField(max_length=255, null=True, blank=True, help_text='URL-friendly version of the blog title')
    meta_tags = models.CharField(max_length=255, blank=True, null=True, help_text='SEO-friendly title (if different from name)')
    meta_description = models.TextField(blank=True, null=True, help_text='Short description for search engine snippets')
    canonical_url = models.URLField(blank=True, null=True, help_text='Canonical URL to avoid duplicate content')
    
    
    created_at = models.DateTimeField(auto_now_add=True); 
    updated_at = models.DateTimeField(auto_now=True); 
    deleted_at = models.DateTimeField(null=True, blank=True); 
    

    def __str__(self): 
        return self.title; 

    class Meta: 
        verbose_name = 'Project'; 
        verbose_name_plural = 'Projects'; 
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Handle duplicate slugs
        original_slug = self.slug
        counter = 1
        
        while Project.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        # Set default SEO fields if not provided
        if not self.meta_tags:
            self.meta_tags = self.title

        if not self.meta_description:
            self.meta_description = self.short_description or self.title

        super().save(*args, **kwargs)


##################################################################################################

# class QuoteRequest(models.Model):
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_processed = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Quote Request from {self.full_name} - {self.created_at.strftime('%Y-%m-%d')}"

#     class Meta:
#         ordering = ['-created_at']




class QuoteRequest(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    # Correct product relation
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        product_name = self.product.name if self.product else "No Product"
        return f"Quote Request from {self.full_name} - {product_name} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']



##################################################################################################

class CustomerServiceEnquiry(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Support'),
        ('billing', 'Billing Support'),
        ('product', 'Product Support'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    
    # Contact Information
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    
    # Enquiry Details
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    question = models.TextField()
    attachment = models.FileField(
        upload_to='customer_service_attachments/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True); 
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        default='pending'
    )

    class Meta:
        verbose_name = 'Customer Service Enquiry'
        verbose_name_plural = 'Customer Service Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"



##################################################################################################


class QuestionSubmission(models.Model):
    # Personal Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Question Details
    product_name = models.CharField(max_length=200)  
    question = models.TextField()
    attachment = models.FileField(
        upload_to='question_attachments/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True); 

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('answered', 'Answered'),
            ('closed', 'Closed'),
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question Submission'
        verbose_name_plural = 'Question Submissions'

    def __str__(self):
        return f"Question about {self.product_name} from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"


##################################################################################################

from django.utils import timezone
from django.db import models

class PartnerApplication(models.Model):
    # Personal Information
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20)
    
    # Company Information
    company = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100)
    
    # Application Details
    message = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('reviewing', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='new'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Partner Application'
        verbose_name_plural = 'Partner Applications'

    def __str__(self):
        return f"Partner Application - {self.company} ({self.name})"
    


###########################################################################################

import os

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('DOCUMENT', 'Document'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    file = models.FileField(
        upload_to='partner_resources/%Y/%m/',
        max_length=500
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        default='DOCUMENT'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) 
    
    def __str__(self):
        return self.title
    
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
    
    def file_size(self):
        try:
            size = self.file.size

            if size > 1024*1024:
                return f"{size/(1024*1024):.2f} MB"
            elif size > 1024:
                return f"{size/1024:.2f} KB"
            return f"{size} bytes"
        except:
            return "Unknown size"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')


#########################################################################################

from django.conf import settings
from catalog.models import Product,Datasheet

class TheList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return self.name
    
class ListItem(models.Model):
    list = models.ForeignKey(TheList, on_delete=models.CASCADE, related_name='items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='list_items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    datasheet = models.ForeignKey(
        Datasheet,  
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True,  
        related_name='list_items', 
        help_text=_("Optional reference to a datasheet for the product")
    )
    
    def __str__(self):
        return f"{self.product_name} ({self.quantity}) in {self.list.name}"
    

    ##################################################################################

class AdminRequestQuote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_quote_requests'
    )
    user_username = models.CharField(max_length=150, blank=True)  # Store username snapshot
    list_name = models.CharField(max_length=255)  # Store list name snapshot
    list_note = models.TextField(blank=True, null=True)  # Store list note snapshot
    total_items = models.PositiveIntegerField(default=0)
    request_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('COMPLETED', 'Completed')
        ],
        default='PENDING'
    )

    class Meta:
        ordering = ['-request_date']
        verbose_name = 'Admin Quote Request'
        verbose_name_plural = 'Admin Quote Requests'

    def __str__(self):
        return f"Quote Request {self.id} by {self.user_username or 'Deleted User'} on {self.request_date.strftime('%Y-%m-%d')}"

class AdminRequestQuoteItem(models.Model):
    quote_request = models.ForeignKey(
        AdminRequestQuote,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_quote_request_items'
    )
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Quote Request Item'
        verbose_name_plural = 'Admin Quote Request Items'

    def __str__(self):
        return f"{self.product_name} (Qty: {self.quantity}) in Quote Request {self.quote_request.id}"
    

###################################################################################

class Banner(models.Model):
    BANNER_TYPE_CHOICES = [
        ('slider', 'Slider Banner'),
        ('about', 'About Banner'),
        ('sustainability', 'Sustainability Banner')
    ]

    title = models.CharField(
        max_length=200,
        help_text=_("Banner title for administrative purposes")
    )
    banner_type = models.CharField(
        max_length=20,
        choices=BANNER_TYPE_CHOICES,
        help_text=_("Type of banner")
    )
    image = models.ImageField(
        upload_to='banners/',
        help_text=_("Banner image")
    )
    alt_text = models.CharField(
        max_length=200,
        help_text=_("Alternative text for image accessibility"),
        blank=True
    )
    url = models.CharField(
        max_length=200,
        help_text=_("URL for banner link"),
        blank=True
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text=_("Order of appearance (only applies to slider banners)")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this banner is currently active")
    )
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text=_("Meta title for SEO (max 60 characters)")
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text=_("Meta description for SEO (max 160 characters)")
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Meta keywords for SEO (comma-separated)")
    )
    
    # Tracking Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['banner_type', 'order', '-created_at']
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")

    def __str__(self):
        return f"{self.get_banner_type_display()} - {self.title}"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()


##########################################################################################

# class OfficeLocation(models.Model):
#     OFFICE_COUNTRY = [
#         ('Bahrain', 'Bahrain'),
#         ('Qatar', 'Qatar'),
#         ('United Arab Emirates', 'United Arab Emirates'),
#         ('Oman', 'Oman'),
#         ('Yemen', 'Yemen'),
#         ('Saudi Arabia', 'Saudi Arabia'),
#         ('Iran', 'Iran'),
#         ('Kuwait', 'Kuwait'),
#         ('Egypt', 'Egypt'),
#         ('Jordan', 'Jordan'),
#         ('Syria', 'Syria'),
#     ]
    
#     title = models.CharField(max_length=200)
#     office_country = models.CharField(max_length=20, choices=OFFICE_COUNTRY, null=True, blank=True)
#     address = models.TextField()
#     phone = models.CharField(max_length=20)
#     email = models.EmailField()
#     latitude = models.DecimalField(max_digits=9, decimal_places=6)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6)
#     image = models.ImageField(upload_to='Office_locations/', blank=True, null=True)

#     # Tracking Fields
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)
    
#     def __str__(self):
#         return self.title
    
#     def soft_delete(self):
#         self.deleted_at = timezone.now()
#         self.is_active = False
#         self.save()

#     def restore(self):
#         self.deleted_at = None
#         self.is_active = True
#         self.save()

class OfficeLocation(models.Model):
    OFFICE_COUNTRY = [
        ('Bahrain', 'Bahrain'),
        ('Qatar', 'Qatar'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('Oman', 'Oman'),
        ('Yemen', 'Yemen'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Iran', 'Iran'),
        ('Kuwait', 'Kuwait'),
        ('Egypt', 'Egypt'),
        ('Jordan', 'Jordan'),
        ('Syria', 'Syria'),
    ]

    PARTNERSHIP_TYPES = [
        ('Strategic Partner', 'Strategic Partner'),
        ('Premier Partner', 'Premier Partner'),
        ('Preferred Partner', 'Preferred Partner'),
        ('Master Partner', 'Master Partner'),
        ('General Partner', 'General Partner'),
    ]

    title = models.CharField(max_length=200)
    office_country = models.CharField(max_length=20, choices=OFFICE_COUNTRY, null=True, blank=True)
    partnership_type = models.CharField(
        max_length=50, choices=PARTNERSHIP_TYPES, null=True, blank=True
    )  # <-- New field added here
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    image = models.ImageField(upload_to='Office_locations/', blank=True, null=True)

    # Tracking Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()

    


    









    
