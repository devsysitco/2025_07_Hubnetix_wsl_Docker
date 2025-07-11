from django.db import models

# Create your models here.

#################################################################################
#################################################################################


class OldUrlRedirect(models.Model):
    
    URL_TYPE_CHOICES = [
        ('category', 'Category'),
        ('product', 'Product'),
        ('news', 'News'),
        ('blog', 'Blog'),
        ('projects', 'Projects'),
    ]


    old_slug = models.CharField(max_length=255, unique=True, help_text="Old PHP URL slug without .php")
    new_slug = models.CharField(max_length=255, help_text="New URL slug for redirection")
    url_type = models.CharField(max_length=50, choices=URL_TYPE_CHOICES, help_text="Type of URL")

    def __str__(self):
        return f"{self.old_slug} → {self.new_slug} ({self.url_type})"
