from django import forms
from .models import NewsArticle,BlogPost,JobListing
#from django_summernote.fields import SummernoteWidget


# from django_summernote.widgets import SummernoteWidget


class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = [
            'title',
            'short_description',
            'full_content',
            'category',
            'featured_image',
            'date_published',
            'is_active',
            'is_event_news',  
            'event_start_date',  
            'event_end_date',  
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the title'}),
            #'short_description': SummernoteWidget(),
            #'full_content': SummernoteWidget(),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter a short description'}),
            'full_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter the full content'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'date_published': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_event_news': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'event_start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'event_end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            
        }

        labels = {
            'title': 'News Title',
            'short_description': 'Short description',
            'full_content': 'Content',
            'category': 'News Category',
            'featured_image': 'News Icon',  
            'date_published': 'Publication Date',
            'is_active': 'Visible',
            'is_event_news': 'Event News',
            'event_start_date': 'Event Start Date',
            'event_end_date': 'Event End Date',
        }
        help_texts = {
            'title': 'Provide a concise and clear headline.',
            'short_description': 'Summarize the news article in a few sentences.',
            'full_content': 'Include detailed content, images, and videos if applicable.',
            'category': 'Select the appropriate category for the news.',
            'featured_image': 'Upload an image to represent the news article.',  # Help text for the featured_image field
            'date_published': 'Set the date and time of publication.',
            'is_active': 'Tick this box to make the article visible on the website.',
            'is_event_news': 'Check this box if the news is related to an event.',
            'event_start_date': 'Select the start date of the event.',
            'event_end_date': 'Select the end date of the event.',
        }




##############################################################################################



class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title',
            'author',  # Now it's a CharField
            'short_description',
            'content',
            'category',
            'tags',
            'featured_image',
            'date_published',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the blog title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),  # TextInput for CharField
            #'short_description': SummernoteWidget(),
            #'content': SummernoteWidget(),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter a Short description'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter the full content'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),  
            'date_published': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Post Title',
            'author': 'Author',  # Label for 'author'
            'short_description': 'Short description',
            'content': 'Blog Content',
            'category': 'Post Category',
            'tags': 'Tags',
            'featured_image': 'Featured Image',
            'date_published': 'Publication Date',
            'is_active': 'Active',
        }
        help_texts = {
            'title': 'Provide a concise and catchy title for your blog post.',
            'author': 'Enter the name of the author of this blog post.',
            'short_description': 'Give readers a brief short description about the blog post.',
            'content': 'Write the full content of your blog post here.',
            'category': 'Select a category that best describes your post.',
            'tags': 'Separate tags with commas to help with search and organization.',
            'featured_image': 'Upload an image to represent your post.',
            'date_published': 'Specify when this post will be published.',
            'is_active': 'Check this to make the post visible on the site.',
        }
        
##################################################################################################

from django import forms
from .models import JobListing

class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'job_title', 'department', 'job_location', 'job_description',
            'qualifications', 'application_link', 'application_instructions', 'active'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter the job title',
                'maxlength': 255
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter the department',
                'maxlength': 255
            }),
            'job_location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter the job location (e.g., Remote, New York Office)',
                'maxlength': 255
            }),
            #'job_description':SummernoteWidget(), 
            #'qualifications': SummernoteWidget(),
            'job_description':forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter the full job_description'}),
            'qualifications':forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter the qualifications'}),
            'application_link': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter the application link (if any)',
                'maxlength': 500
            }),
            'application_instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Provide instructions on how to apply if no link is provided'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'job_title': 'Job Title',
            'department': 'Department',
            'job_location': 'Job Location',
            'job_description': 'Job Description',
            'qualifications': 'Qualifications',
            'application_link': 'Application Link',
            'application_instructions': 'Application Instructions',
            'active': 'Active',
        }

    def clean(self):
        """Custom validation logic for the JobListing form."""
        cleaned_data = super().clean()
        job_title = cleaned_data.get('job_title')
        department = cleaned_data.get('department')
        job_location = cleaned_data.get('job_location')
        job_description = cleaned_data.get('job_description')
        qualifications = cleaned_data.get('qualifications')

        # Validate required fields
        if not job_title:
            self.add_error('job_title', 'Job title is required.')
        if not department:
            self.add_error('department', 'Department is required.')
        if not job_location:
            self.add_error('job_location', 'Job location is required.')
        if not job_description:
            self.add_error('job_description', 'Job description is required.')
        if not qualifications:
            self.add_error('qualifications', 'Qualifications are required.')

        # Ensure either application_link or application_instructions is provided
        application_link = cleaned_data.get('application_link')
        application_instructions = cleaned_data.get('application_instructions')

        if not application_link and not application_instructions:
            error_message = 'Either application link or application instructions must be provided.'
            self.add_error('application_link', error_message)
            self.add_error('application_instructions', error_message)



##################################################################################################

from .models import JobApplication, ContactSubmission

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'state', 'position', 'resume']
        
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB")
        return resume
    
###############################################################################

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['full_name', 'email', 'phone', 'message']

##################################################################################
# forms.py

from .models import NewsletterSubscription

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if NewsletterSubscription.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already subscribed to our newsletter.")
        return email
    

##################################################################################



from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'short_description',
            'content',
            'category',
            'status',
            'featured_image',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the project title'}),
            #'short_description': SummernoteWidget(),
            #'content': SummernoteWidget(),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Provide a brief summary of the project'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Provide detailed information about the project'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control',  'required': True}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Project Title',
            'short_description': 'Short Description',
            'content': 'Project Content',
            'category': 'Project Category',
            'status': 'Project Status',
            'featured_image': 'Featured Image',
            'is_active': 'Active',
        }
        help_texts = {
            'title': 'The title of the project.',
            'short_description': 'A brief summary of the project.',
            'content': 'Detailed information about the project, its objectives, scope, and significance.',
            'category': 'The category the project falls under.',
            'status': 'The current state of the project.',
            'featured_image': 'An image that represents the project.',
            'is_active': 'Indicates if the project is visible on the website.',
        }


##################################################################################

from .models import QuoteRequest


class QuoteRequestForm(forms.ModelForm):
    product_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    
    class Meta:
        model = QuoteRequest
        fields = ['full_name', 'email', 'phone', 'message', 'product']
        widgets = {
            'product': forms.HiddenInput()
        }
    

##################################################################################

from .models import CustomerServiceEnquiry

class CustomerServiceForm(forms.ModelForm):
    class Meta:
        model = CustomerServiceEnquiry
        exclude = ['status', 'created_at', 'updated_at', 'deleted_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['first_name','last_name','email', 'address', 'phone', 'city', 'postal_code', 'subject', 'question']
        for field in required_fields:
            self.fields[field].required = True

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if not phone.isdigit():
    #         raise forms.ValidationError("Phone number should contain only digits.")
    #     if len(phone) < 7 or len(phone) > 15:
    #         raise forms.ValidationError("Enter a valid phone number.")
    #     return phone


##################################################################################

from .models import QuestionSubmission

class QuestionSubmissionForm(forms.ModelForm):
    class Meta:
        model = QuestionSubmission
        exclude = ['status', 'created_at', 'updated_at', 'deleted_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['name', 'email', 'phone', 'country', 'product_name', 'question']
        for field in required_fields:
            self.fields[field].required = True

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if not phone.isdigit():
    #         raise forms.ValidationError("Phone number should contain only digits.")
    #     if len(phone) < 7 or len(phone) > 15:
    #         raise forms.ValidationError("Enter a valid phone number.")
    #     return phone
    

##################################################################################

from django import forms
from .models import PartnerApplication

class PartnerApplicationForm(forms.ModelForm):
    class Meta:
        model = PartnerApplication
        fields = ['name', 'position', 'phone', 'company', 'email', 'country', 'message']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if PartnerApplication.objects.filter(email=email, deleted_at__isnull=True).exists():
            raise forms.ValidationError("This email has already submitted a partner application.")
        return email

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if not phone.isdigit():
    #         raise forms.ValidationError("Phone number should contain only digits.")
    #     if len(phone) < 7 or len(phone) > 15:
    #         raise forms.ValidationError("Enter a valid phone number.")
    #     return phone



######################################################################################

from user_account.models import Partner
from django.contrib.auth.hashers import make_password

class PartnerForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-input',
            'placeholder': 'Enter password',
            'id': 'password-field'  # Add an ID for JavaScript targeting
        }),
        required=False
    )

    class Meta:
        model = Partner
        fields = [
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
            'partner_company_name',
            'business_type',
            'partnership_level',
        ]
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'partner_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter business type'}),
            'partnership_level': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('BRONZE', 'Bronze Partner'), ('SILVER', 'Silver Partner'), ('GOLD', 'Gold Partner')])
        }

        labels = {
            'email': 'Email Address',
            'username': 'Username',
            'password': 'Password',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'partner_company_name': 'Company Name',
            'business_type': 'Business Type',
            'partnership_level': 'Partnership Level',
        }

        help_texts = {
            'email': 'Enter a valid email address for the partner',
            'username': 'Choose a unique username (letters, numbers, and @/./+/-/_ only)',
            'password': 'Leave blank to keep current password or enter new password',
            'partner_company_name': 'Enter the official company name',
            'business_type': 'Specify the type of business',
            'partnership_level': 'Select the appropriate partnership tier',
        }

    def save(self, commit=True):
        partner = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        
        if password:
            partner.password = make_password(password)
            
        if commit:
            partner.save()
        return partner


################################################################################

from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'title',
            'description',
            'file',
            'resource_type',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter resource description'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Resource Title',
            'description': 'Description',
            'file': 'Upload File',
            'resource_type': 'Type of Resource'
        }
        help_texts = {
            'title': 'Enter a clear and descriptive title for the resource.',
            'description': 'Provide details about the resource and its contents.',
            'file': 'Upload your document, image, video, or other file (Max size: 10MB).',
            'resource_type': 'Select the type of resource you are uploading.'
        }    




######################################################################################

from django import forms
from .models import Banner, OfficeLocation

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            'title',
            'banner_type',
            'image',
            'alt_text',
            'url',
            'order',
            'is_active',
            'meta_title',
            'meta_description',
            'meta_keywords',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter banner title'
            }),
            'banner_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),  
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter alternative text for the image'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter URL for the banner'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter display order'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meta title'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meta description'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meta keywords (comma-separated)'
            }),
        }
        labels = {
            'title': 'Banner Title',
            'banner_type': 'Banner Type',
            'image': 'Banner Image',
            'alt_text': 'Alternative Text',
            'url': 'Banner URL',
            'order': 'Display Order',
            'is_active': 'Active Status',
            'meta_title': 'Meta Title',
            'meta_description': 'Meta Description',
            'meta_keywords': 'Meta Keywords',
        }
        help_texts = {
            'title': 'Enter a descriptive title for administrative purposes.',
            'banner_type': 'Select the type of banner (Slider, About, or Sustainability).',
            'image': 'Upload the banner image. Recommended size depends on banner type.',
            'alt_text': 'Provide alternative text for accessibility purposes.',
            'url': 'Enter the URL where this banner should link to (optional).',
            'order': 'Set the display order (especially important for slider banners).',
            'is_active': 'Toggle whether this banner is currently active on the site.',
            'meta_title': 'Enter SEO meta title (max 60 characters).',
            'meta_description': 'Enter SEO meta description (max 160 characters).',
            'meta_keywords': 'Enter SEO keywords, separated by commas.',
        }

#####################################################################################


class OfficeLocationForm(forms.ModelForm):
    class Meta:
        model = OfficeLocation
        fields = [
            'title',
            'office_country',
            'partnership_type',  # <-- New field added
            'address',
            'phone',
            'email',
            'latitude',
            'longitude',
            'image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter office location title'
            }),
            'office_country': forms.Select(attrs={
                'class': 'form-control'
            }),
            'partnership_type': forms.Select(attrs={  # <-- New widget
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter latitude',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter longitude',
                'step': 'any'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Office Name',
            'office_country': 'Country',
            'partnership_type': 'Partnership Type',  # <-- New label
            'address': 'Office Address',
            'phone': 'Contact Number',
            'email': 'Email Address',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'image': 'Office Image',
        }
        help_texts = {
            'title': 'Enter the name or title of the office location.',
            'office_country': 'Select the country where the office is located.',
            'partnership_type': 'Select the type of partnership for this office.',  # <-- New help text
            'address': 'Provide the complete physical address of the office.',
            'phone': 'Enter the contact number with country code if applicable.',
            'email': 'Enter the official email address for this office.',
            'latitude': 'Enter the precise latitude coordinate for map placement.',
            'longitude': 'Enter the precise longitude coordinate for map placement.',
            'image': 'Upload an image of the office location (optional).',
        }





