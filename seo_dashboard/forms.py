from django import forms
from catalog.models import Category
from django.core.exceptions import ValidationError
#from django_summernote.fields import SummernoteWidget
from admin_dashboard.models import NewsArticle,BlogPost,Project



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'short_description', 'detailed_description',
            'meta_tags', 'meta_description', 'canonical_url',
            'icon', 'icon_alt', 'banner', 'banner_alt', 'side_image', 'side_image_alt'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name', 'readonly': 'readonly'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short description', 'readonly': 'readonly'}),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter detailed description', 'readonly': 'readonly'}),
            'meta_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meta tags'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter meta description'}),
            'canonical_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter canonical URL'}),
            'icon': forms.FileInput(attrs={'class': 'form-control'}),
            'icon_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter icon alt text'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'banner_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter banner alt text'}),
            'side_image': forms.FileInput(attrs={'class': 'form-control'}),
            'side_image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter side image alt text'}),
        }
        labels = {
            'name': 'Category Name',
            'slug': 'Slug',
            'short_description': 'Short Description',
            'detailed_description': 'Detailed Description',
            'meta_tags': 'Meta Tags',
            'meta_description': 'Meta Description',
            'canonical_url': 'Canonical URL',
            'icon': 'Icon',
            'icon_alt': 'Icon Alt Text',
            'banner': 'Banner',
            'banner_alt': 'Banner Alt Text',
            'side_image': 'Side Image',
            'side_image_alt': 'Side Image Alt Text',
        }
        help_texts = {
            'name': 'Display name for the category',
            'slug': 'URL-friendly version of the category name',
            'short_description': 'Brief summary for search results or listings',
            'detailed_description': 'Comprehensive description for SEO and context',
            'meta_tags': 'SEO-friendly tags for better visibility',
            'meta_description': 'Short description for search engine snippets',
            'canonical_url': 'Canonical URL to avoid duplicate content',
            'icon': 'Icon representing the category',
            'icon_alt': 'Alt text for the icon image',
            'banner': 'Large banner image at the top of the category page',
            'banner_alt': 'Alt text for the banner image',
            'side_image': 'Side image for promoting sub-categories',
            'side_image_alt': 'Alt text for the side image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required fields for SEO team
        self.fields['slug'].required = True
        self.fields['short_description'].required = True
        self.fields['meta_description'].required = True

        # Add Bootstrap error styling if validation fails
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control is-invalid'})


#######################################################################################################
# 2024-12-18
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from catalog.models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'short_description', 'detailed_description',
            'main_image', 'main_image_alt', 'meta_tags', 'meta_description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name', 'readonly': 'readonly'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter short description', 'readonly': 'readonly'}),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter detailed description', 'readonly': 'readonly'}),
            'meta_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meta tags'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter meta description'}),
        }

class ProductImageForm(forms.ModelForm):
    # Add this to make the field not required for new instances
    product_image = forms.ImageField(required=False)
    
    class Meta:
        model = ProductImage
        fields = ['product_image', 'alt_text']

# Custom formset that handles empty forms better
class BaseProductImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # No validation needed for empty forms
        for form in self.forms:
            if not form.has_changed() and not form.instance.pk:
                for field in form.errors:
                    form.errors[field] = []

# Use our custom formset as the base
ProductImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    form=ProductImageForm, 
    formset=BaseProductImageFormSet,  # Use our custom formset
    extra=0,
    can_delete=False
)


#######################################################################################

from .models import OldUrlRedirect

class OldUrlRedirectForm(forms.ModelForm):
    class Meta:
        model = OldUrlRedirect
        fields = ['old_slug', 'new_slug', 'url_type']
        widgets = {
            'old_slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter old PHP URL slug without .php'}),
            'new_slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL slug for redirection'}),
            'url_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'old_slug': 'Old URL Slug',
            'new_slug': 'New URL Slug',
            'url_type': 'URL Type',
        }
        help_texts = {
            'old_slug': 'Enter the old PHP URL slug without the .php extension.',
            'new_slug': 'Enter the new URL slug for redirection.',
            'url_type': 'Select the type of URL (Category or Product).',
        }

    def clean_old_slug(self):
        old_slug = self.cleaned_data.get('old_slug')
        if '.php' in old_slug:
            raise ValidationError("The old slug should not contain '.php'.")
        return old_slug
    
######################################################################################



class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = [
            'title', 'slug', 'short_description', 'full_content', 
            'featured_image', 'featured_image_alt',
            'meta_tags', 'meta_description', 'canonical_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter article title', 'readonly': 'readonly'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter short description', 'rows': 3, 'readonly': 'readonly'}),
            'full_content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter full content', 'readonly': 'readonly'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured_image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter image alt text'}),
            'date_published': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meta_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meta tags'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter meta description', 'rows': 3}),
        }
        labels = {
            'title': 'Article Title',
            'slug': 'Slug',
            'short_description': 'Short Description',
            'full_content': 'Content',
            'featured_image': 'Featured Image',
            'featured_image_alt': 'Featured Image Alt Text',
            'date_published': 'Date Published',
            'meta_tags': 'Meta Tags',
            'meta_description': 'Meta Description',
            
        }
        help_texts = {
            'title': 'The headline or title of the news article',
            'slug': 'URL-friendly version of the article title',
            'short_description': 'A brief summary of the news article',
            'full_content': 'The body of the news article, which can include text, images, and videos',
            'featured_image': 'The image representing the news article, shown as a thumbnail or preview',
            'featured_image_alt': 'Alternative text for the featured image for accessibility and SEO',
            'date_published': 'The publication date of the news article',
            'meta_tags': 'SEO-friendly tags for better visibility',
            'meta_description': 'Short description for search engine snippets',
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Required fields for SEO team
        
        self.fields['slug'].required = True
        self.fields['short_description'].required = True
        self.fields['meta_description'].required = True
        
        
        
        # Add Bootstrap error styling if validation fails
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control is-invalid'})
    
##########################################################################


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title',
            'author',
            'short_description',
            'content',
            'tags',
            'featured_image',
            'featured_image_alt',
            'slug',
            'meta_tags',
            'meta_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the blog title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name', 'readonly': 'readonly'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter a short teaser', 'readonly': 'readonly'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter the full content', 'readonly': 'readonly'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'featured_image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Describe the image for accessibility'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL-friendly version of the title'}),
            'meta_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEO-friendly title'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short description for search engine snippets'}),
        }
        labels = {
            'title': 'Post Title',
            'author': 'Author',
            'short_description': 'Short Description',
            'content': 'Blog Content',
            'tags': 'Tags',
            'featured_image': 'Featured Image',
            'featured_image_alt': 'Image Alt Text',
            'slug': 'Slug',
            'meta_tags': 'Meta Tags',
            'meta_description': 'Meta Description',
        }
        help_texts = {
            'title': 'Provide a concise and catchy title for your blog post.',
            'author': 'Enter the name of the author of this blog post.',
            'short_description': 'Give readers a brief idea about the blog post.',
            'content': 'Write the full content of your blog post here.',
            'tags': 'Separate tags with commas to help with search and organization.',
            'featured_image': 'Upload an image to represent your post.',
            'featured_image_alt': 'Describe the image for accessibility and SEO purposes.',
            'slug': 'URL-friendly version of the title (will be auto-generated if left blank).',
            'meta_tags': 'SEO-friendly title if different from the post title.',
            'meta_description': 'Short description for search engine results (keep under 160 characters).',
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = True 


####################################################################################

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'short_description',
            'content',
            'featured_image',
            'featured_image_alt',
            'slug',
            'meta_tags',
            'meta_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the project title', 'readonly': 'readonly'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Provide a brief summary of the project', 'readonly': 'readonly'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Provide detailed information about the project', 'readonly': 'readonly'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured_image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternative text for the image'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL-friendly version of the title'}),
            'meta_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEO-friendly title'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short description for search engines'}),
        }
        labels = {
            'title': 'Project Title',
            'short_description': 'Short Description',
            'content': 'Project Content',
            'featured_image': 'Featured Image',
            'featured_image_alt': 'Image Alt Text',
            'slug': 'URL Slug',
            'meta_tags': 'Meta Tags',
            'meta_description': 'Meta Description',
        }
        help_texts = {
            'title': 'The title of the project.',
            'short_description': 'A brief summary of the project.',
            'content': 'Detailed information about the project, its objectives, scope, and significance.',
            'featured_image': 'An image that represents the project.',
            'featured_image_alt': 'Alternative text for the featured image.',
            'slug': 'URL-friendly version of the project title',
            'meta_tags': 'SEO-friendly title (if different from name)',
            'meta_description': 'Short description for search engine snippets',
        }













